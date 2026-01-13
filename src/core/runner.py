from __future__ import annotations
import time
from typing import Any, Dict, List, Optional
from .logger import setup_logger
from ..collector.airly_client import AirlyClient
from ..processor.validation import validate_payload
from ..processor.transforms import transform_payload
from ..storage.mariadb import MariaDBStorage

logger = setup_logger()

class PipelineContext:
    def __init__(self) -> None:
        self.raw: Optional[Dict[str, Any]] = None
        self.rows: List[Dict[str, Any]] = []

def run_once(cfg: Dict[str, Any]) -> int:
    ctx = PipelineContext()

    source = cfg["source"]
    processing = cfg["processing"]
    storage_cfg = cfg["storage"]
    steps = cfg["steps"]

    client = AirlyClient(
        base_url=source["base_url"],
        api_key_env="AIRLY_API_KEY",
        timeout_seconds=source.get("timeout_seconds", 10),
        retries=source.get("retries", 0),
    )
    storage = MariaDBStorage.from_env(table=storage_cfg["table"], mode=storage_cfg["mode"])

    for step in steps:
        action = step["action"]

        if action == "fetch_current":
            logger.info("Step: fetch_current")
            ctx.raw = client.fetch_current(installation_id=source["installation_id"])
            logger.info("Fetched payload keys: %s", list(ctx.raw.keys()) if isinstance(ctx.raw, dict) else type(ctx.raw))

        elif action == "validate":
            logger.info("Step: validate")
            if ctx.raw is None:
                raise RuntimeError("No raw payload to validate. Did fetch_current run?")
            validate_payload(ctx.raw, require_fields=processing.get("require_fields", []))
            logger.info("Validation OK")

        elif action == "transform":
            logger.info("Step: transform")
            if ctx.raw is None:
                raise RuntimeError("No raw payload to transform. Did fetch_current run?")
            ctx.rows = transform_payload(
                ctx.raw,
                installation_id=source["installation_id"],
                allowed_params=set(processing.get("allowed_params", [])),
                value_decimals=int(processing.get("rounding", {}).get("value_decimals", 2)),
                timestamp_field=processing.get("timestamp_field", "tillDateTime"),
            )
            logger.info("Transformed to %d rows", len(ctx.rows))

        elif action == "save":
            logger.info("Step: save")
            if not ctx.rows:
                logger.warning("No rows to save (empty transform output).")
                continue
            inserted = storage.save_measurements(ctx.rows)
            logger.info("Saved rows: %d", inserted)

        else:
            raise ValueError(f"Unknown action: {action}")

    return len(ctx.rows)

def run_loop(cfg: Dict[str, Any]) -> None:
    interval = int(cfg["agent"]["interval_seconds"])
    while True:
        t0 = time.time()
        try:
            rows = run_once(cfg)
            logger.info("Run finished. Rows=%d. Took %.2fs", rows, time.time() - t0)
        except Exception as e:
            logger.exception("Run failed: %s", e)
        time.sleep(max(1, interval))
