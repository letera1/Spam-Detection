"""
Advanced Prediction module for spam detection.

Provides inference functionality for classifying new messages
with detailed analysis and feature extraction.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass

import joblib
import numpy as np

from ..config.settings import MODELS_DIR, LABEL_INV_MAP
from ..utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class PredictionResult:
    """
    Container for a single prediction result with detailed analysis.

    Attributes:
        text: Original input text
        label: Predicted label ('ham' or 'spam')
        confidence: Confidence score for the prediction
        probabilities: Class probabilities [P(ham), P(spam)]
        features: Extracted spam-indicative features
        explanation: Human-readable explanation
    """

    text: str
    label: str
    confidence: float
    probabilities: np.ndarray
    features: Optional[Dict[str, Any]] = None
    explanation: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {
            "text": self.text,
            "label": self.label,
            "confidence": round(self.confidence, 4),
            "probabilities": {
                "ham": round(float(self.probabilities[0]), 4),
                "spam": round(float(self.probabilities[1]), 4),
            },
        }
        if self.features:
            result["features"] = self.features
        if self.explanation:
            result["explanation"] = self.explanation
        return result

    def __repr__(self) -> str:
        return f"PredictionResult(label={self.label}, confidence={self.confidence:.4f})"


class SpamPredictor:
    """
    High-level predictor for spam detection.

    Handles model loading, preprocessing, and prediction
    with a clean inference API.

    Example:
        predictor = SpamPredictor()
        result = predictor.predict("Win a free iPhone now!")
        print(result.label)  # 'spam'
    """

    def __init__(self, model_path: Optional[Union[str, Path]] = None):
        """
        Initialize the predictor.

        Args:
            model_path: Path to trained pipeline file.
        """
        self.model_path = model_path
        self.pipeline = None
        self._is_loaded = False

    def load(self, model_path: Optional[Union[str, Path]] = None) -> "SpamPredictor":
        """
        Load a trained pipeline from disk.

        Args:
            model_path: Path to pipeline file

        Returns:
            Self for method chaining
        """
        path = model_path or self.model_path

        if path is None:
            default_paths = [
                MODELS_DIR / "default_spam_pipeline.joblib",
                MODELS_DIR / "logistic_regression_spam_pipeline.joblib",
                MODELS_DIR / "naive_bayes_spam_pipeline.joblib",
            ]
            for p in default_paths:
                if p.exists():
                    path = p
                    break

        if path is None or not Path(path).exists():
            raise FileNotFoundError(
                f"No model found. Please train a model first.\n"
                f"Searched: {default_paths if path is None else path}"
            )

        logger.info(f"Loading model from: {path}")
        self.pipeline = joblib.load(path)
        self._is_loaded = True
        logger.info("Model loaded successfully")

        return self

    def predict(self, text: str, threshold: float = 0.5) -> PredictionResult:
        """
        Predict whether a single message is spam or ham.

        Args:
            text: The message text to classify
            threshold: Probability threshold for spam classification

        Returns:
            PredictionResult with label and confidence
        """
        if not self._is_loaded:
            self.load()

        probs = self.pipeline.predict_proba([text])[0]
        pred_idx = 1 if probs[1] >= threshold else 0
        label = LABEL_INV_MAP[pred_idx]
        confidence = probs[pred_idx]

        return PredictionResult(
            text=text,
            label=label,
            confidence=confidence,
            probabilities=probs,
        )

    def predict_batch(
        self, texts: List[str], threshold: float = 0.5
    ) -> List[PredictionResult]:
        """
        Predict labels for multiple messages.

        Args:
            texts: List of message texts
            threshold: Probability threshold

        Returns:
            List of PredictionResult objects
        """
        if not self._is_loaded:
            self.load()

        probs = self.pipeline.predict_proba(texts)
        pred_indices = np.where(probs[:, 1] >= threshold, 1, 0)

        results = []
        for text, pred_idx, prob in zip(texts, pred_indices, probs):
            label = LABEL_INV_MAP[pred_idx]
            confidence = prob[pred_idx]
            results.append(
                PredictionResult(
                    text=text,
                    label=label,
                    confidence=confidence,
                    probabilities=prob,
                )
            )

        return results

    def predict_labels_only(self, texts: Union[str, List[str]]) -> np.ndarray:
        """Quick prediction returning only labels."""
        if not self._is_loaded:
            self.load()

        if isinstance(texts, str):
            texts = [texts]

        return self.pipeline.predict(texts)

    def is_spam(self, text: str, threshold: float = 0.5) -> bool:
        """Quick boolean check if text is spam."""
        result = self.predict(text, threshold)
        return result.label == "spam"

    def get_spam_probability(self, text: str) -> float:
        """Get the spam probability for a message."""
        if not self._is_loaded:
            self.load()

        probs = self.pipeline.predict_proba([text])[0]
        return float(probs[1])


class BatchPredictor:
    """
    Batch prediction handler for high-volume inference.

    Optimized for processing large batches of messages.
    """

    def __init__(self, predictor: Optional[SpamPredictor] = None):
        """
        Initialize batch predictor.

        Args:
            predictor: SpamPredictor instance (creates new if None)
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

    def predict_to_dataframe(
        self,
        texts: List[str],
        threshold: float = 0.5,
    ):
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


def predict_message(
    text: str,
    model_path: Optional[Union[str, Path]] = None,
    threshold: float = 0.5,
) -> Dict[str, Any]:
    """
    Convenience function for single message prediction.

    Args:
        text: Message to classify
        model_path: Optional path to model
        threshold: Classification threshold

    Returns:
        Dictionary with prediction results
    """
    predictor = SpamPredictor(model_path)
    result = predictor.predict(text, threshold)
    return result.to_dict()


def predict_messages(
    texts: List[str],
    model_path: Optional[Union[str, Path]] = None,
    threshold: float = 0.5,
) -> List[Dict[str, Any]]:
    """
    Convenience function for batch prediction.

    Args:
        texts: List of messages
        model_path: Optional path to model
        threshold: Classification threshold

    Returns:
        List of dictionaries with prediction results
    """
    predictor = SpamPredictor(model_path)
    results = predictor.predict_batch(texts, threshold)
    return [r.to_dict() for r in results]


def interactive_predict():
    """Run an interactive prediction session."""
    print("\n" + "=" * 60)
    print("SPAM DETECTION - Interactive Prediction")
    print("=" * 60)
    print("Enter messages to classify. Type 'quit' to exit.\n")

    try:
        predictor = SpamPredictor()
        predictor.load()
        print("Model loaded successfully!\n")
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please train a model first using: python -m main train")
        return

    while True:
        try:
            text = input("Message: ").strip()

            if text.lower() in ("quit", "exit", "q"):
                print("Goodbye!")
                break

            if not text:
                continue

            result = predictor.predict(text)
            print(f"  Result: {result.label.upper()}")
            print(f"  Confidence: {result.confidence:.2%}")
            print(f"  P(ham): {result.probabilities[0]:.2%}, P(spam): {result.probabilities[1]:.2%}")
            print()

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}\n")
