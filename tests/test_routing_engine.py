from python_engine.routing_engine import route_document


def test_low_risk_document_routes_to_auto_export():
    routing = route_document(
        {"vendor_country": "DE"},
        [
            {"rule": "iban_format", "status": "passed"},
            {"rule": "vat_id_format", "status": "passed"},
            {"rule": "duplicate_check", "status": "passed"},
        ],
        {"risk_score": 5, "risk_level": "low"},
    )

    assert routing["route"] == "Auto export to ERP"
    assert "Export" in routing["next_best_action"]


def test_high_duplicate_risk_document_routes_to_blocked():
    routing = route_document(
        {"vendor_country": "DE"},
        [{"rule": "duplicate_check", "status": "failed"}],
        {"risk_score": 88, "risk_level": "critical"},
    )

    assert routing["route"] == "Blocked"


def test_missing_po_routes_to_procurement_review():
    routing = route_document(
        {"vendor_country": "DE"},
        [{"rule": "po_number_presence", "status": "failed"}],
        {"risk_score": 34, "risk_level": "medium"},
    )

    assert routing["route"] == "Procurement review"
