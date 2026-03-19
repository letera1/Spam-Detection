"""
Training module for spam detection.

Provides high-level training functions and comparison utilities
for training and evaluating multiple models.
"""

from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path

import pandas as pd

from .data_loader import DataLoader
from .preprocessing import TextPreprocessor
from .model_pipeline import SpamDetectionPipeline
from .utils import setup_logger, ensure_dirs, MODELS_DIR

logger = setup_logger(__name__)


# =============================================================================
# Training Configuration
# =============================================================================


class TrainingConfig:
    """Configuration for training runs."""

    def __init__(
        self,
        vectorizer_types: List[str] = None,
        model_types: List[str] = None,
        test_size: float = 0.2,
        random_state: int = 42,
        use_grid_search: bool = True,
        cv_folds: int = 5,
    ):
        """
        Initialize training configuration.

        Args:
            vectorizer_types: List of vectorizers to try ('count', 'tfidf')
            model_types: List of models to try ('naive_bayes', 'logistic_regression')
            test_size: Fraction of data for testing
            random_state: Random seed for reproducibility
            use_grid_search: Whether to perform hyperparameter tuning
            cv_folds: Number of CV folds for grid search
        """
        self.vectorizer_types = vectorizer_types or ["count", "tfidf"]
        self.model_types = model_types or ["naive_bayes", "logistic_regression"]
        self.test_size = test_size
        self.random_state = random_state
        self.use_grid_search = use_grid_search
        self.cv_folds = cv_folds


# =============================================================================
# Training Functions
# =============================================================================


def train_single_model(
    X_train,
    y_train,
    X_test,
    y_test,
    vectorizer_type: str = "tfidf",
    model_type: str = "naive_bayes",
    preprocessor: Optional[TextPreprocessor] = None,
    use_grid_search: bool = True,
    cv_folds: int = 5,
) -> Tuple[SpamDetectionPipeline, Dict[str, Any]]:
    """
    Train a single model with specified configuration.

    Args:
        X_train: Training texts
        y_train: Training labels
        X_test: Test texts
        y_test: Test labels
        vectorizer_type: 'count' or 'tfidf'
        model_type: 'naive_bayes' or 'logistic_regression'
        preprocessor: Optional custom preprocessor
        use_grid_search: Whether to perform hyperparameter tuning
        cv_folds: Number of CV folds

    Returns:
        Tuple of (trained pipeline, results dictionary)
    """
    logger.info(f"\n{'='*60}")
    logger.info(f"Training: {model_type} + {vectorizer_type}")
    logger.info(f"{'='*60}")

    # Create and train pipeline
    pipeline = SpamDetectionPipeline(
        preprocessor=preprocessor,
        vectorizer_type=vectorizer_type,
        model_type=model_type,
    )

    # Train
    train_metrics = pipeline.train(
        X_train,
        y_train,
        X_val=X_test,
        y_val=y_test,
        use_grid_search=use_grid_search,
        cv_folds=cv_folds,
    )

    # Evaluate
    eval_results = pipeline.evaluate(X_test, y_test)

    results = {
        "vectorizer": vectorizer_type,
        "model": model_type,
        "train_metrics": train_metrics.get("train", {}),
        "test_metrics": eval_results["metrics"],
        "confusion_matrix": eval_results["confusion_matrix"],
        "classification_report": eval_results["classification_report"],
        "pipeline": pipeline,
    }

    return pipeline, results


def compare_models(
    data_path: Optional[str] = None,
    config: Optional[TrainingConfig] = None,
    preprocessor: Optional[TextPreprocessor] = None,
) -> Dict[str, Any]:
    """
    Train and compare multiple model configurations.

    Args:
        data_path: Path to dataset (uses default if None)
        config: TrainingConfig instance (uses defaults if None)
        preprocessor: Optional custom preprocessor

    Returns:
        Dictionary with all results and best model info
    """
    config = config or TrainingConfig()
    ensure_dirs()

    # Load data
    loader = DataLoader(data_path)
    data = loader.load_sms_spam_collection()
    loader.validate_data(data)

    X_train, X_test, y_train, y_test = loader.get_train_test_split(
        test_size=config.test_size,
        random_state=config.random_state,
    )

    # Train all combinations
    all_results = []
    best_f1 = 0
    best_result = None

    for vectorizer in config.vectorizer_types:
        for model in config.model_types:
            pipeline, results = train_single_model(
                X_train,
                y_train,
                X_test,
                y_test,
                vectorizer_type=vectorizer,
                model_type=model,
                preprocessor=preprocessor,
                use_grid_search=config.use_grid_search,
                cv_folds=config.cv_folds,
            )

            all_results.append(results)

            # Track best model
            f1 = results["test_metrics"]["f1"]
            if f1 > best_f1:
                best_f1 = f1
                best_result = results

    # Generate comparison summary
    comparison = generate_comparison_report(all_results)

    # Save best model
    if best_result:
        best_path = best_result["pipeline"].save()
        logger.info(f"\nBest model saved to: {best_path}")

    return {
        "all_results": all_results,
        "best_result": best_result,
        "comparison": comparison,
    }


def generate_comparison_report(results: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Generate a comparison DataFrame for all trained models.

    Args:
        results: List of result dictionaries from training

    Returns:
        DataFrame with model comparison metrics
    """
    rows = []
    for r in results:
        rows.append(
            {
                "Vectorizer": r["vectorizer"],
                "Model": r["model"],
                "Test Accuracy": f"{r['test_metrics']['accuracy']:.4f}",
                "Test Precision": f"{r['test_metrics']['precision']:.4f}",
                "Test Recall": f"{r['test_metrics']['recall']:.4f}",
                "Test F1": f"{r['test_metrics']['f1']:.4f}",
                "Train F1": f"{r['train_metrics']['f1']:.4f}",
            }
        )

    df = pd.DataFrame(rows)
    df = df.sort_values("Test F1", ascending=False)

    logger.info("\n" + "=" * 80)
    logger.info("MODEL COMPARISON SUMMARY")
    logger.info("=" * 80)
    logger.info(df.to_string(index=False))
    logger.info("=" * 80)

    return df


# =============================================================================
# Main Training Script
# =============================================================================


def run_training(
    data_path: Optional[str] = None,
    model_name: str = "default",
    use_best_config: bool = True,
) -> SpamDetectionPipeline:
    """
    Run the complete training pipeline.

    This is the main entry point for training.

    Args:
        data_path: Path to dataset (downloads default if None)
        model_name: Name for saving the model
        use_best_config: Whether to compare models or use single best config

    Returns:
        Trained SpamDetectionPipeline
    """
    logger.info("Starting spam detection training...")

    if use_best_config:
        # Compare all models and use the best
        results = compare_models(data_path=data_path)
        pipeline = results["best_result"]["pipeline"]
    else:
        # Use single best configuration (TF-IDF + Logistic Regression)
        loader = DataLoader(data_path)
        data = loader.load_sms_spam_collection()
        loader.validate_data(data)

        X_train, X_test, y_train, y_test = loader.get_train_test_split()

        pipeline, _ = train_single_model(
            X_train,
            y_train,
            X_test,
            y_test,
            vectorizer_type="tfidf",
            model_type="logistic_regression",
            use_grid_search=True,
        )

    # Save with specified name
    save_path = MODELS_DIR / f"{model_name}_spam_pipeline.joblib"
    pipeline.save(save_path)

    logger.info(f"\nTraining complete! Model saved to: {save_path}")

    return pipeline


if __name__ == "__main__":
    # Run training when script is executed directly
    run_training()
