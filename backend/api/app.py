"""
FastAPI application for spam detection.

Provides REST API endpoints for:
- Single message prediction
- Batch prediction
- Model health check
"""

from typing import List, Optional
from contextlib import asynccontextmanager
import io
import csv

from fastapi import FastAPI, HTTPException, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from ..inference.predictor import SpamPredictor
from ..utils.logging import get_logger

logger = get_logger(__name__)


# =============================================================================
# Pydantic Models
# =============================================================================


class PredictionRequest(BaseModel):
    """Request model for single message prediction."""

    text: str = Field(..., min_length=1, max_length=10000, description="Message text to classify")
    threshold: float = Field(default=0.5, ge=0.0, le=1.0, description="Classification threshold")


class BatchPredictionRequest(BaseModel):
    """Request model for batch prediction."""

    texts: List[str] = Field(..., min_length=1, max_length=100, description="List of messages to classify")
    threshold: float = Field(default=0.5, ge=0.0, le=1.0, description="Classification threshold")


class PredictionResponse(BaseModel):
    """Response model for prediction results."""

    text: str
    label: str
    confidence: float
    probabilities: dict
    features: Optional[dict] = None
    explanation: Optional[str] = None


class BatchPredictionResponse(BaseModel):
    """Response model for batch prediction results."""

    results: List[PredictionResponse]
    total: int
    spam_count: int
    ham_count: int


class HealthResponse(BaseModel):
    """Response model for health check."""

    status: str
    model_loaded: bool
    model_path: Optional[str]


# =============================================================================
# Application State
# =============================================================================


class AppState:
    """Application state container."""

    predictor: Optional[SpamPredictor] = None


app_state = AppState()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup/shutdown."""
    # Startup
    logger.info("Starting Spam Detection API...")
    try:
        app_state.predictor = SpamPredictor()
        app_state.predictor.load()
        logger.info("Model loaded successfully")
    except FileNotFoundError as e:
        logger.error(f"Failed to load model: {e}")
        app_state.predictor = None

    yield

    # Shutdown
    logger.info("Shutting down Spam Detection API...")
    app_state.predictor = None


# =============================================================================
# FastAPI Application
# =============================================================================


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    app = FastAPI(
        title="Spam Detection API",
        description="REST API for spam/ham text classification using ML",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app


app = create_app()


# =============================================================================
# API Endpoints
# =============================================================================


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Spam Detection API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "predict": "/predict",
        "batch_predict": "/predict/batch",
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Check API and model health status."""
    model_loaded = app_state.predictor is not None and app_state.predictor._is_loaded

    return HealthResponse(
        status="healthy" if model_loaded else "degraded",
        model_loaded=model_loaded,
        model_path=str(app_state.predictor.model_path) if app_state.predictor else None,
    )


@app.post("/predict", response_model=PredictionResponse, tags=["Prediction"])
async def predict_single(request: PredictionRequest):
    """
    Classify a single message as spam or ham.

    Args:
        request: PredictionRequest with text and optional threshold

    Returns:
        PredictionResponse with classification result
    """
    if app_state.predictor is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model not loaded. Please train a model first.",
        )

    try:
        result = app_state.predictor.predict(request.text, request.threshold)
        return PredictionResponse(
            text=result.text,
            label=result.label,
            confidence=result.confidence,
            probabilities=result.to_dict()["probabilities"],
        )
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}",
        )


@app.post("/predict/batch", response_model=BatchPredictionResponse, tags=["Prediction"])
async def predict_batch(request: BatchPredictionRequest):
    """
    Classify multiple messages as spam or ham.

    Args:
        request: BatchPredictionRequest with list of texts

    Returns:
        BatchPredictionResponse with all classification results
    """
    if app_state.predictor is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model not loaded. Please train a model first.",
        )

    try:
        results = app_state.predictor.predict_batch(request.texts, request.threshold)

        spam_count = sum(1 for r in results if r.label == "spam")
        ham_count = len(results) - spam_count

        return BatchPredictionResponse(
            results=[
                PredictionResponse(
                    text=r.text,
                    label=r.label,
                    confidence=r.confidence,
                    probabilities=r.to_dict()["probabilities"],
                )
                for r in results
            ],
            total=len(results),
            spam_count=spam_count,
            ham_count=ham_count,
        )
    except Exception as e:
        logger.error(f"Batch prediction error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch prediction failed: {str(e)}",
        )


@app.get("/predict/probability", tags=["Prediction"])
async def get_spam_probability(text: str):
    """
    Get spam probability for a message without classification.

    Args:
        text: Message text to analyze

    Returns:
        Dictionary with spam probability
    """
    if app_state.predictor is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model not loaded.",
        )

    try:
        prob = app_state.predictor.get_spam_probability(text)
        return {"text": text, "spam_probability": prob}
    except Exception as e:
        logger.error(f"Probability calculation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate probability: {str(e)}",
        )


@app.post("/analyze", response_model=PredictionResponse, tags=["Analysis"])
async def analyze_message(request: PredictionRequest):
    """
    Analyze a message with detailed feature extraction and explanation.

    This endpoint provides:
    - Spam/ham classification
    - Confidence score
    - Extracted spam-indicative features
    - Human-readable explanation

    Args:
        request: PredictionRequest with text and optional threshold

    Returns:
        PredictionResponse with detailed analysis
    """
    if app_state.predictor is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model not loaded. Please train a model first.",
        )

    try:
        result = app_state.predictor.analyze(request.text, request.threshold)
        return PredictionResponse(
            text=result.text,
            label=result.label,
            confidence=result.confidence,
            probabilities=result.to_dict()["probabilities"],
            features=result.features,
            explanation=result.explanation,
        )
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}",
        )


class BatchAnalysisRequest(BaseModel):
    """Request model for batch analysis."""

    texts: List[str] = Field(..., min_length=1, max_length=1000, description="List of messages to analyze")
    threshold: float = Field(default=0.5, ge=0.0, le=1.0, description="Classification threshold")
    include_features: bool = Field(default=False, description="Include spam features in response")


class BatchAnalysisResponse(BaseModel):
    """Response model for batch analysis."""

    results: List[PredictionResponse]
    total: int
    spam_count: int
    ham_count: int
    spam_percentage: float


@app.post("/analyze/batch", response_model=BatchAnalysisResponse, tags=["Analysis"])
async def analyze_batch(request: BatchAnalysisRequest):
    """
    Analyze multiple messages with detailed feature extraction.

    Args:
        request: BatchAnalysisRequest with list of texts

    Returns:
        BatchAnalysisResponse with all classification results
    """
    if app_state.predictor is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model not loaded. Please train a model first.",
        )

    try:
        results = []
        for text in request.texts:
            result = app_state.predictor.analyze(text, request.threshold)
            if not request.include_features:
                result.features = None
            results.append(result)

        spam_count = sum(1 for r in results if r.label == "spam")
        ham_count = len(results) - spam_count

        return BatchAnalysisResponse(
            results=[
                PredictionResponse(
                    text=r.text,
                    label=r.label,
                    confidence=r.confidence,
                    probabilities=r.to_dict()["probabilities"],
                    features=r.features,
                    explanation=r.explanation,
                )
                for r in results
            ],
            total=len(results),
            spam_count=spam_count,
            ham_count=ham_count,
            spam_percentage=round((spam_count / len(results)) * 100, 2) if results else 0,
        )
    except Exception as e:
        logger.error(f"Batch analysis error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch analysis failed: {str(e)}",
        )


@app.post("/upload/file", response_model=BatchAnalysisResponse, tags=["File Upload"])
async def upload_file(
    file: UploadFile = File(..., description="CSV or TXT file containing messages"),
    threshold: float = File(default=0.5, ge=0.0, le=1.0, description="Classification threshold"),
    include_features: bool = File(default=False, description="Include spam features in response"),
):
    """
    Upload a CSV or TXT file for batch spam analysis.

    Supported formats:
    - CSV: Must have a 'text' column or use the first column
    - TXT: One message per line

    Args:
        file: Uploaded file
        threshold: Classification threshold
        include_features: Whether to include spam features

    Returns:
        BatchAnalysisResponse with all classification results
    """
    if app_state.predictor is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model not loaded. Please train a model first.",
        )

    try:
        content = await file.read()
        content_str = content.decode("utf-8")
        messages = []

        if file.filename.endswith(".csv"):
            # Parse CSV
            reader = csv.DictReader(io.StringIO(content_str))
            if "text" in reader.fieldnames:
                messages = [row["text"] for row in reader if row.get("text")]
            else:
                # Use first column
                reader = csv.reader(io.StringIO(content_str))
                messages = [row[0] for row in reader if row and row[0]]
        else:
            # Parse TXT (one message per line)
            messages = [line.strip() for line in content_str.split("\n") if line.strip()]

        if not messages:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No messages found in file",
            )

        if len(messages) > 1000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File contains too many messages (max 1000)",
            )

        # Analyze all messages
        results = []
        for text in messages:
            result = app_state.predictor.analyze(text, threshold)
            if not include_features:
                result.features = None
            results.append(result)

        spam_count = sum(1 for r in results if r.label == "spam")
        ham_count = len(results) - spam_count

        return BatchAnalysisResponse(
            results=[
                PredictionResponse(
                    text=r.text,
                    label=r.label,
                    confidence=r.confidence,
                    probabilities=r.to_dict()["probabilities"],
                    features=r.features,
                    explanation=r.explanation,
                )
                for r in results
            ],
            total=len(results),
            spam_count=spam_count,
            ham_count=ham_count,
            spam_percentage=round((spam_count / len(results)) * 100, 2) if results else 0,
        )
    except csv.Error as e:
        logger.error(f"CSV parsing error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid CSV format: {str(e)}",
        )
    except Exception as e:
        logger.error(f"File upload error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File upload failed: {str(e)}",
        )


# =============================================================================
# Main Entry Point
# =============================================================================


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.api.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
