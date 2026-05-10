"""Explainable weighted risk scoring for document automation."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from python_engine.validation_rules import has_failed_rule


def parse_date(value: str) -> date | None:
    """Parse an ISO date/datetime string into a date."""
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
    except ValueError:
        return None


def is_urgent_due_date(due_date: str, generated_on: date, urgent_due_days: int) -> bool:
    """Return whether the due date falls within the urgent processing window."""
    parsed_due_date = parse_date(due_date)
    if not parsed_due_date:
        return False
    days_until_due = (parsed_due_date - generated_on).days
    return 0 <= days_until_due <= urgent_due_days


def determine_risk_level(score: int) -> str:
    """Map a numeric risk score to a human-readable risk level."""
    if score >= 75:
        return "critical"
    if score >= 50:
        return "high"
    if score >= 25:
        return "medium"
    return "low"


def calculate_risk_score(
    document: dict[str, Any],
    validation_results: list[dict[str, str]],
    config: dict[str, Any],
    generated_on: date | None = None,
) -> dict[str, Any]:
    """Calculate weighted risk score, level, explanation, and top factors."""
    generated_on = generated_on or date.today()
    factors: list[dict[str, Any]] = []

    def add_factor(name: str, weight: int, detail: str) -> None:
        factors.append({"factor": name, "weight": weight, "detail": detail})

    confidence = float(document.get("extraction_confidence") or 0)
    minimum_confidence = float(config.get("minimum_confidence", 0.8))
    if confidence < minimum_confidence:
        add_factor("low_extraction_confidence", 14, f"Extraction confidence is {confidence:.2f}.")

    missing_count = len(document.get("missing_fields", []))
    if missing_count:
        add_factor("missing_required_fields", min(20, missing_count * 8), f"{missing_count} field(s) require completion.")

    if has_failed_rule(validation_results, "iban_format"):
        add_factor("invalid_iban", 16, "IBAN failed plausibility or checksum validation.")
    if has_failed_rule(validation_results, "vat_id_format"):
        add_factor("invalid_vat_id", 12, "VAT ID failed the expected format validation.")
    if bool(document.get("suspected_duplicate", False)):
        add_factor("duplicate_suspicion", 24, "Duplicate signal is active.")
    if bool(document.get("amount_mismatch", False)):
        add_factor("amount_mismatch", 18, "Amount mismatch requires reconciliation.")

    high_amount_threshold = float(config.get("high_amount_threshold", 10000))
    if float(document.get("amount") or 0) >= high_amount_threshold:
        add_factor("high_amount_threshold", 10, f"Amount is at or above {high_amount_threshold:.0f} EUR.")

    domestic_country = str(config.get("domestic_country", "DE")).upper()
    if str(document.get("vendor_country", "")).upper() != domestic_country:
        add_factor("foreign_vendor_country", 8, "Vendor is outside the domestic country profile.")

    if is_urgent_due_date(str(document.get("due_date", "")), generated_on, int(config.get("urgent_due_days", 5))):
        add_factor("urgent_due_date", 8, "Due date is within the urgent processing window.")

    if has_failed_rule(validation_results, "supported_currency"):
        add_factor("unsupported_currency", 10, "Currency prevents straight-through ERP export.")

    score = min(100, sum(factor["weight"] for factor in factors))
    level = determine_risk_level(score)
    top_factors = sorted(factors, key=lambda factor: factor["weight"], reverse=True)[:4]
    explanation = "Low operational risk; document can follow standard processing."
    if top_factors:
        explanation = "Risk driven by " + ", ".join(factor["factor"] for factor in top_factors) + "."

    return {
        "risk_score": score,
        "risk_level": level,
        "explanation": explanation,
        "top_risk_factors": top_factors,
    }
