"""Audit trail generation for every pipeline stage."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any


def build_audit_trail(
    document: dict[str, Any],
    validation_results: list[dict[str, str]],
    risk: dict[str, Any],
    routing: dict[str, str],
    recommendations: list[str],
    export_readiness: dict[str, Any],
) -> list[dict[str, str]]:
    """Create a deterministic audit timeline for a processed document."""
    received = datetime.fromisoformat(str(document["received_at"]).replace("Z", "+00:00"))

    events = [
        (0, "system", "document_received", f"Received via {document['source_channel']} from {document['vendor_name']}.",),
        (2, "ai_engine", "extraction_completed", f"Extraction completed with confidence {document['extraction']['confidence']:.2f}.",),
        (3, "validation_engine", "validation_checks_executed", f"Executed {len(validation_results)} validation checks.",),
        (4, "validation_engine", "risk_score_calculated", f"Risk score {risk['risk_score']} ({risk['risk_level']}).",),
        (5, "system", "route_assigned", f"Assigned route: {routing['route']}.",),
        (6, "ai_engine", "recommendation_generated", recommendations[0],),
        (7, "system", "erp_export_prepared_or_blocked", "ERP export prepared." if export_readiness["ready_for_export"] else "ERP export blocked with documented reasons.",),
    ]

    return [
        {
            "timestamp": (received + timedelta(minutes=minutes)).astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
            "actor": actor,
            "action": action,
            "detail": detail,
        }
        for minutes, actor, action, detail in events
    ]
