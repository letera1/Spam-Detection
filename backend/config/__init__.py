"""
Configuration package for spam detection.

Provides centralized configuration management for:
- Model hyperparameters
- Vectorizer settings
- Preprocessor options
- Training parameters
- Path configurations
"""

from .settings import (
    Settings,
    ModelConfig,
    VectorizerConfig,
    PreprocessorConfig,
    TrainingConfig,
    DEFAULT_SETTINGS,
    PROJECT_ROOT,
    MODELS_DIR,
    DATA_DIR,
    LABEL_MAP,
    LABEL_INV_MAP,
)

from .hyperparameters import (
    HYPERPARAM_GRIDS,
    DEFAULT_PARAMS,
    VECTORIZER_PRESETS,
    MODEL_PRESETS,
    TRAINING_PRESETS,
    get_preset_config,
)

__all__ = [
    # Settings
    "Settings",
    "ModelConfig",
    "VectorizerConfig",
    "PreprocessorConfig",
    "TrainingConfig",
    "DEFAULT_SETTINGS",
    # Paths
    "PROJECT_ROOT",
    "MODELS_DIR",
    "DATA_DIR",
    # Labels
    "LABEL_MAP",
    "LABEL_INV_MAP",
    # Hyperparameters
    "HYPERPARAM_GRIDS",
    "DEFAULT_PARAMS",
    "VECTORIZER_PRESETS",
    "MODEL_PRESETS",
    "TRAINING_PRESETS",
    "get_preset_config",
]
