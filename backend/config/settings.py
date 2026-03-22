"""
Application settings and configuration management.

Centralized configuration for paths, model parameters, and runtime settings.
"""

from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field


# =============================================================================
# Path Configuration
# =============================================================================

PROJECT_ROOT = Path(__file__).parent.parent.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
MODELS_DIR = PROJECT_ROOT / "models"
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
DATA_DIR = RAW_DATA_DIR # Default fallback for data loaders
LOGS_DIR = PROJECT_ROOT / "logs"

# Ensure directories exist
MODELS_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)


# =============================================================================
# Data Classes for Configuration
# =============================================================================


@dataclass
class PreprocessorConfig:
    """Configuration for text preprocessing."""

    remove_stopwords: bool = True
    use_stemming: bool = False
    use_lemmatization: bool = False
    min_length: int = 2
    lowercase: bool = True
    remove_urls: bool = True
    remove_emails: bool = True
    remove_phones: bool = True


@dataclass
class VectorizerConfig:
    """Configuration for feature extraction."""

    type: str = "tfidf"  # 'tfidf' or 'count'
    max_features: int = 5000
    min_df: int = 2
    max_df: float = 0.95
    ngram_range: tuple = (1, 2)
    sublinear_tf: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for sklearn."""
        return {
            "max_features": self.max_features,
            "min_df": self.min_df,
            "max_df": self.max_df,
            "ngram_range": self.ngram_range,
            "sublinear_tf": self.sublinear_tf,
        }


@dataclass
class ModelConfig:
    """Configuration for classifier models."""

    type: str = "logistic_regression"  # 'naive_bayes' or 'logistic_regression'
    alpha: float = 1.0  # For Naive Bayes
    C: float = 1.0  # For Logistic Regression
    max_iter: int = 1000
    solver: str = "lbfgs"
    random_state: int = 42

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for sklearn."""
        if self.type == "naive_bayes":
            return {"alpha": self.alpha, "fit_prior": True}
        else:
            return {
                "C": self.C,
                "max_iter": self.max_iter,
                "solver": self.solver,
                "random_state": self.random_state,
            }


@dataclass
class TrainingConfig:
    """Configuration for training runs."""

    test_size: float = 0.2
    random_state: int = 42
    stratify: bool = True
    use_grid_search: bool = True
    cv_folds: int = 5
    n_jobs: int = -1


class Settings:
    """
    Centralized settings manager.

    Provides access to all configuration through a single interface.

    Example:
        settings = Settings()
        preprocessor_cfg = settings.preprocessor
        vectorizer_cfg = settings.vectorizer
    """

    def __init__(
        self,
        preprocessor: Optional[PreprocessorConfig] = None,
        vectorizer: Optional[VectorizerConfig] = None,
        model: Optional[ModelConfig] = None,
        training: Optional[TrainingConfig] = None,
    ):
        """
        Initialize settings with optional custom configurations.

        Args:
            preprocessor: Custom preprocessor config (uses default if None)
            vectorizer: Custom vectorizer config (uses default if None)
            model: Custom model config (uses default if None)
            training: Custom training config (uses default if None)
        """
        self._preprocessor = preprocessor or PreprocessorConfig()
        self._vectorizer = vectorizer or VectorizerConfig()
        self._model = model or ModelConfig()
        self._training = training or TrainingConfig()

    @property
    def preprocessor(self) -> PreprocessorConfig:
        """Get preprocessor configuration."""
        return self._preprocessor

    @property
    def vectorizer(self) -> VectorizerConfig:
        """Get vectorizer configuration."""
        return self._vectorizer

    @property
    def model(self) -> ModelConfig:
        """Get model configuration."""
        return self._model

    @property
    def training(self) -> TrainingConfig:
        """Get training configuration."""
        return self._training

    @property
    def paths(self) -> Dict[str, Path]:
        """Get all path configurations."""
        return {
            "project_root": PROJECT_ROOT,
            "backend": BACKEND_DIR,
            "models": MODELS_DIR,
            "data": DATA_DIR,
        }

    @classmethod
    def default(cls) -> "Settings":
        """Get default settings instance."""
        return cls()


# =============================================================================
# Label Mappings
# =============================================================================

LABEL_MAP = {"ham": 0, "spam": 1}
LABEL_INV_MAP = {0: "ham", 1: "spam"}

# =============================================================================
# Default Configurations (for quick access)
# =============================================================================

DEFAULT_SETTINGS = Settings()
