"""
ML pipeline construction and management.

Encapsulates the full ML pipeline:
- Text preprocessing
- Feature extraction (CountVectorizer or TF-IDF)
- Classification model
"""

import joblib
from pathlib import Path
from typing import Optional, Dict, Any, List

from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression

from ..config.settings import (
    MODELS_DIR,
    DEFAULT_PARAMS,
    HYPERPARAM_GRIDS,
    VECTORIZER_PRESETS,
)
from ..utils.logging import get_logger

logger = get_logger(__name__)


class ModelFactory:
    """Factory for creating classifier models."""

    @staticmethod
    def create_naive_bayes(alpha: float = 1.0, fit_prior: bool = True) -> MultinomialNB:
        """Create a Multinomial Naive Bayes classifier."""
        return MultinomialNB(alpha=alpha, fit_prior=fit_prior)

    @staticmethod
    def create_logistic_regression(
        C: float = 1.0, max_iter: int = 1000, solver: str = "lbfgs"
    ) -> LogisticRegression:
        """Create a Logistic Regression classifier."""
        return LogisticRegression(C=C, max_iter=max_iter, solver=solver, random_state=42)

    @staticmethod
    def get_model(model_type: str, **kwargs):
        """Create a model by type name."""
        if model_type == "naive_bayes":
            return ModelFactory.create_naive_bayes(**kwargs)
        elif model_type == "logistic_regression":
            return ModelFactory.create_logistic_regression(**kwargs)
        else:
            raise ValueError(f"Unknown model type: {model_type}")


class SpamPipelineBuilder:
    """
    Builder for creating spam detection pipelines.

    Constructs sklearn Pipeline objects with:
    1. Preprocessing transformer
    2. Vectorizer (Count or TF-IDF)
    3. Classifier
    """

    def __init__(self):
        """Initialize the pipeline builder."""
        self.preprocessor = None
        self.vectorizer_type: str = "tfidf"
        self.vectorizer_params: Dict[str, Any] = {}
        self.model_type: str = "naive_bayes"
        self.model_params: Dict[str, Any] = {}

    def with_preprocessor(self, preprocessor) -> "SpamPipelineBuilder":
        """Set the text preprocessor."""
        self.preprocessor = preprocessor
        return self

    def with_vectorizer(
        self, vectorizer_type: str = "tfidf", **kwargs
    ) -> "SpamPipelineBuilder":
        """Configure the vectorizer."""
        self.vectorizer_type = vectorizer_type
        self.vectorizer_params = kwargs or VECTORIZER_PRESETS.get("standard", {})
        return self

    def with_model(
        self, model_type: str = "naive_bayes", **kwargs
    ) -> "SpamPipelineBuilder":
        """Configure the classifier model."""
        self.model_type = model_type
        self.model_params = kwargs or DEFAULT_PARAMS.get(model_type, {})
        return self

    def build(self) -> Pipeline:
        """Build and return the complete pipeline."""
        steps = []

        if self.preprocessor:
            steps.append(("preprocessor", self.preprocessor.create_sklearn_transformer()))

        vectorizer = self._create_vectorizer()
        steps.append(("vectorizer", vectorizer))

        classifier = self._create_classifier()
        steps.append(("classifier", classifier))

        pipeline = Pipeline(steps)
        logger.info(f"Built pipeline with {len(steps)} steps")

        return pipeline

    def _create_vectorizer(self):
        """Create the vectorizer based on configuration."""
        params = self.vectorizer_params or VECTORIZER_PRESETS.get("standard", {})

        if self.vectorizer_type == "count":
            return CountVectorizer(**params)
        else:
            return TfidfVectorizer(**params)

    def _create_classifier(self):
        """Create the classifier based on configuration."""
        return ModelFactory.get_model(self.model_type, **self.model_params)


class SpamDetectionPipeline:
    """
    High-level wrapper for spam detection pipeline.

    Handles:
    - Pipeline construction
    - Training with hyperparameter tuning
    - Evaluation
    - Model persistence
    - Inference
    """

    def __init__(
        self,
        preprocessor=None,
        vectorizer_type: str = "tfidf",
        model_type: str = "naive_bayes",
    ):
        """
        Initialize the spam detection pipeline.

        Args:
            preprocessor: TextPreprocessor instance
            vectorizer_type: 'count' or 'tfidf'
            model_type: 'naive_bayes' or 'logistic_regression'
        """
        self.preprocessor = preprocessor
        self.vectorizer_type = vectorizer_type
        self.model_type = model_type
        self.pipeline: Optional[Pipeline] = None
        self.is_trained = False
        self._metrics: Dict[str, Any] = {}

    def build_pipeline(self) -> Pipeline:
        """Build the sklearn pipeline."""
        builder = SpamPipelineBuilder()
        self.pipeline = (
            builder.with_preprocessor(self.preprocessor)
            .with_vectorizer(self.vectorizer_type)
            .with_model(self.model_type)
            .build()
        )
        return self.pipeline

    def train(
        self,
        X_train,
        y_train,
        X_val=None,
        y_val=None,
        use_grid_search: bool = True,
        cv_folds: int = 5,
    ) -> Dict[str, Any]:
        """
        Train the pipeline on provided data.

        Args:
            X_train: Training texts
            y_train: Training labels
            X_val: Validation texts (optional)
            y_val: Validation labels (optional)
            use_grid_search: Whether to perform hyperparameter tuning
            cv_folds: Number of CV folds for grid search

        Returns:
            Dictionary with training metrics
        """
        if self.pipeline is None:
            self.build_pipeline()

        logger.info(f"Training {self.model_type} with {self.vectorizer_type} vectorizer")

        if use_grid_search:
            self._train_with_grid_search(X_train, y_train, cv_folds)
        else:
            self.pipeline.fit(X_train, y_train)

        train_preds = self.pipeline.predict(X_train)
        self._metrics["train"] = self._compute_metrics(y_train, train_preds)

        if X_val is not None and y_val is not None:
            val_preds = self.pipeline.predict(X_val)
            self._metrics["validation"] = self._compute_metrics(y_val, val_preds)

        self.is_trained = True
        logger.info(f"Training complete. Train F1: {self._metrics['train']['f1']:.4f}")

        return self._metrics

    def _train_with_grid_search(self, X_train, y_train, cv_folds: int):
        """Perform grid search for hyperparameter tuning."""
        from sklearn.model_selection import GridSearchCV

        param_grid = self._get_param_grid()

        if not param_grid:
            logger.warning("No hyperparameter grid found, training with defaults")
            self.pipeline.fit(X_train, y_train)
            return

        logger.info(f"Performing grid search with {cv_folds}-fold CV")

        grid_search = GridSearchCV(
            self.pipeline,
            param_grid,
            cv=cv_folds,
            scoring="f1",
            n_jobs=-1,
            verbose=1,
        )

        grid_search.fit(X_train, y_train)

        logger.info(f"Best parameters: {grid_search.best_params_}")
        logger.info(f"Best CV F1 score: {grid_search.best_score_:.4f}")

        self.pipeline = grid_search.best_estimator_
        self._metrics["grid_search"] = {
            "best_params": grid_search.best_params_,
            "best_score": grid_search.best_score_,
        }

    def _get_param_grid(self) -> Dict[str, List]:
        """Get hyperparameter grid for current model."""
        return HYPERPARAM_GRIDS.get(self.model_type, {})

    def _compute_metrics(self, y_true, y_pred) -> Dict[str, float]:
        """Compute classification metrics."""
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

        return {
            "accuracy": accuracy_score(y_true, y_pred),
            "precision": precision_score(y_true, y_pred),
            "recall": recall_score(y_true, y_pred),
            "f1": f1_score(y_true, y_pred),
        }

    def evaluate(self, X_test, y_test) -> Dict[str, Any]:
        """Evaluate the trained pipeline on test data."""
        from .evaluator import ModelEvaluator

        if not self.is_trained:
            raise RuntimeError("Pipeline must be trained before evaluation")

        evaluator = ModelEvaluator(self.pipeline)
        return evaluator.evaluate(X_test, y_test)

    def predict(self, texts):
        """Predict labels for input texts."""
        if not self.is_trained:
            raise RuntimeError("Pipeline must be trained before prediction")

        if isinstance(texts, str):
            texts = [texts]

        return self.pipeline.predict(texts)

    def predict_proba(self, texts):
        """Predict class probabilities for input texts."""
        if not self.is_trained:
            raise RuntimeError("Pipeline must be trained before prediction")

        if isinstance(texts, str):
            texts = [texts]

        return self.pipeline.predict_proba(texts)

    def save(self, path: Optional[Union[str, Path]] = None) -> Path:
        """Save the trained pipeline to disk."""
        if not self.is_trained:
            raise RuntimeError("Cannot save untrained pipeline")

        if path is None:
            path = MODELS_DIR / f"{self.model_type}_spam_pipeline.joblib"
        else:
            path = Path(path)

        joblib.dump(self.pipeline, path)
        logger.info(f"Pipeline saved to: {path}")

        return path

    @classmethod
    def load(cls, path: Union[str, Path]) -> "SpamDetectionPipeline":
        """Load a trained pipeline from disk."""
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Pipeline file not found: {path}")

        pipeline = joblib.load(path)

        instance = cls()
        instance.pipeline = pipeline
        instance.is_trained = True

        logger.info(f"Pipeline loaded from: {path}")
        return instance
