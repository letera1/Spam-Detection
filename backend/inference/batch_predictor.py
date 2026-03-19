"""
Batch prediction handler.

Optimized for processing large volumes of messages.
"""

from typing import List, Dict, Any, Optional, Union
from pathlib import Path

from .predictor import SpamPredictor, PredictionResult


class BatchPredictor:
    """
    Batch prediction handler for high-volume inference.

    Optimized for processing large batches of messages.
    """

    def __init__(self, predictor: Optional[SpamPredictor] = None):
        """
        Initialize batch predictor.

        Args:
            predictor: SpamPredictor instance
        """
        self.predictor = predictor or SpamPredictor()

    def predict(
        self,
        texts: List[str],
        batch_size: int = 100,
        threshold: float = 0.5,
    ) -> List[Dict[str, Any]]:
        """
        Predict labels for a large batch of messages.

        Args:
            texts: List of message texts
            batch_size: Batch size for processing
            threshold: Classification threshold

        Returns:
            List of prediction result dictionaries
        """
        if not self.predictor._is_loaded:
            self.predictor.load()

        all_results = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            results = self.predictor.predict_batch(batch, threshold)
            all_results.extend([r.to_dict() for r in results])

        return all_results

    def predict_to_dataframe(self, texts: List[str], threshold: float = 0.5):
        """
        Predict and return results as a pandas DataFrame.

        Args:
            texts: List of message texts
            threshold: Classification threshold

        Returns:
            DataFrame with predictions
        """
        import pandas as pd

        results = self.predict(texts, threshold=threshold)
        df = pd.DataFrame(results)
        return df

    def predict_summary(
        self, texts: List[str], threshold: float = 0.5
    ) -> Dict[str, Any]:
        """
        Predict and return summary statistics.

        Args:
            texts: List of message texts
            threshold: Classification threshold

        Returns:
            Dictionary with summary statistics
        """
        results = self.predict(texts, threshold)

        spam_count = sum(1 for r in results if r["label"] == "spam")
        ham_count = len(results) - spam_count

        avg_spam_prob = sum(r["probabilities"]["spam"] for r in results) / len(results)

        return {
            "total": len(results),
            "spam_count": spam_count,
            "ham_count": ham_count,
            "spam_ratio": spam_count / len(results),
            "average_spam_probability": round(avg_spam_prob, 4),
        }
