from python_engine.validation_rules import is_valid_german_vat_id, is_valid_iban, validate_document


def test_valid_and_invalid_iban_checks():
    assert is_valid_iban("DE89 3704 0044 0532 0130 00")
    assert is_valid_iban("FR76 3000 6000 0112 3456 7890 189")
    assert not is_valid_iban("DE12 3456 7890 1234 5678 90")
    assert not is_valid_iban("NOT-AN-IBAN")


def test_valid_and_invalid_german_vat_checks():
    assert is_valid_german_vat_id("DE123456789")
    assert is_valid_german_vat_id("de987654321")
    assert not is_valid_german_vat_id("DE12345")
    assert not is_valid_german_vat_id("FR40303265045")


def test_validate_document_flags_po_and_currency_issues():
    document = {
        "document_id": "DOC-TEST",
        "document_type": "invoice",
        "vendor_name": "Test GmbH",
        "vendor_country": "DE",
        "amount": 100,
        "currency": "USD",
        "received_at": "2026-05-10T00:00:00Z",
        "iban": "DE89370400440532013000",
        "vat_id": "DE123456789",
        "po_number": "",
        "missing_fields": ["po_number"],
        "amount_mismatch": False,
        "suspected_duplicate": False,
    }
    config = {
        "required_fields": ["document_id", "document_type", "vendor_name", "vendor_country", "amount", "currency", "received_at"],
        "po_required_document_types": ["invoice"],
        "supported_currencies": ["EUR"],
    }

    results = validate_document(document, config)
    failed_rules = {result["rule"] for result in results if result["status"] == "failed"}

    assert "po_number_presence" in failed_rules
    assert "supported_currency" in failed_rules
