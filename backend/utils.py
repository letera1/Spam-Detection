"""
Utility functions and constants for the spam detection system.
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any

# =============================================================================
# Constants
# =============================================================================

# Label mappings
LABEL_MAP: Dict[str, int] = {"ham": 0, "spam": 1}
LABEL_INV_MAP: Dict[int, str] = {0: "ham", 1: "spam"}

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
MODELS_DIR = PROJECT_ROOT / "models"
DATA_DIR = PROJECT_ROOT / "data"

# Model artifacts
PIPELINE_FILENAME = "spam_pipeline.joblib"
VECTORIZER_FILENAME = "vectorizer.joblib"
MODEL_FILENAME = "model.joblib"

# Default hyperparameters
DEFAULT_MODEL_PARAMS: Dict[str, Dict[str, Any]] = {
    "naive_bayes": {
        "alpha": 1.0,
        "fit_prior": True,
    },
    "logistic_regression": {
        "C": 1.0,
        "max_iter": 1000,
        "solver": "lbfgs",
    },
}

# Hyperparameter search grids
HYPERPARAM_GRIDS: Dict[str, Dict[str, list]] = {
    "naive_bayes": {
        "alpha": [0.1, 0.5, 1.0, 1.5],
        "fit_prior": [True, False],
    },
    "logistic_regression": {
        "C": [0.1, 1.0, 10.0, 100.0],
        "max_iter": [500, 1000, 1500],
    },
}

# Vectorizer settings
VECTORIZER_CONFIG: Dict[str, Any] = {
    "count": {
        "max_features": 5000,
        "min_df": 2,
        "max_df": 0.95,
        "ngram_range": (1, 2),
    },
    "tfidf": {
        "max_features": 5000,
        "min_df": 2,
        "max_df": 0.95,
        "ngram_range": (1, 2),
        "sublinear_tf": True,
    },
}

# =============================================================================
# Logging Setup
# =============================================================================


def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Configure and return a logger with console and file handlers.

    Args:
        name: Logger name (typically __name__)
        level: Logging level (default: INFO)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if logger.handlers:
        return logger

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)

    # File handler (optional - logs to file if models dir exists)
    if MODELS_DIR.exists():
        log_file = MODELS_DIR / "training.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(console_format)
        logger.addHandler(file_handler)

    return logger


# =============================================================================
# Path Utilities
# =============================================================================


def ensure_dirs() -> None:
    """Create necessary directories if they don't exist."""
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def get_pipeline_path(model_name: str = "default") -> Path:
    """
    Get the full path for saving a pipeline.

    Args:
        model_name: Name identifier for the model

    Returns:
        Full path to the pipeline file
    """
    ensure_dirs()
    return MODELS_DIR / f"{model_name}_{PIPELINE_FILENAME}"


def get_model_path(model_name: str) -> Path:
    """
    Get the full path for a specific model artifact.

    Args:
        model_name: Name of the model/artifact

    Returns:
        Full path to the model file
    """
    ensure_dirs()
    return MODELS_DIR / model_name
