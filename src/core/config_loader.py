from __future__ import annotations
import json
from pathlib import Path
from jsonschema import validate
from jsonschema.exceptions import ValidationError

def load_json(path: str | Path) -> dict:
    p = Path(path)
    return json.loads(p.read_text(encoding="utf-8"))

def load_and_validate_config(config_path: str | Path, schema_path: str | Path) -> dict:
    cfg = load_json(config_path)
    schema = load_json(schema_path)
    try:
        validate(instance=cfg, schema=schema)
    except ValidationError as e:
        raise ValueError(f"Invalid config JSON: {e.message}") from e
    return cfg
