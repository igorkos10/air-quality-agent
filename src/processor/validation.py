from __future__ import annotations
from typing import Any, Dict, List

def validate_payload(payload: Dict[str, Any], require_fields: List[str]) -> None:
    if "current" not in payload or not isinstance(payload["current"], dict):
        raise ValueError("Payload missing 'current' object")

    current = payload["current"]
    for f in require_fields:
        if f not in current:
            raise ValueError(f"Missing required field in payload.current: {f}")

    values = current.get("values")
    if not isinstance(values, list) or not values:
        raise ValueError("payload.current.values is empty or invalid")
