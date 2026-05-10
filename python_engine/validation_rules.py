"""Deterministic validation checks for ERP-ready document processing."""

from __future__ import annotations

import re
from typing import Any

IBAN_PATTERN = re.compile(r"^[A-Z]{2}\d{2}[A-Z0-9]{11,30}$")
GERMAN_VAT_PATTERN = re.compile(r"^DE\d{9}$")


def is_valid_iban(iban: str) -> bool:
    """Return whether an IBAN is plausible using format and checksum validation."""
    compact = iban.replace(" ", "").upper()
    if not IBAN_PATTERN.match(compact):
        return False

    rearranged = compact[4:] + compact[:4]
    numeric = ""
    for character in rearranged:
        if character.isdigit():
            numeric += character
        elif character.isalpha():
            numeric += str(ord(character) - 55)
        else:
            return False
    return int(numeric) % 97 == 1


def is_valid_german_vat_id(vat_id: str) -> bool:
    """Return whether a VAT ID looks like a German VAT identifier."""
    return bool(GERMAN_VAT_PATTERN.match(vat_id.replace(" ", "").upper()))


def validation_result(rule: str, status: str, severity: str, message: str) -> dict[str, str]:
    """Build a consistently shaped validation result."""
    return {
        "rule": rule,
        "status": status,
        "severity": severity,
        "message": message,
    }


def validate_document(document: dict[str, Any], config: dict[str, Any]) -> list[dict[str, str]]:
    """Run all configured validation checks for a single document."""
    results: list[dict[str, str]] = []
    required_fields = list(config.get("required_fields", []))
    supported_currencies = set(config.get("supported_currencies", ["EUR"]))
    po_required_types = set(config.get("po_required_document_types", []))

    missing_required = [field for field in required_fields if document.get(field) in (None, "", [])]
    missing_required.extend(field for field in document.get("missing_fields", []) if field not in missing_required)
    if missing_required:
        results.append(validation_result(
            "required_fields_completeness",
            "failed",
            "high",
            f"Missing required fields: {', '.join(sorted(missing_required))}.",
        ))
    else:
        results.append(validation_result("required_fields_completeness", "passed", "low", "Required fields are complete."))

    if is_valid_iban(str(document.get("iban", ""))):
        results.append(validation_result("iban_format", "passed", "low", "IBAN format looks valid."))
    else:
        results.append(validation_result("iban_format", "failed", "high", "IBAN is missing or failed format/checksum validation."))

    vendor_country = str(document.get("vendor_country", "")).upper()
    vat_id = str(document.get("vat_id", ""))
    if vendor_country == "DE":
        if is_valid_german_vat_id(vat_id):
            results.append(validation_result("vat_id_format", "passed", "low", "German VAT ID format looks valid."))
        else:
            results.append(validation_result("vat_id_format", "failed", "high", "German vendor VAT ID must match DE plus 9 digits."))
    elif vat_id:
        results.append(validation_result("vat_id_format", "passed", "medium", "Foreign VAT ID captured for manual plausibility review."))
    else:
        results.append(validation_result("vat_id_format", "warning", "medium", "Foreign vendor VAT ID is missing."))

    if document.get("document_type") in po_required_types and not document.get("po_number"):
        results.append(validation_result("po_number_presence", "failed", "high", "PO number is required before ERP export."))
    else:
        results.append(validation_result("po_number_presence", "passed", "low", "PO number requirement is satisfied."))

    if bool(document.get("amount_mismatch", False)):
        results.append(validation_result("amount_match", "failed", "high", "Amount mismatch against purchase order or delivery note."))
    else:
        results.append(validation_result("amount_match", "passed", "low", "No amount mismatch flagged."))

    if bool(document.get("suspected_duplicate", False)):
        results.append(validation_result("duplicate_check", "failed", "critical", "Potential duplicate document detected."))
    else:
        results.append(validation_result("duplicate_check", "passed", "low", "No duplicate signal detected."))

    if document.get("currency") in supported_currencies:
        results.append(validation_result("supported_currency", "passed", "low", "Currency is supported for this demo ERP flow."))
    else:
        results.append(validation_result("supported_currency", "failed", "medium", "Currency is not supported for automated ERP export."))

    return results


def has_failed_rule(results: list[dict[str, str]], rule: str) -> bool:
    """Return whether a named rule failed."""
    return any(result["rule"] == rule and result["status"] == "failed" for result in results)
