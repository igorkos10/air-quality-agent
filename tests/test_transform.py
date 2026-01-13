from src.processor.transforms import transform_payload

def test_transform_filters_and_rounds():
    payload = {
        "current": {
            "fromDateTime": "2025-01-01T10:00:00Z",
            "tillDateTime": "2025-01-01T11:00:00Z",
            "values": [
                {"name": "PM2.5", "value": 12.3456},
                {"name": "PM10", "value": 45.6789},
                {"name": "NO2", "value": 99.9},
            ],
        }
    }

    rows = transform_payload(
        payload,
        installation_id=123,
        allowed_params={"PM2.5", "PM10"},
        value_decimals=2,
        timestamp_field="tillDateTime",
    )
    assert len(rows) == 2
    assert rows[0]["installation_id"] == 123
    assert rows[0]["param"] == "PM2.5"
    assert rows[0]["value"] == 12.35
