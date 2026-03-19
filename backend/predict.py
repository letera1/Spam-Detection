"""
Prediction module for spam detection.

Provides inference functionality for classifying new messages
using trained pipeline models.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional, Union

import joblib
import numpy as np

from .utils import setup_logger, MODELS_DIR, LABEL_INV_MAP

logger = setup_logger(__name__)


# =============================================================================
# Prediction Result Classes
# =============================================================================


class PredictionResult:
    """
    Container for a single prediction result.

    Attributes:
        text: Original input text
        label: Predicted label ('ham' or 'spam')
        confidence: Confidence score for the prediction
        probabilities: Class probabilities [P(ham), P(spam)]
    """

    def __init__(
        self,
        text: str,
        label: str,
        confidence: float,
        probabilities: np.ndarray,
    ):
        """
        Initialize prediction result.

        Args:
            text: Original input text
            label: Predicted label
            confidence: Confidence score
            probabilities: Class probabilities
        """
        self.text = text
        self.label = label
        self.confidence = confidence
        self.probabilities = probabilities

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "text": self.text,
            "label": self.label,
            "confidence": round(self.confidence, 4),
            "probabilities": {
                "ham": round(float(self.probabilities[0]), 4),
                "spam": round(float(self.probabilities[1]), 4),
            },
        }

    def __repr__(self) -> str:
        return f"PredictionResult(label={self.label}, confidence={self.confidence:.4f})"


# =============================================================================
# Predictor Class
# =============================================================================


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
                       If None, uses default saved model.
        """
        self.model_path = model_path
        self.pipeline = None
        self._is_loaded = False

    def load(self, model_path: Optional[Union[str, Path]] = None) -> "SpamPredictor":
        """
        Load a trained pipeline from disk.

        Args:
            model_path: Path to pipeline file (uses constructor path if None)

        Returns:
            Self for method chaining
        """
        path = model_path or self.model_path

        if path is None:
            # Try default locations
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
                f"No model found. Please train a model first or specify path.\n"
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

        # Get prediction and probabilities
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
            threshold: Probability threshold for spam classification

        Returns:
            List of PredictionResult objects
        """
        if not self._is_loaded:
            self.load()

        # Batch prediction
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
        """
        Quick prediction returning only labels (no probabilities).

        Args:
            texts: Single text or list of texts

        Returns:
            Array of predicted labels (0=ham, 1=spam)
        """
        if not self._is_loaded:
            self.load()

        if isinstance(texts, str):
            texts = [texts]

        return self.pipeline.predict(texts)

    def is_spam(self, text: str, threshold: float = 0.5) -> bool:
        """
        Quick boolean check if text is spam.

        Args:
            text: Message text to check
            threshold: Probability threshold

        Returns:
            True if spam, False if ham
        """
        result = self.predict(text, threshold)
        return result.label == "spam"

    def get_spam_probability(self, text: str) -> float:
        """
        Get the spam probability for a message.

        Args:
            text: Message text

        Returns:
            Probability that text is spam (0.0 to 1.0)
        """
        if not self._is_loaded:
            self.load()

        probs = self.pipeline.predict_proba([text])[0]
        return float(probs[1])


# =============================================================================
# Convenience Functions
# =============================================================================


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
        texts: List of messages to classify
        model_path: Optional path to model
        threshold: Classification threshold

    Returns:
        List of dictionaries with prediction results
    """
    predictor = SpamPredictor(model_path)
    results = predictor.predict_batch(texts, threshold)
    return [r.to_dict() for r in results]


# =============================================================================
# CLI Interface
# =============================================================================


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
        print("Please train a model first using: python -m backend.train")
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


if __name__ == "__main__":
    interactive_predict()
