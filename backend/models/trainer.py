"""
Model training and comparison module.

Provides high-level training functions for spam detection models.
"""

from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path

import pandas as pd

from .pipeline import SpamDetectionPipeline
from ..data.loader import DataLoader
from ..config.settings import TrainingConfig, DEFAULT_SETTINGS
from ..utils.logging import get_logger

logger = get_logger(__name__)


class ModelTrainer:
    """
    High-level trainer for spam detection models.

    Handles:
    - Data loading and splitting
    - Model training with hyperparameter tuning
    - Model comparison
    - Best model selection and saving
    """

    def __init__(self, config: Optional[TrainingConfig] = None):
        """
        Initialize the model trainer.

        Args:
            config: TrainingConfig instance (uses default if None)
        """
        self.config = config or DEFAULT_SETTINGS.training

    def train(
        self,
        X_train,
        y_train,
        X_test,
        y_test,
        vectorizer_type: str = "tfidf",
        model_type: str = "naive_bayes",
        preprocessor=None,
    ) -> Tuple[SpamDetectionPipeline, Dict[str, Any]]:
        """
        Train a single model.

        Args:
            X_train: Training texts
            y_train: Training labels
            X_test: Test texts
            y_test: Test labels
            vectorizer_type: 'count' or 'tfidf'
            model_type: 'naive_bayes' or 'logistic_regression'
            preprocessor: Optional custom preprocessor

        Returns:
            Tuple of (trained pipeline, results dictionary)
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"Training: {model_type} + {vectorizer_type}")
        logger.info(f"{'='*60}")

        pipeline = SpamDetectionPipeline(
            preprocessor=preprocessor,
            vectorizer_type=vectorizer_type,
            model_type=model_type,
        )

        train_metrics = pipeline.train(
            X_train,
            y_train,
            X_val=X_test,
            y_val=y_test,
            use_grid_search=self.config.use_grid_search,
            cv_folds=self.config.cv_folds,
        )

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

    def compare(
        self,
        data_path: Optional[str] = None,
        vectorizer_types: Optional[List[str]] = None,
        model_types: Optional[List[str]] = None,
        preprocessor=None,
    ) -> Dict[str, Any]:
        """
        Train and compare multiple model configurations.

        Args:
            data_path: Path to dataset
            vectorizer_types: List of vectorizers to try
            model_types: List of models to try
            preprocessor: Optional custom preprocessor

        Returns:
            Dictionary with all results and best model info
        """
        vectorizer_types = vectorizer_types or ["count", "tfidf"]
        model_types = model_types or ["naive_bayes", "logistic_regression"]

        # Load data
        loader = DataLoader(data_path)
        data = loader.load_sms_spam_collection()
        loader.validate_data(data)

        X_train, X_test, y_train, y_test = loader.get_train_test_split(
            test_size=self.config.test_size,
            random_state=self.config.random_state,
        )

        # Train all combinations
        all_results = []
        best_f1 = 0
        best_result = None

        for vectorizer in vectorizer_types:
            for model in model_types:
                pipeline, results = self.train(
                    X_train,
                    y_train,
                    X_test,
                    y_test,
                    vectorizer_type=vectorizer,
                    model_type=model,
                    preprocessor=preprocessor,
                )

                all_results.append(results)

                f1 = results["test_metrics"]["f1"]
                if f1 > best_f1:
                    best_f1 = f1
                    best_result = results

        comparison = self._generate_comparison(all_results)

        if best_result:
            best_path = best_result["pipeline"].save()
            logger.info(f"\nBest model saved to: {best_path}")

        return {
            "all_results": all_results,
            "best_result": best_result,
            "comparison": comparison,
        }

    def _generate_comparison(self, results: List[Dict[str, Any]]) -> pd.DataFrame:
        """Generate a comparison DataFrame."""
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


def train_model(
    data_path: Optional[str] = None,
    vectorizer_type: str = "tfidf",
    model_type: str = "logistic_regression",
    preprocessor=None,
) -> SpamDetectionPipeline:
    """
    Convenience function to train a single model.

    Args:
        data_path: Path to dataset
        vectorizer_type: Vectorizer type
        model_type: Model type
        preprocessor: Optional custom preprocessor

    Returns:
        Trained SpamDetectionPipeline
    """
    trainer = ModelTrainer()

    loader = DataLoader(data_path)
    data = loader.load_sms_spam_collection()
    loader.validate_data(data)

    X_train, X_test, y_train, y_test = loader.get_train_test_split()

    pipeline, _ = trainer.train(
        X_train,
        y_train,
        X_test,
        y_test,
        vectorizer_type=vectorizer_type,
        model_type=model_type,
        preprocessor=preprocessor,
    )

    return pipeline


def compare_models(
    data_path: Optional[str] = None,
    preprocessor=None,
) -> Dict[str, Any]:
    """
    Convenience function to compare all model combinations.

    Args:
        data_path: Path to dataset
        preprocessor: Optional custom preprocessor

    Returns:
        Dictionary with comparison results
    """
    trainer = ModelTrainer()
    return trainer.compare(data_path=data_path, preprocessor=preprocessor)
