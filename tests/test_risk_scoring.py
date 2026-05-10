from datetime import date

from python_engine.risk_scoring import calculate_risk_score, determine_risk_level


CONFIG = {
    "minimum_confidence": 0.8,
    "high_amount_threshold": 10000,
    "urgent_due_days": 5,
    "domestic_country": "DE",
}


def test_risk_scoring_levels_for_clean_document():
    document = {
        "extraction_confidence": 0.96,
        "missing_fields": [],
        "suspected_duplicate": False,
        "amount_mismatch": False,
        "amount": 2400,
        "vendor_country": "DE",
        "due_date": "2026-05-30",
    }

    risk = calculate_risk_score(document, [], CONFIG, date(2026, 5, 10))

    assert risk["risk_score"] == 0
    assert risk["risk_level"] == "low"


def test_risk_scoring_levels_for_high_risk_document():
    document = {
        "extraction_confidence": 0.64,
        "missing_fields": ["po_number", "vat_id"],
        "suspected_duplicate": True,
        "amount_mismatch": True,
        "amount": 25000,
        "vendor_country": "FR",
        "due_date": "2026-05-12",
    }
    validation_results = [
        {"rule": "iban_format", "status": "failed"},
        {"rule": "vat_id_format", "status": "failed"},
        {"rule": "supported_currency", "status": "passed"},
    ]

    risk = calculate_risk_score(document, validation_results, CONFIG, date(2026, 5, 10))

    assert risk["risk_score"] >= 75
    assert risk["risk_level"] == "critical"
    assert risk["top_risk_factors"][0]["factor"] == "duplicate_suspicion"


def test_determine_risk_level_boundaries():
    assert determine_risk_level(24) == "low"
    assert determine_risk_level(25) == "medium"
    assert determine_risk_level(50) == "high"
    assert determine_risk_level(75) == "critical"
