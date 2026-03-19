"""Inference package for spam detection predictions."""

from .predictor import SpamPredictor, PredictionResult
from .batch_predictor import BatchPredictor

__all__ = [
    "SpamPredictor",
    "PredictionResult",
    "BatchPredictor",
]
