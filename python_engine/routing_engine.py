"""Routing decisions for finance, procurement, compliance, and ERP export."""

from __future__ import annotations

from typing import Any


def route_document(document: dict[str, Any], validation_results: list[dict[str, str]], risk: dict[str, Any]) -> dict[str, str]:
    """Route a document based on risk score, document state, and validation outcomes."""
    failed_rules = {result["rule"] for result in validation_results if result["status"] == "failed"}
    risk_score = int(risk["risk_score"])

    if "duplicate_check" in failed_rules or risk_score >= 85:
        return {
            "route": "Blocked",
            "routing_reason": "Critical duplicate or extreme risk prevents ERP export.",
            "next_best_action": "Block posting, keep audit evidence, and request human investigation.",
        }

    if "iban_format" in failed_rules or "vat_id_format" in failed_rules or str(document.get("vendor_country")) != "DE":
        return {
            "route": "Compliance review",
            "routing_reason": "Supplier master data or cross-border compliance needs review.",
            "next_best_action": "Verify supplier identity, tax data, and bank details before release.",
        }

    if "po_number_presence" in failed_rules:
        return {
            "route": "Procurement review",
            "routing_reason": "Purchase order reference is missing for a PO-controlled document.",
            "next_best_action": "Request or match the PO number before financial posting.",
        }

    if "amount_match" in failed_rules or risk_score >= 50:
        return {
            "route": "Finance review",
            "routing_reason": "Financial reconciliation is required before export.",
            "next_best_action": "Compare amount, line items, and approval limits with source documents.",
        }

    if risk_score >= 25:
        return {
            "route": "Human approval required",
            "routing_reason": "Medium-risk document should receive lightweight approval.",
            "next_best_action": "Ask an AP specialist to approve or add missing context.",
        }

    return {
        "route": "Auto export to ERP",
        "routing_reason": "Low-risk document passed validation checks.",
        "next_best_action": "Export to ERP and retain audit trail.",
    }
