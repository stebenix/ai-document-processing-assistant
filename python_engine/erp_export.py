"""ERP export readiness payload generation."""

from __future__ import annotations

from typing import Any

EXPORT_ROUTE = "Auto export to ERP"
TARGET_SYSTEM = "SAP S/4HANA"


def build_erp_export_readiness(
    document: dict[str, Any],
    validation_results: list[dict[str, str]],
    routing: dict[str, str],
) -> dict[str, Any]:
    """Create an ERP export readiness object and payload preview."""
    failed_results = [result for result in validation_results if result["status"] == "failed"]
    blocking_reasons = [result["message"] for result in failed_results]

    if routing["route"] != EXPORT_ROUTE:
        blocking_reasons.append(f"Route is {routing['route']}, not auto export.")

    ready_for_export = not blocking_reasons
    payload_preview: dict[str, Any] = {}
    if ready_for_export:
        payload_preview = {
            "document_id": document["document_id"],
            "document_type": document["document_type"],
            "vendor_name": document["vendor_name"],
            "invoice_number": document.get("invoice_number"),
            "po_number": document.get("po_number"),
            "amount": document["amount"],
            "currency": document["currency"],
            "due_date": document.get("due_date"),
            "iban": document.get("iban"),
            "vat_id": document.get("vat_id"),
            "line_items_count": document.get("line_items_count"),
        }

    return {
        "ready_for_export": ready_for_export,
        "target_system": TARGET_SYSTEM,
        "blocking_reasons": blocking_reasons,
        "export_payload_preview": payload_preview,
    }
