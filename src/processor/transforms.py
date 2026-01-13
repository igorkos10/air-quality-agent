from __future__ import annotations
from typing import Any, Dict, List, Set
from datetime import datetime

def _parse_dt(s: str) -> datetime:
    s = s.replace("Z", "+00:00")
    return datetime.fromisoformat(s)

def transform_payload(
    payload: Dict[str, Any],
    installation_id: int,
    allowed_params: Set[str],
    value_decimals: int = 2,
    timestamp_field: str = "tillDateTime",
) -> List[Dict[str, Any]]:
    current = payload["current"]
    from_dt = _parse_dt(current["fromDateTime"])
    till_dt = _parse_dt(current["tillDateTime"])

    measured_at = _parse_dt(current[timestamp_field])
    rows: List[Dict[str, Any]] = []

    for item in current.get("values", []):
        name = item.get("name")
        value = item.get("value")

        if not name:
            continue
        if allowed_params and name not in allowed_params:
            continue

        if value is not None:
            try:
                value = round(float(value), value_decimals)
            except Exception:
                value = None

        rows.append({
            "installation_id": installation_id,
            "measured_at": measured_at,
            "param": str(name),
            "value": value,
            "source": "airly",
            "from_datetime": from_dt,
            "till_datetime": till_dt,
        })

    return rows
