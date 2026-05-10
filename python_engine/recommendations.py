"""AI-style recommendations generated from deterministic document signals."""

from __future__ import annotations

from collections import Counter
from typing import Any


def recommend_for_document(
    document: dict[str, Any],
    validation_results: list[dict[str, str]],
    risk: dict[str, Any],
    routing: dict[str, str],
) -> list[str]:
    """Generate concise next-step recommendations for a processed document."""
    failed_rules = {result["rule"] for result in validation_results if result["status"] == "failed"}
    recommendations: list[str] = []

    if "po_number_presence" in failed_rules:
        recommendations.append("Request missing PO number from supplier or procurement before ERP export.")
    if document.get("amount_mismatch"):
        recommendations.append("Send document to Finance review due to amount mismatch.")
    if document.get("suspected_duplicate"):
        recommendations.append("Block posting until the duplicate candidate is investigated.")
    if "iban_format" in failed_rules:
        recommendations.append("Verify supplier bank details before payment release.")
    if "vat_id_format" in failed_rules:
        recommendations.append("Validate supplier VAT ID and update master data if needed.")
    if routing["route"] == "Auto export to ERP":
        recommendations.append("Auto-export low-risk document and retain the audit trace.")
    elif int(risk["risk_score"]) >= 50:
        recommendations.append("Prioritize human review because the document has elevated operational risk.")

    if not recommendations:
        recommendations.append(f"Route to {routing['route']} and follow the suggested next action.")
    return recommendations


def recommend_for_batch(processed_documents: list[dict[str, Any]]) -> list[str]:
    """Generate summary-level recommendations for portfolio dashboard storytelling."""
    routes = Counter(document["routing"]["route"] for document in processed_documents)
    issue_counter: Counter[str] = Counter()
    for document in processed_documents:
        for result in document["validation_results"]:
            if result["status"] == "failed":
                issue_counter[result["rule"]] += 1

    recommendations = [
        "Use the generated JSON as static evidence for the dashboard while keeping GitHub Pages deployment simple.",
        f"Focus process improvement on {issue_counter.most_common(1)[0][0]} issues." if issue_counter else "Keep monitoring validation quality for straight-through processing.",
        f"Review staffing for {routes.get('Finance review', 0) + routes.get('Procurement review', 0) + routes.get('Compliance review', 0)} specialist-review documents.",
    ]
    return recommendations
