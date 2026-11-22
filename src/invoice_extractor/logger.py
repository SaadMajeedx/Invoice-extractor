"""Lightweight structured logging — token counts and response times."""

from __future__ import annotations

import logging
import sys


def setup_logger() -> logging.Logger:
    """Return the application logger, configuring it on first call."""
    logger = logging.getLogger("invoice_extractor")
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s | %(levelname)-7s | %(message)s",
                datefmt="%H:%M:%S",
            )
        )
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


def log_extraction(
    logger: logging.Logger,
    model: str,
    token_count: int,
    response_time: float,
) -> None:
    """Log the telemetry for a single extraction run."""
    logger.info("Model: %s", model)
    logger.info("Tokens used: %s", f"{token_count:,}")
    logger.info("Response time: %.3fs", response_time)
