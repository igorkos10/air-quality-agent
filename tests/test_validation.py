import pytest
from src.processor.validation import validate_payload

def test_validate_ok():
    payload = {"current": {"fromDateTime":"2025-01-01T10:00:00Z","tillDateTime":"2025-01-01T11:00:00Z","values":[{"name":"PM10","value":1}]}}
    validate_payload(payload, require_fields=["fromDateTime","tillDateTime","values"])

def test_validate_missing_current():
    with pytest.raises(ValueError):
        validate_payload({}, require_fields=["fromDateTime"])

def test_validate_missing_field():
    payload = {"current": {"tillDateTime":"2025-01-01T11:00:00Z","values":[{"name":"PM10","value":1}]}}
    with pytest.raises(ValueError):
        validate_payload(payload, require_fields=["fromDateTime"])
