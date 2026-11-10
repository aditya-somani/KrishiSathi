"""LiveKit worker entrypoint for KrishiSathi."""

from __future__ import annotations

import logging
import sys

from livekit.agents import WorkerOptions, cli

from krishisathi.agent import entrypoint
from krishisathi.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("krishisathi.main")


def prewarm_worker(_proc) -> None:
    """Validate runtime credentials before accepting incoming call jobs."""
    try:
        settings.validate()
        logger.info("KrishiSathi configuration validated")
    except ValueError as exc:
        logger.error("Configuration error: %s", exc)
        sys.exit(1)


def run() -> None:
    """Start the LiveKit worker CLI."""
    logger.info("Starting KrishiSathi LiveKit worker...")
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            prewarm_fnc=prewarm_worker,
        )
    )


if __name__ == "__main__":
    run()

