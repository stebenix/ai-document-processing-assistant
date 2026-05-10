"""Simulated OCR and LLM-style field extraction."""

from __future__ import annotations

from typing import Any

LOW_CONFIDENCE_THRESHOLD = 0.82


def normalize_document(document: dict[str, Any]) -> dict[str, Any]:
    """Normalize raw intake values into a consistent extracted document shape."""
    normalized = dict(document)
    normalized["document_type"] = str(normalized.get("document_type", "")).strip().lower()
    normalized["source_channel"] = str(normalized.get("source_channel", "")).strip()
    normalized["vendor_name"] = str(normalized.get("vendor_name", "")).strip()
    normalized["vendor_country"] = str(normalized.get("vendor_country", "")).strip().upper()
    normalized["currency"] = str(normalized.get("currency", "")).strip().upper()
    normalized["iban"] = str(normalized.get("iban", "")).replace(" ", "").upper()
    normalized["vat_id"] = str(normalized.get("vat_id", "")).replace(" ", "").upper()
    normalized["po_number"] = str(normalized.get("po_number", "")).strip()
    normalized["amount"] = round(float(normalized.get("amount") or 0), 2)
    normalized["line_items_count"] = int(normalized.get("line_items_count") or 0)
    normalized["extraction_confidence"] = round(float(normalized.get("extraction_confidence") or 0), 2)
    normalized["missing_fields"] = list(normalized.get("missing_fields") or [])
    normalized["suspected_duplicate"] = bool(normalized.get("suspected_duplicate", False))
    normalized["amount_mismatch"] = bool(normalized.get("amount_mismatch", False))
    return normalized


def calculate_completeness(document: dict[str, Any], required_fields: list[str]) -> float:
    """Calculate the share of required fields that contain usable values."""
    if not required_fields:
        return 1.0

    present_count = 0
    for field in required_fields:
        value = document.get(field)
        if value not in (None, "", []):
            present_count += 1
    return round(present_count / len(required_fields), 2)


def detect_low_confidence_fields(document: dict[str, Any]) -> list[str]:
    """Return fields that would need attention after simulated OCR/LLM extraction."""
    fields: list[str] = []
    confidence = float(document.get("extraction_confidence") or 0)
    if confidence < LOW_CONFIDENCE_THRESHOLD:
        fields.extend(["invoice_number", "iban", "vat_id"])
    fields.extend(str(field) for field in document.get("missing_fields", []))
    return sorted(set(fields))


def extract_document(document: dict[str, Any], required_fields: list[str]) -> dict[str, Any]:
    """Simulate extraction, normalization, metadata enrichment, and completeness scoring."""
    normalized = normalize_document(document)
    confidence = normalized["extraction_confidence"]
    low_confidence_fields = detect_low_confidence_fields(normalized)
    completeness = calculate_completeness(normalized, required_fields)

    normalized["extraction"] = {
        "extraction_status": "completed" if confidence >= 0.65 else "needs_rescan",
        "confidence": confidence,
        "completeness": completeness,
        "missing_fields": normalized["missing_fields"],
        "low_confidence_fields": low_confidence_fields,
        "metadata": {
            "engine": "deterministic_ocr_llm_simulator",
            "model_profile": "portfolio-demo-v1",
            "normalized_fields": [
                "document_type",
                "vendor_country",
                "currency",
                "iban",
                "vat_id",
                "amount",
            ],
        },
    }
    return normalized


def extract_documents(documents: list[dict[str, Any]], required_fields: list[str]) -> list[dict[str, Any]]:
    """Extract and normalize a batch of raw intake documents."""
    return [extract_document(document, required_fields) for document in documents]
