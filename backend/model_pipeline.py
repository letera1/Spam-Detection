"""
Model pipeline module for spam detection.

Encapsulates the full ML pipeline:
- Text preprocessing
- Feature extraction (CountVectorizer or TF-IDF)
- Classification model

Provides unified training and inference interface.
"""

import joblib
from pathlib import Path
from typing import Optional, Tuple, Dict, Any, List
from abc import ABC, abstractmethod

import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV, cross_val_score
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    precision_score,
    recall_score,
    f1_score,
    accuracy_score,
)

from .preprocessing import TextPreprocessor, PreprocessingTransformer
from .utils import (
    setup_logger,
    LABEL_INV_MAP,
    DEFAULT_MODEL_PARAMS,
    HYPERPARAM_GRIDS,
    VECTORIZER_CONFIG,
    get_pipeline_path,
)

logger = setup_logger(__name__)


# =============================================================================
# Model Factory
# =============================================================================


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
    def get_hyperparam_grid(model_type: str) -> Dict[str, List]:
        """Get hyperparameter search grid for a model type."""
        return HYPERPARAM_GRIDS.get(model_type, {})


# =============================================================================
# Pipeline Builder
# =============================================================================


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
        self.preprocessor: Optional[TextPreprocessor] = None
        self.vectorizer_type: str = "tfidf"
        self.vectorizer_params: Dict[str, Any] = {}
        self.model_type: str = "naive_bayes"
        self.model_params: Dict[str, Any] = {}

    def with_preprocessor(self, preprocessor: TextPreprocessor) -> "SpamPipelineBuilder":
        """Set the text preprocessor."""
        self.preprocessor = preprocessor
        return self

    def with_vectorizer(
        self, vectorizer_type: str = "tfidf", **kwargs
    ) -> "SpamPipelineBuilder":
        """
        Configure the vectorizer.

        Args:
            vectorizer_type: 'count' or 'tfidf'
            **kwargs: Additional vectorizer parameters
        """
        self.vectorizer_type = vectorizer_type
        self.vectorizer_params = kwargs
        return self

    def with_model(
        self, model_type: str = "naive_bayes", **kwargs
    ) -> "SpamPipelineBuilder":
        """
        Configure the classifier model.

        Args:
            model_type: 'naive_bayes' or 'logistic_regression'
            **kwargs: Additional model parameters
        """
        self.model_type = model_type
        self.model_params = kwargs
        return self

    def build(self) -> Pipeline:
        """
        Build and return the complete pipeline.

        Returns:
            sklearn Pipeline object
        """
        steps = []

        # Add preprocessing
        if self.preprocessor:
            steps.append(("preprocessor", self.preprocessor.create_sklearn_transformer()))

        # Add vectorizer
        vectorizer = self._create_vectorizer()
        steps.append(("vectorizer", vectorizer))

        # Add classifier
        classifier = self._create_classifier()
        steps.append(("classifier", classifier))

        pipeline = Pipeline(steps)
        logger.info(f"Built pipeline with {len(steps)} steps")

        return pipeline

    def _create_vectorizer(self):
        """Create the vectorizer based on configuration."""
        params = self.vectorizer_params or VECTORIZER_CONFIG.get(
            self.vectorizer_type, {}
        )

        if self.vectorizer_type == "count":
            return CountVectorizer(**params)
        else:
            return TfidfVectorizer(**params)

    def _create_classifier(self):
        """Create the classifier based on configuration."""
        params = self.model_params or DEFAULT_MODEL_PARAMS.get(self.model_type, {})

        if self.model_type == "naive_bayes":
            return ModelFactory.create_naive_bayes(**params)
        else:
            return ModelFactory.create_logistic_regression(**params)


# =============================================================================
# Pipeline Wrapper
# =============================================================================


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
        preprocessor: Optional[TextPreprocessor] = None,
        vectorizer_type: str = "tfidf",
        model_type: str = "naive_bayes",
    ):
        """
        Initialize the spam detection pipeline.

        Args:
            preprocessor: TextPreprocessor instance (uses default if None)
            vectorizer_type: 'count' or 'tfidf'
            model_type: 'naive_bayes' or 'logistic_regression'
        """
        self.preprocessor = preprocessor or TextPreprocessor()
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

        # Evaluate on training data
        train_preds = self.pipeline.predict(X_train)
        self._metrics["train"] = self._compute_metrics(y_train, train_preds)

        # Evaluate on validation data if provided
        if X_val is not None and y_val is not None:
            val_preds = self.pipeline.predict(X_val)
            self._metrics["validation"] = self._compute_metrics(y_val, val_preds)

        self.is_trained = True
        logger.info(f"Training complete. Train F1: {self._metrics['train']['f1']:.4f}")

        return self._metrics

    def _train_with_grid_search(self, X_train, y_train, cv_folds: int):
        """Perform grid search for hyperparameter tuning."""
        param_grid = ModelFactory.get_hyperparam_grid(self.model_type)

        if not param_grid:
            logger.warning("No hyperparameter grid found, training with defaults")
            self.pipeline.fit(X_train, y_train)
            return

        logger.info(f"Performing grid search with {cv_folds}-fold CV")
        logger.info(f"Parameter grid: {param_grid}")

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

    def _compute_metrics(self, y_true, y_pred) -> Dict[str, float]:
        """Compute classification metrics."""
        return {
            "accuracy": accuracy_score(y_true, y_pred),
            "precision": precision_score(y_true, y_pred),
            "recall": recall_score(y_true, y_pred),
            "f1": f1_score(y_true, y_pred),
        }

    def evaluate(self, X_test, y_test) -> Dict[str, Any]:
        """
        Evaluate the trained pipeline on test data.

        Args:
            X_test: Test texts
            y_test: Test labels

        Returns:
            Dictionary with evaluation metrics and reports
        """
        if not self.is_trained:
            raise RuntimeError("Pipeline must be trained before evaluation")

        y_pred = self.pipeline.predict(X_test)
        y_proba = self.pipeline.predict_proba(X_test)[:, 1]

        metrics = self._compute_metrics(y_test, y_pred)
        conf_matrix = confusion_matrix(y_test, y_pred)
        class_report = classification_report(
            y_test, y_pred, target_names=["ham", "spam"]
        )

        self._metrics["test"] = metrics

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

        # Log FP/FN analysis
        self._log_error_analysis(y_test, y_pred, X_test)

        return {
            "metrics": metrics,
            "confusion_matrix": conf_matrix,
            "classification_report": class_report,
            "predictions": y_pred,
            "probabilities": y_proba,
        }

    def _log_error_analysis(self, y_true, y_pred, X_test):
        """Log analysis of false positives and false negatives."""
        fp_mask = (y_true == 0) & (y_pred == 1)
        fn_mask = (y_true == 1) & (y_pred == 0)

        fp_count = fp_mask.sum()
        fn_count = fn_mask.sum()

        logger.info("\nERROR ANALYSIS")
        logger.info("-" * 40)
        logger.info(f"False Positives (ham classified as spam): {fp_count}")
        logger.info(f"False Negatives (spam classified as ham): {fn_count}")

        if fn_count > 0:
            logger.info("\nSample False Negatives (missed spam):")
            fn_indices = np.where(fn_mask)[0][:3]
            for idx in fn_indices:
                text = X_test.iloc[idx][:100] if hasattr(X_test, "iloc") else X_test[idx][:100]
                logger.info(f"  - {text}...")

        if fp_count > 0:
            logger.info("\nSample False Positives (ham flagged as spam):")
            fp_indices = np.where(fp_mask)[0][:3]
            for idx in fp_indices:
                text = X_test.iloc[idx][:100] if hasattr(X_test, "iloc") else X_test[idx][:100]
                logger.info(f"  - {text}...")

        # Impact explanation
        logger.info("\nIMPACT ANALYSIS")
        logger.info("-" * 40)
        logger.info("False Positives: Legitimate messages marked as spam")
        logger.info("  - User may miss important messages")
        logger.info("  - Higher user frustration")
        logger.info("\nFalse Negatives: Spam messages not detected")
        logger.info("  - User receives unwanted messages")
        logger.info("  - Lower trust in system")
        logger.info("\nFor spam detection, minimizing False Negatives is typically")
        logger.info("prioritized, but False Positives should be kept very low.")

    def predict(self, texts) -> np.ndarray:
        """
        Predict labels for input texts.

        Args:
            texts: Single text or list of texts

        Returns:
            Array of predicted labels (0=ham, 1=spam)
        """
        if not self.is_trained:
            raise RuntimeError("Pipeline must be trained before prediction")

        if isinstance(texts, str):
            texts = [texts]

        return self.pipeline.predict(texts)

    def predict_proba(self, texts) -> np.ndarray:
        """
        Predict class probabilities for input texts.

        Args:
            texts: Single text or list of texts

        Returns:
            Array of shape (n_samples, 2) with class probabilities
        """
        if not self.is_trained:
            raise RuntimeError("Pipeline must be trained before prediction")

        if isinstance(texts, str):
            texts = [texts]

        return self.pipeline.predict_proba(texts)

    def save(self, path: Optional[Union[str, Path]] = None) -> Path:
        """
        Save the trained pipeline to disk.

        Args:
            path: Optional save path (auto-generates if None)

        Returns:
            Path to saved file
        """
        if not self.is_trained:
            raise RuntimeError("Cannot save untrained pipeline")

        if path is None:
            path = get_pipeline_path(self.model_type)
        else:
            path = Path(path)

        joblib.dump(self.pipeline, path)
        logger.info(f"Pipeline saved to: {path}")

        return path

    @classmethod
    def load(cls, path: Union[str, Path]) -> "SpamDetectionPipeline":
        """
        Load a trained pipeline from disk.

        Args:
            path: Path to saved pipeline file

        Returns:
            Loaded SpamDetectionPipeline instance
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Pipeline file not found: {path}")

        pipeline = joblib.load(path)

        # Create wrapper instance
        instance = cls()
        instance.pipeline = pipeline
        instance.is_trained = True

        logger.info(f"Pipeline loaded from: {path}")
        return instance
