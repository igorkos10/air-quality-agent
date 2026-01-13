import pytest
from src.collector.airly_client import AirlyClient

class DummyResp:
    def __init__(self, status_code=200, data=None, text=""):
        self.status_code = status_code
        self._data = data or {}
        self.text = text
    def json(self):
        return self._data

def test_missing_api_key(monkeypatch):
    monkeypatch.delenv("AIRLY_API_KEY", raising=False)
    c = AirlyClient(base_url="https://airapi.airly.eu/v2")
    with pytest.raises(RuntimeError):
        c.fetch_current(installation_id=1)

def test_fetch_current_calls_requests(monkeypatch):
    monkeypatch.setenv("AIRLY_API_KEY", "x")
    called = {}
    def fake_get(url, headers=None, params=None, timeout=None):
        called["url"] = url
        called["params"] = params
        return DummyResp(200, {"current":{"fromDateTime":"2025-01-01T10:00:00Z","tillDateTime":"2025-01-01T11:00:00Z","values":[{"name":"PM10","value":1}]}})
    monkeypatch.setattr("requests.get", fake_get)
    c = AirlyClient(base_url="https://airapi.airly.eu/v2")
    data = c.fetch_current(installation_id=123)
    assert called["url"].endswith("/measurements/installation")
    assert called["params"]["installationId"] == 123
    assert "current" in data
