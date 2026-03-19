"""
Spam Detection Backend

A production-ready ML system for spam/ham text classification.

Package Structure:
    - config: Configuration and hyperparameters
    - data: Data loading and preprocessing pipelines
    - models: Model definitions, training, and evaluation
    - inference: Prediction and serving utilities
    - api: REST API endpoints

Example:
    from backend import SpamDetector
    detector = SpamDetector.load("path/to/model")
    result = detector.predict("Win money now!")
"""

__version__ = "1.0.0"
__author__ = "ML Engineering Team"

from .models.pipeline import SpamDetectionPipeline
from .inference.predictor import SpamPredictor

__all__ = [
    "SpamDetectionPipeline",
    "SpamPredictor",
]
