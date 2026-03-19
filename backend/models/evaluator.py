"""
Model evaluation module.

Provides comprehensive evaluation metrics and error analysis.
"""

import numpy as np
from typing import Dict, Any, Optional

from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    precision_score,
    recall_score,
    f1_score,
    accuracy_score,
)

from ..utils.logging import get_logger

logger = get_logger(__name__)


class ModelEvaluator:
    """
    Comprehensive model evaluator for spam detection.

    Provides:
    - Standard metrics (accuracy, precision, recall, F1)
    - Confusion matrix analysis
    - Error analysis (FP/FN breakdown)
    - Classification reports
    """

    def __init__(self, pipeline):
        """
        Initialize the evaluator.

        Args:
            pipeline: Trained sklearn pipeline
        """
        self.pipeline = pipeline

    def evaluate(
        self, X_test, y_test, detailed: bool = True
    ) -> Dict[str, Any]:
        """
        Evaluate the model on test data.

        Args:
            X_test: Test texts
            y_test: Test labels
            detailed: Whether to include detailed analysis

        Returns:
            Dictionary with evaluation results
        """
        y_pred = self.pipeline.predict(X_test)
        y_proba = self.pipeline.predict_proba(X_test)[:, 1]

        metrics = self._compute_metrics(y_test, y_pred)
        conf_matrix = confusion_matrix(y_test, y_pred)
        class_report = classification_report(
            y_test, y_pred, target_names=["ham", "spam"]
        )

        results = {
            "metrics": metrics,
            "confusion_matrix": conf_matrix,
            "classification_report": class_report,
            "predictions": y_pred,
            "probabilities": y_proba,
        }

        if detailed:
            results["error_analysis"] = self._analyze_errors(X_test, y_test, y_pred)

        self._log_results(metrics, conf_matrix, class_report)

        return results

    def _compute_metrics(self, y_true, y_pred) -> Dict[str, float]:
        """Compute classification metrics."""
        return {
            "accuracy": accuracy_score(y_true, y_pred),
            "precision": precision_score(y_true, y_pred),
            "recall": recall_score(y_true, y_pred),
            "f1": f1_score(y_true, y_pred),
        }

    def _analyze_errors(
        self, X_test, y_true, y_pred
    ) -> Dict[str, Any]:
        """Analyze false positives and false negatives."""
        fp_mask = (y_true == 0) & (y_pred == 1)
        fn_mask = (y_true == 1) & (y_pred == 0)

        fp_count = fp_mask.sum()
        fn_count = fn_mask.sum()

        error_analysis = {
            "false_positives": {
                "count": int(fp_count),
                "description": "Ham messages classified as spam",
                "impact": "User may miss important messages",
            },
            "false_negatives": {
                "count": int(fn_count),
                "description": "Spam messages classified as ham",
                "impact": "User receives unwanted messages",
            },
        }

        # Sample errors
        if hasattr(X_test, "iloc"):
            if fp_count > 0:
                fp_indices = np.where(fp_mask)[0][:3]
                error_analysis["false_positives"]["samples"] = [
                    X_test.iloc[idx][:100] for idx in fp_indices
                ]
            if fn_count > 0:
                fn_indices = np.where(fn_mask)[0][:3]
                error_analysis["false_negatives"]["samples"] = [
                    X_test.iloc[idx][:100] for idx in fn_indices
                ]

        return error_analysis

    def _log_results(
        self,
        metrics: Dict[str, float],
        conf_matrix: np.ndarray,
        class_report: str,
    ):
        """Log evaluation results."""
        logger.info("\n" + "=" * 60)
        logger.info("EVALUATION RESULTS")
        logger.info("=" * 60)
        logger.info(f"Accuracy:  {metrics['accuracy']:.4f}")
        logger.info(f"Precision: {metrics['precision']:.4f}")
        logger.info(f"Recall:    {metrics['recall']:.4f}")
        logger.info(f"F1 Score:  {metrics['f1']:.4f}")
        logger.info("\nConfusion Matrix:")
        logger.info(f"{conf_matrix}")
        logger.info("\nClassification Report:")
        logger.info(class_report)
        logger.info("=" * 60)

    def get_feature_importance(
        self, top_n: int = 20
    ) -> Dict[str, Dict[str, Any]]:
        """
        Get top features by importance.

        Args:
            top_n: Number of top features to return

        Returns:
            Dictionary with spam and ham top features
        """
        # Get vectorizer and classifier from pipeline
        vectorizer = None
        classifier = None

        for name, step in self.pipeline.steps:
            if "vectorizer" in name or "tfidf" in name or "count" in name:
                vectorizer = step
            if "classifier" in name or "model" in name:
                classifier = step

        if vectorizer is None or classifier is None:
            return {}

        feature_names = vectorizer.get_feature_names_out()

        if hasattr(classifier, "coef_"):
            coef = classifier.coef_[0]
            top_indices = np.argsort(np.abs(coef))[-top_n:]

            spam_features = []
            ham_features = []

            for idx in top_indices:
                feature = feature_names[idx]
                weight = coef[idx]
                if weight > 0:
                    spam_features.append((feature, weight))
                else:
                    ham_features.append((feature, weight))

            return {
                "spam_indicators": [
                    {"feature": f, "weight": round(w, 4)}
                    for f, w in sorted(spam_features, key=lambda x: x[1], reverse=True)[
                        :10
                    ]
                ],
                "ham_indicators": [
                    {"feature": f, "weight": round(w, 4)}
                    for f, w in sorted(ham_features, key=lambda x: x[1])[:10]
                ],
            }

        return {}
