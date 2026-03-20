# Spam Detection System

A production-ready, enterprise-grade spam/ham text classification system built with clean architecture, modularity, and scalability in mind.

## 🏗️ Project Structure

```
Spam-Detection/
├── backend/                    # Main package
│   ├── __init__.py             # Package initialization & exports
│   │
│   ├── config/                 # Configuration management
│   │   ├── __init__.py
│   │   ├── settings.py         # Settings, paths, dataclasses
│   │   └── hyperparameters.py  # Hyperparameter grids & presets
│   │
│   ├── data/                   # Data loading & preprocessing
│   │   ├── __init__.py
│   │   ├── loader.py           # DataLoader, dataset loading
│   │   └── preprocessor.py     # TextPreprocessor, transformations
│   │
│   ├── models/                 # Model definitions & training
│   │   ├── __init__.py
│   │   ├── pipeline.py         # SpamDetectionPipeline, builder
│   │   ├── trainer.py          # ModelTrainer, training orchestration
│   │   └── evaluator.py        # ModelEvaluator, metrics & analysis
│   │
│   ├── inference/              # Prediction & serving
│   │   ├── __init__.py
│   │   ├── predictor.py        # SpamPredictor, PredictionResult
│   │   └── batch_predictor.py  # BatchPredictor for high-volume
│   │
│   ├── api/                    # REST API layer
│   │   ├── __init__.py
│   │   └── app.py              # FastAPI application
│   │
│   ├── scripts/                # Executable scripts
│   │   ├── __init__.py
│   │   └── train.py            # Training CLI script
│   │
│   └── utils/                  # Utilities
│       ├── __init__.py
│       └── logging.py          # Logging configuration
│
├── models/                     # Saved model artifacts
├── data/                       # Dataset storage
├── main.py                     # CLI entry point
├── requirements.txt            # Dependencies
└── README.md                   # Documentation
```

## ✨ Features

- **Clean Architecture**: Separation of concerns with dedicated packages for config, data, models, inference, and API
- **Multiple Models**: Naive Bayes and Logistic Regression with hyperparameter tuning via GridSearchCV
- **Feature Extraction**: CountVectorizer and TF-IDF with configurable parameters
- **Reusable Pipelines**: sklearn Pipeline encapsulating preprocessing → vectorization → classification
- **REST API**: FastAPI-based API with Swagger docs, batch prediction, and health checks
- **Comprehensive Evaluation**: Precision, recall, F1, confusion matrix, and error analysis
- **Production Ready**: Logging, error handling, type hints, and documentation

## 🚀 Quick Start

### Installation

```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# NLTK data downloads automatically on first run
```

### Training

```bash
# Train all model combinations and save the best
python -m main train

# Quick training (single best configuration)
python -m main train --quick

# Train specific model
python -m backend.scripts.train --model logistic_regression --vectorizer tfidf
```

### Inference

```bash
# Command line prediction
python -m main predict "Congratulations! You've won a $1000 gift card!"

# Interactive session
python -m main interactive

# Start REST API
python -m main api
```

## 📦 Programmatic Usage

### Training

```python
from backend.models.trainer import ModelTrainer, compare_models

# Compare all models
results = compare_models()
print(f"Best F1: {results['best_result']['test_metrics']['f1']:.4f}")

# Train specific configuration
from backend.models.trainer import train_model
pipeline = train_model(model_type="logistic_regression", vectorizer_type="tfidf")
pipeline.save()
```

### Inference

```python
from backend.inference.predictor import SpamPredictor

# Load and predict
predictor = SpamPredictor()
predictor.load()

result = predictor.predict("Win money now!")
print(f"Label: {result.label}, Confidence: {result.confidence:.2%}")

# Batch prediction
results = predictor.predict_batch(["Message 1", "Message 2"])
for r in results:
    print(f"{r.text[:30]}... -> {r.label}")

# Quick functions
from backend.inference.predictor import predict_message
result = predict_message("Claim your prize!")
```

### Custom Configuration

```python
from backend.config.settings import Settings, PreprocessorConfig, VectorizerConfig

# Custom preprocessor
preprocessor_cfg = PreprocessorConfig(
    remove_stopwords=True,
    use_stemming=True,
    min_length=3,
)

# Custom vectorizer
vectorizer_cfg = VectorizerConfig(
    type="tfidf",
    max_features=10000,
    ngram_range=(1, 3),
)

settings = Settings(preprocessor=preprocessor_cfg, vectorizer=vectorizer_cfg)
```

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information |
| `/health` | GET | Health check |
| `/predict` | POST | Single message prediction |
| `/predict/batch` | POST | Batch prediction (up to 100 messages) |
| `/predict/probability` | GET | Get spam probability |
| `/docs` | GET | Interactive Swagger docs |

### API Examples

```bash
# Single prediction
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"text": "Free entry to win FA Cup tickets"}'

# Batch prediction
curl -X POST "http://localhost:8000/predict/batch" \
  -H "Content-Type: application/json" \
  -d '{"texts": ["Hello there", "Win money now!", "Meeting at 3pm"]}'

# Health check
curl "http://localhost:8000/health"
```

## 📊 Model Comparison

The system trains and compares 4 combinations:

| Vectorizer | Model | Characteristics |
|------------|-------|-----------------|
| CountVectorizer | Naive Bayes | Fast, good baseline |
| CountVectorizer | Logistic Regression | Linear with count features |
| TF-IDF | Naive Bayes | Weighted features with NB |
| TF-IDF | Logistic Regression | **Best overall performance** |

### Evaluation Metrics

- **Precision**: Of all predicted spam, how many were actually spam?
- **Recall**: Of all actual spam, how many were correctly identified?
- **F1 Score**: Harmonic mean of precision and recall

### Error Analysis

| Error Type | Description | Business Impact |
|------------|-------------|-----------------|
| **False Positive** | Ham → Spam | User misses important messages |
| **False Negative** | Spam → Ham | User receives unwanted messages |

For spam detection, minimizing **False Negatives** is typically prioritized, but False Positives should be kept very low.

## ⚙️ Configuration

### Presets (`backend/config/hyperparameters.py`)

```python
from backend.config.hyperparameters import get_preset_config

# Quick training (minimal features, no grid search)
quick_cfg = get_preset_config("quick")

# Standard training (balanced)
standard_cfg = get_preset_config("standard")

# Thorough training (extensive features, 10-fold CV)
thorough_cfg = get_preset_config("thorough")
```

### Hyperparameter Grids

```python
HYPERPARAM_GRIDS = {
    "naive_bayes": {
        "classifier__alpha": [0.1, 0.5, 1.0, 1.5, 2.0],
    },
    "logistic_regression": {
        "classifier__C": [0.01, 0.1, 1.0, 10.0, 100.0],
        "classifier__max_iter": [500, 1000, 1500, 2000],
    },
}
```

## 📁 Dataset

Uses the **SMS Spam Collection Dataset**:
- 5,572 SMS messages labeled as ham/spam
- Automatically downloaded from GitHub
- ~86.6% ham, ~13.4% spam (imbalanced)

### Custom Dataset Format

```csv
text,label
"Hello there, how are you?",ham
"Win money now! Click here!",spam
```

## 🧪 Testing

```bash
# Run tests (when tests are added)
pytest tests/ -v --cov=backend

# Type checking
mypy backend/
```

## 📝 Code Quality

```bash
# Format code
black backend/

# Lint code
flake8 backend/

# Type checking
mypy backend/
```

## 🔒 Security Notes

- Model files are loaded with `joblib` - only load trusted models
- API has no authentication by default - add middleware for production
- Input validation via Pydantic models prevents injection attacks

## 📄 License

MIT License
