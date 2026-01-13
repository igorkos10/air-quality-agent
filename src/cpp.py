from __future__ import annotations
import argparse
from dotenv import load_dotenv
from .core.config_loader import load_and_validate_config
from .core.runner import run_once, run_loop
from .core.logger import setup_logger

logger = setup_logger()

def main() -> None:
    parser = argparse.ArgumentParser(description="Air Quality Agent (Airly -> MariaDB), JSON-driven pipeline")
    parser.add_argument("--config", required=True, help="Path to pipeline config JSON")
    parser.add_argument("--schema", default="config/schema.pipeline.json", help="Path to pipeline JSON schema")
    parser.add_argument("--once", action="store_true", help="Run once and exit (override config.agent.loop)")
    args = parser.parse_args()

    load_dotenv(override=False)

    cfg = load_and_validate_config(args.config, args.schema)

    if args.once or not cfg["agent"]["loop"]:
        logger.info("Running once...")
        rows = run_once(cfg)
        logger.info("Done. Rows=%d", rows)
    else:
        logger.info("Running in loop. Interval=%ss", cfg["agent"]["interval_seconds"])
        run_loop(cfg)

if __name__ == "__main__":
    main()
