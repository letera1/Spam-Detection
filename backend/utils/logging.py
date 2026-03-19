"""
Logging utilities for the spam detection system.

Provides centralized logging configuration.
"""

import logging
import sys
from pathlib import Path
from typing import Optional

from ..config.settings import MODELS_DIR


def get_logger(
    name: str,
    level: int = logging.INFO,
    log_to_file: bool = True,
) -> logging.Logger:
    """
    Configure and return a logger.

    Args:
        name: Logger name (typically __name__)
        level: Logging level
        log_to_file: Whether to log to file

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if logger.handlers:
        return logger

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)

    # File handler (optional)
    if log_to_file and MODELS_DIR.exists():
        log_file = MODELS_DIR / "spam_detection.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(console_format)
        logger.addHandler(file_handler)

    return logger


def set_log_level(level: int):
    """Set log level for all spam detection loggers."""
    for name in logging.root.manager.loggerDict:
        if "backend" in name or "spam" in name:
            logging.getLogger(name).setLevel(level)


def get_log_file_path() -> Optional[Path]:
    """Get the path to the log file."""
    if MODELS_DIR.exists():
        return MODELS_DIR / "spam_detection.log"
    return None
