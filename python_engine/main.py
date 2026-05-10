"""CLI entry point for the Python automation engine."""

from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from python_engine.audit_trail import build_audit_trail
from python_engine.document_intake import load_sample_documents, load_validation_config
from python_engine.erp_export import build_erp_export_readiness
from python_engine.extraction_engine import extract_documents
from python_engine.recommendations import recommend_for_batch, recommend_for_document
from python_engine.risk_scoring import calculate_risk_score
from python_engine.routing_engine import route_document
from python_engine.validation_rules import validate_document

DEFAULT_OUTPUT_PATH = Path("outputs/demo_results.json")


def process_documents(
    documents: list[dict[str, Any]],
    config: dict[str, Any],
    generated_at: datetime | None = None,
) -> dict[str, Any]:
    """Run the complete automation pipeline and return JSON-serializable results."""
    generated_at = generated_at or datetime.now(timezone.utc)
    generated_on = generated_at.date()
    extracted_documents = extract_documents(documents, list(config.get("required_fields", [])))
    processed_documents: list[dict[str, Any]] = []

    for document in extracted_documents:
        validation_results = validate_document(document, config)
        risk = calculate_risk_score(document, validation_results, config, generated_on)
        routing = route_document(document, validation_results, risk)
        erp_export = build_erp_export_readiness(document, validation_results, routing)
        recommendations = recommend_for_document(document, validation_results, risk, routing)
        audit_trail = build_audit_trail(document, validation_results, risk, routing, recommendations, erp_export)

        processed_documents.append({
            "document_id": document["document_id"],
            "document_type": document["document_type"],
            "source_channel": document["source_channel"],
            "vendor_name": document["vendor_name"],
            "vendor_country": document["vendor_country"],
            "invoice_number": document.get("invoice_number"),
            "iban": document.get("iban"),
            "vat_id": document.get("vat_id"),
            "po_number": document.get("po_number"),
            "amount": document["amount"],
            "currency": document["currency"],
            "due_date": document.get("due_date"),
            "received_at": document["received_at"],
            "line_items_count": document["line_items_count"],
            "extraction": document["extraction"],
            "validation_results": validation_results,
            "risk": risk,
            "routing": routing,
            "erp_export_readiness": erp_export,
            "recommendations": recommendations,
            "audit_trail": audit_trail,
        })

    return {
        "generated_at": generated_at.isoformat().replace("+00:00", "Z"),
        "batch_summary": build_batch_summary(processed_documents),
        "batch_recommendations": recommend_for_batch(processed_documents),
        "documents": processed_documents,
    }


def build_batch_summary(processed_documents: list[dict[str, Any]]) -> dict[str, Any]:
    """Build dashboard-level analytics for the processed document batch."""
    total_documents = len(processed_documents)
    routes = Counter(document["routing"]["route"] for document in processed_documents)
    issue_counter: Counter[str] = Counter()
    for document in processed_documents:
        for result in document["validation_results"]:
            if result["status"] == "failed":
                issue_counter[result["rule"]] += 1

    average_confidence = round(
        sum(document["extraction"]["confidence"] for document in processed_documents) / total_documents,
        2,
    ) if total_documents else 0
    average_risk_score = round(
        sum(document["risk"]["risk_score"] for document in processed_documents) / total_documents,
        1,
    ) if total_documents else 0

    return {
        "total_documents": total_documents,
        "auto_export_count": routes.get("Auto export to ERP", 0),
        "auto_export_rate": round(routes.get("Auto export to ERP", 0) / total_documents, 2) if total_documents else 0,
        "human_review_count": sum(count for route, count in routes.items() if route not in {"Auto export to ERP", "Blocked"}),
        "blocked_count": routes.get("Blocked", 0),
        "average_confidence": average_confidence,
        "average_risk_score": average_risk_score,
        "route_distribution": dict(routes),
        "top_validation_issues": [
            {"rule": rule, "count": count} for rule, count in issue_counter.most_common(5)
        ],
    }


def write_results(results: dict[str, Any], output_path: Path = DEFAULT_OUTPUT_PATH) -> None:
    """Write formatted JSON output for the static case study."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as file:
        json.dump(results, file, indent=2, ensure_ascii=False)
        file.write("\n")


def main() -> None:
    """Run the CLI pipeline and print a short terminal summary."""
    documents = load_sample_documents()
    config = load_validation_config()
    results = process_documents(documents, config)
    write_results(results, DEFAULT_OUTPUT_PATH)

    summary = results["batch_summary"]
    print(f"Processed {summary['total_documents']} documents")
    print(f"Auto export: {summary['auto_export_count']}")
    print(f"Human review: {summary['human_review_count']}")
    print(f"Blocked: {summary['blocked_count']}")
    print(f"Average risk score: {summary['average_risk_score']}")
    print(f"Output written to {DEFAULT_OUTPUT_PATH}")


if __name__ == "__main__":
    main()
