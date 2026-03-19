"""
Training script for spam detection.

Main entry point for training spam detection models.

Usage:
    python -m backend.scripts.train              # Train all models
    python -m backend.scripts.train --quick      # Train single best model
    python -m backend.scripts.train --model logistic_regression
"""

import argparse
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.models.trainer import ModelTrainer, compare_models, train_model
from backend.config.settings import DEFAULT_SETTINGS, TrainingConfig
from backend.utils.logging import get_logger

logger = get_logger(__name__)


def train_all_models(data_path: str = None):
    """Train and compare all model combinations."""
    logger.info("=" * 60)
    logger.info("SPAM DETECTION - MODEL TRAINING")
    logger.info("=" * 60)

    results = compare_models(data_path=data_path)

    logger.info("\n" + "=" * 60)
    logger.info("TRAINING COMPLETE")
    logger.info("=" * 60)

    if results["best_result"]:
        best = results["best_result"]
        logger.info(f"Best Model: {best['model']} + {best['vectorizer']}")
        logger.info(f"Test F1 Score: {best['test_metrics']['f1']:.4f}")
        logger.info(f"Test Precision: {best['test_metrics']['precision']:.4f}")
        logger.info(f"Test Recall: {best['test_metrics']['recall']:.4f}")

    return results


def train_single_model(
    data_path: str = None,
    model_type: str = "logistic_regression",
    vectorizer_type: str = "tfidf",
):
    """Train a single model configuration."""
    logger.info(f"Training {model_type} with {vectorizer_type}...")

    pipeline = train_model(
        data_path=data_path,
        model_type=model_type,
        vectorizer_type=vectorizer_type,
    )

    save_path = pipeline.save()
    logger.info(f"Model saved to: {save_path}")

    return pipeline


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Train spam detection models")

    parser.add_argument(
        "--quick",
        action="store_true",
        help="Train only the best model configuration (faster)",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="logistic_regression",
        choices=["naive_bayes", "logistic_regression"],
        help="Model type to train",
    )
    parser.add_argument(
        "--vectorizer",
        type=str,
        default="tfidf",
        choices=["count", "tfidf"],
        help="Vectorizer type to use",
    )
    parser.add_argument(
        "--data",
        type=str,
        default=None,
        help="Path to dataset (uses default SMS Spam Collection if None)",
    )

    args = parser.parse_args()

    if args.quick:
        train_single_model(
            data_path=args.data,
            model_type=args.model,
            vectorizer_type=args.vectorizer,
        )
    else:
        train_all_models(data_path=args.data)


if __name__ == "__main__":
    main()
