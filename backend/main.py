"""
Spam Detection System - Main Entry Point

A production-ready ML system for spam/ham text classification.

Usage:
    python -m main train              # Train all models and save best
    python -m main train --quick      # Train single best model
    python -m main predict "message"  # Predict single message
    python -m main api                # Start FastAPI server
    python -m main interactive        # Interactive prediction session
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from backend.utils.logging import get_logger
from backend.models.trainer import compare_models, train_model
from backend.inference.predictor import SpamPredictor, interactive_predict

logger = get_logger(__name__)


def train_models(quick: bool = False, data_path: str = None):
    """Train spam detection models."""
    if quick:
        logger.info("Quick training mode - training single best model...")
        pipeline = train_model(data_path=data_path)
        save_path = pipeline.save()
        logger.info(f"Model saved to: {save_path}")
    else:
        logger.info("Full training mode - comparing all models...")
        results = compare_models(data_path=data_path)
        if results["best_result"]:
            best = results["best_result"]
            logger.info(f"Best model: {best['model']} + {best['vectorizer']}")
            logger.info(f"Test F1: {best['test_metrics']['f1']:.4f}")


def predict_message(text: str, model_path: str = None):
    """Predict if a single message is spam."""
    try:
        predictor = SpamPredictor(model_path)
        result = predictor.predict(text)
        print(f"\n{'='*50}")
        print(f"Result: {result.label.upper()}")
        print(f"Confidence: {result.confidence:.2%}")
        print(f"P(Ham): {result.probabilities[0]:.2%}")
        print(f"P(Spam): {result.probabilities[1]:.2%}")
        print(f"{'='*50}")
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please train a model first: python -m main train")


def start_api(host: str = "0.0.0.0", port: int = 8000):
    """Start the FastAPI server."""
    try:
        import uvicorn
        from backend.api.app import app

        logger.info(f"Starting API server on {host}:{port}")
        logger.info(f"API Docs: http://{host}:{port}/docs")
        uvicorn.run(app, host=host, port=port)
    except ImportError:
        print("Error: FastAPI and uvicorn are required for API mode")
        print("Install with: pip install fastapi uvicorn")
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please train a model first: python -m main train")


def main():
    """Main entry point with CLI argument parsing."""
    parser = argparse.ArgumentParser(
        description="Spam Detection System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m main train              Train all models and save best
  python -m main train --quick      Train single best model only
  python -m main predict "Hello!"   Predict single message
  python -m main api                Start FastAPI server
  python -m main interactive        Interactive prediction session
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Train command
    train_parser = subparsers.add_parser("train", help="Train spam detection models")
    train_parser.add_argument(
        "--quick",
        action="store_true",
        help="Train only the best model configuration (faster)",
    )
    train_parser.add_argument(
        "--data",
        type=str,
        default=None,
        help="Path to dataset (uses default SMS Spam Collection if None)",
    )

    # Predict command
    predict_parser = subparsers.add_parser("predict", help="Predict single message")
    predict_parser.add_argument("text", type=str, help="Message text to classify")
    predict_parser.add_argument(
        "--model", type=str, default=None, help="Path to model file"
    )

    # API command
    api_parser = subparsers.add_parser("api", help="Start FastAPI server")
    api_parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind")
    api_parser.add_argument("--port", type=int, default=8000, help="Port to bind")

    # Interactive command
    subparsers.add_parser("interactive", help="Interactive prediction session")

    args = parser.parse_args()

    if args.command == "train":
        train_models(quick=args.quick, data_path=args.data)
    elif args.command == "predict":
        predict_message(args.text, args.model)
    elif args.command == "api":
        start_api(args.host, args.port)
    elif args.command == "interactive":
        interactive_predict()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
