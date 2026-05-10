"""Document intake helpers for loading simulated business documents."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DEFAULT_DOCUMENTS_PATH = Path("data/sample_documents.json")
DEFAULT_RULES_PATH = Path("data/validation_rules.json")


def load_sample_documents(path: Path | str = DEFAULT_DOCUMENTS_PATH) -> list[dict[str, Any]]:
    """Load sample documents from JSON and return them in their intake order."""
    document_path = Path(path)
    with document_path.open("r", encoding="utf-8") as file:
        documents = json.load(file)

    if not isinstance(documents, list):
        raise ValueError("Sample document file must contain a JSON array.")
    return documents


def load_validation_config(path: Path | str = DEFAULT_RULES_PATH) -> dict[str, Any]:
    """Load configurable validation and risk thresholds."""
    rules_path = Path(path)
    with rules_path.open("r", encoding="utf-8") as file:
        config = json.load(file)

    if not isinstance(config, dict):
        raise ValueError("Validation rules file must contain a JSON object.")
    return config
