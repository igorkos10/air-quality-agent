from __future__ import annotations
import os
import time
import requests
from typing import Any, Dict
from ..core.logger import setup_logger

logger = setup_logger()

class AirlyClient:
    def __init__(self, base_url: str, api_key_env: str = "AIRLY_API_KEY", timeout_seconds: int = 10, retries: int = 0):
        self.base_url = base_url.rstrip("/")
        self.api_key_env = api_key_env
        self.timeout_seconds = timeout_seconds
        self.retries = retries

    def _headers(self) -> Dict[str, str]:
        api_key = os.getenv(self.api_key_env)
        if not api_key:
            raise RuntimeError(f"Missing API key in env var {self.api_key_env}")
        return {"Accept": "application/json", "apikey": api_key}

    def fetch_current(self, installation_id: int) -> Dict[str, Any]:
        url = f"{self.base_url}/measurements/installation"
        params = {"installationId": installation_id}

        last_err: Exception | None = None
        for attempt in range(self.retries + 1):
            try:
                resp = requests.get(url, headers=self._headers(), params=params, timeout=self.timeout_seconds)
                if resp.status_code >= 400:
                    raise RuntimeError(f"Airly HTTP {resp.status_code}: {resp.text[:200]}")
                return resp.json()
            except Exception as e:
                last_err = e
                wait = 2 ** attempt
                logger.warning("Airly fetch failed (attempt %d/%d): %s. Waiting %ds", attempt + 1, self.retries + 1, e, wait)
                time.sleep(wait)

        raise RuntimeError(f"Airly fetch failed after retries: {last_err}") from last_err
