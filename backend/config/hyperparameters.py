"""
Hyperparameter configurations and search grids.

Defines search spaces for hyperparameter optimization.
"""

from typing import Dict, List, Any


# =============================================================================
# Hyperparameter Search Grids
# =============================================================================

HYPERPARAM_GRIDS: Dict[str, Dict[str, List[Any]]] = {
    "naive_bayes": {
        "classifier__alpha": [0.1, 0.5, 1.0, 1.5, 2.0],
        "classifier__fit_prior": [True, False],
    },
    "logistic_regression": {
        "classifier__C": [0.01, 0.1, 1.0, 10.0, 100.0],
        "classifier__max_iter": [500, 1000, 1500, 2000],
        "classifier__solver": ["lbfgs", "saga"],
    },
}

# =============================================================================
# Default Model Parameters
# =============================================================================

DEFAULT_PARAMS: Dict[str, Dict[str, Any]] = {
    "naive_bayes": {
        "alpha": 1.0,
        "fit_prior": True,
    },
    "logistic_regression": {
        "C": 1.0,
        "max_iter": 1000,
        "solver": "lbfgs",
        "random_state": 42,
    },
}

# =============================================================================
# Vectorizer Presets
# =============================================================================

VECTORIZER_PRESETS: Dict[str, Dict[str, Any]] = {
    "minimal": {
        "max_features": 1000,
        "min_df": 1,
        "max_df": 0.9,
        "ngram_range": (1, 1),
    },
    "standard": {
        "max_features": 5000,
        "min_df": 2,
        "max_df": 0.95,
        "ngram_range": (1, 2),
    },
    "extensive": {
        "max_features": 10000,
        "min_df": 2,
        "max_df": 0.98,
        "ngram_range": (1, 3),
        "sublinear_tf": True,
    },
}

# =============================================================================
# Model Presets
# =============================================================================

MODEL_PRESETS: Dict[str, Dict[str, Any]] = {
    "fast": {
        "type": "naive_bayes",
        "alpha": 1.0,
    },
    "balanced": {
        "type": "logistic_regression",
        "C": 1.0,
        "max_iter": 1000,
    },
    "accurate": {
        "type": "logistic_regression",
        "C": 10.0,
        "max_iter": 2000,
        "solver": "saga",
    },
}

# =============================================================================
# Training Presets
# =============================================================================

TRAINING_PRESETS: Dict[str, Dict[str, Any]] = {
    "quick": {
        "test_size": 0.2,
        "use_grid_search": False,
        "cv_folds": 3,
    },
    "standard": {
        "test_size": 0.2,
        "use_grid_search": True,
        "cv_folds": 5,
    },
    "thorough": {
        "test_size": 0.2,
        "use_grid_search": True,
        "cv_folds": 10,
    },
}


def get_preset_config(preset_name: str) -> Dict[str, Any]:
    """
    Get a complete configuration preset.

    Args:
        preset_name: Name of preset ('quick', 'standard', 'thorough')

    Returns:
        Dictionary with vectorizer, model, and training configs
    """
    presets = {
        "quick": {
            "vectorizer": VECTORIZER_PRESETS["minimal"],
            "model": MODEL_PRESETS["fast"],
            "training": TRAINING_PRESETS["quick"],
        },
        "standard": {
            "vectorizer": VECTORIZER_PRESETS["standard"],
            "model": MODEL_PRESETS["balanced"],
            "training": TRAINING_PRESETS["standard"],
        },
        "thorough": {
            "vectorizer": VECTORIZER_PRESETS["extensive"],
            "model": MODEL_PRESETS["accurate"],
            "training": TRAINING_PRESETS["thorough"],
        },
    }

    if preset_name not in presets:
        raise ValueError(
            f"Unknown preset: {preset_name}. Available: {list(presets.keys())}"
        )

    return presets[preset_name]
