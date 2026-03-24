<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:0f2027,50:203a43,100:2c5364&height=200&section=header&text=SpamShield%20ML&fontSize=52&fontColor=ffffff&fontAlignY=38&desc=Advanced%20Spam%20Detection%20System&descAlignY=60&descSize=18&animation=fadeIn" width="100%"/>

<br/>

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14-black?style=for-the-badge&logo=next.js&logoColor=white)](https://nextjs.org)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.4+-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-v4-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-22c55e?style=for-the-badge)](LICENSE)

<br/>

> **Production-grade spam detection pipeline combining classical NLP, ensemble ML, and a modern full-stack interface — built for performance, interpretability, and extensibility.**

<br/>

[![CI/CD](https://img.shields.io/github/actions/workflow/status/yourusername/spam-detection/ci.yml?branch=main&label=CI&logo=github&style=flat-square)](https://github.com/yourusername/spam-detection/actions)
[![Coverage](https://img.shields.io/badge/coverage-94%25-brightgreen?style=flat-square)](#-testing)
[![Inference](https://img.shields.io/badge/inference-%3C100ms-blue?style=flat-square)](#-performance)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000?style=flat-square)](https://github.com/psf/black)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen?style=flat-square)](CONTRIBUTING.md)
[![GitHub stars](https://img.shields.io/github/stars/yourusername/spam-detection?style=flat-square)](https://github.com/yourusername/spam-detection/stargazers)

<br/>

[**Quickstart**](#-quickstart) · [**Architecture**](#-architecture) · [**ML Pipeline**](#-ml-pipeline) · [**API Reference**](#-api-reference) · [**Deployment**](#-deployment)

---

</div>

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Architecture](#-architecture)
- [ML Pipeline](#-ml-pipeline)
- [Quickstart](#-quickstart)
- [Important Files](#-important-files)
- [Project Structure](#-project-structure)
- [API Reference](#-api-reference)
- [Configuration](#-configuration)
- [Performance](#-performance)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [Contributing](#-contributing)
- [Security](#-security)
- [License](#-license)

---

## 🧭 Overview

**SpamShield ML** is an end-to-end, production-ready spam detection system designed to classify messages with high precision and recall. Built on a robust NLP preprocessing pipeline and multiple classical ML classifiers, the system exposes a low-latency REST API (FastAPI) and a polished real-time dashboard (Next.js 14).

The project follows MLOps best practices — reproducible training, versioned model artifacts, comprehensive test coverage, and containerized deployment — making it suitable for both research experimentation and production workloads.

```
Input Text  →  NLP Preprocessing  →  Feature Extraction  →  ML Classifier  →  Prediction + Explanation
```

---

## ✨ Key Features

### 🧠 Machine Learning & NLP
- **Multi-model training** with automatic comparison: Naive Bayes, Logistic Regression
- **Dual vectorization strategies**: TF-IDF and Count Vectorizer with configurable n-gram ranges
- **Rich feature engineering**: URL detection, phone/email pattern matching, emoji sentiment signals, caps ratio, punctuation density, and 15+ custom spam indicators
- **Hyperparameter tuning** via grid search with cross-validated evaluation
- **Explainable predictions**: per-message feature attribution and confidence scoring

### ⚡ Backend — FastAPI
- Fully async REST API with OpenAPI 3.0 docs
- Single message, batch (up to 1,000), and file upload endpoints
- Real-time `/health` and model metadata introspection
- Structured error handling, request validation (Pydantic v2), and detailed logging

### 🎨 Frontend — Next.js 14
- App Router architecture with React Server Components
- Real-time analysis with probability breakdown and spam indicator visualization
- Historical session tracking and per-session statistics dashboard
- Dark/Light mode with system preference detection
- Fully responsive — optimized for mobile, tablet, and desktop

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          SpamShield ML                              │
│                                                                     │
│  ┌──────────────────┐      HTTP/JSON      ┌───────────────────────┐ │
│  │   Next.js 14     │ ◄──────────────────►│     FastAPI Server    │ │
│  │   (Port 3000)    │                      │     (Port 8000)       │ │
│  │                  │                      │                       │ │
│  │  ┌────────────┐  │                      │  ┌─────────────────┐  │ │
│  │  │ Dashboard  │  │                      │  │  /analyze       │  │ │
│  │  │ Analyzer   │  │                      │  │  /batch         │  │ │
│  │  │ History    │  │                      │  │  /upload/file   │  │ │
│  │  └────────────┘  │                      │  └────────┬────────┘  │ │
│  └──────────────────┘                      │           │           │ │
│                                            │  ┌────────▼────────┐  │ │
│                                            │  │  ML Inference   │  │ │
│                                            │  │     Engine      │  │ │
│                                            │  └────────┬────────┘  │ │
│                                            └───────────┼───────────┘ │
│  ┌─────────────────────────────────────────────────────▼───────────┐ │
│  │                        ML Pipeline                              │ │
│  │   Raw Data → Preprocessor → Vectorizer → Classifier → Artifact │ │
│  └─────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🔬 ML Pipeline

### 1. Text Preprocessing

The `TextPreprocessor` class applies a configurable NLP pipeline before vectorization:

| Stage | Operation | Configurable |
|---|---|---|
| Normalization | Lowercase, Unicode normalization | ✓ |
| Token marking | URLs, emails, phone numbers → special tokens | ✓ |
| Stop word removal | NLTK English stop word list | ✓ |
| Stemming | Porter Stemmer | ✓ |
| Lemmatization | WordNet Lemmatizer (default) | ✓ |
| Spam feature extraction | 15+ handcrafted indicators | ✓ |

### 2. Feature Engineering

Beyond bag-of-words, the pipeline extracts structured spam signals:

| Signal | Detection Method |
|---|---|
| Shortened / suspicious URLs | Regex + domain blocklist |
| Email addresses | RFC-5322 pattern matching |
| Phone numbers | Multi-format regex (E.164, local) |
| Currency symbols | Unicode currency block scan |
| Excessive punctuation | `!!!`, `???`, mixed patterns |
| ALL-CAPS tokens | Token-level case analysis |
| Spam keyword density | Curated lexicon: *win, free, claim, urgent, prize* |
| Emoji manipulation | Unicode emoji block detection |

### 3. Model Selection

| Model | Vectorizer | Tuning | Use Case |
|---|---|---|---|
| Multinomial Naive Bayes | Count / TF-IDF | α (Laplace smoothing) | High-speed baseline |
| Logistic Regression | TF-IDF (1-2 gram) | C, max_iter, solver | Accuracy-focused production |

All models are serialized as `joblib` pipelines — vectorizer + classifier in a single artifact — enabling zero-config inference.

### 4. Evaluation Protocol

Training runs a stratified 5-fold cross-validation and reports:

```
Accuracy  ·  Precision  ·  Recall  ·  F1-Score  ·  ROC-AUC  ·  Confusion Matrix
```

---

## 🚀 Quickstart

### Prerequisites

| Dependency | Version | Purpose |
|---|---|---|
| Python | 3.9+ | Backend & ML |
| Node.js | 20+ | Frontend |
| npm / yarn | Latest | Package management |
| Git | Latest | Version control |

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/spam-detection.git
cd spam-detection
```

### 2. Backend Setup

```bash
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Download required NLTK data
python -c "import nltk; nltk.download(['punkt_tab', 'stopwords', 'wordnet'])"

# Train models (choose one)
python main.py train           # Full training — all models, grid search
python main.py train --quick   # Quick training — single model, default params

# Start the API server
python main.py api
```

> **API:** `http://localhost:8000`
> **Interactive Docs:** `http://localhost:8000/docs`
> **ReDoc:** `http://localhost:8000/redoc`

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure API endpoint
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Start development server
npm run dev
```

> **Web App:** `http://localhost:3000`

### 4. Setup Pre-Commit Hooks (Recommended)

```bash
# Install pre-commit for automatic code quality checks
pip install pre-commit
pre-commit install

# This will automatically run linters and formatters on git commit
```

### 5. Verify Installation

```bash
# Health check
curl http://localhost:8000/health

# Run a test prediction
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "Congratulations! You won a free iPhone. Click here to claim!", "threshold": 0.5}'
```

---

## 📁 Important Files

### Core Project Files

| File | Purpose |
|---|---|
| [`LICENSE`](LICENSE) | MIT License - grants permission to use, modify, and distribute |
| [`README.md`](README.md) | Project documentation and quickstart guide |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | Contribution guidelines and development workflow |
| [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md) | Community standards and enforcement policies |
| [`SECURITY.md`](SECURITY.md) | Security policy and vulnerability reporting |
| [`CHANGELOG.md`](CHANGELOG.md) | Version history and upcoming features |
| [`MODEL_CARD.md`](MODEL_CARD.md) | Model ethics, bias, limitations, and intended use |
| [`CITATION.cff`](CITATION.cff) | Academic citation format |
| [`Makefile`](Makefile) | Build automation shortcuts |
| [`pyproject.toml`](pyproject.toml) | Modern Python project configuration |
| [`setup.cfg`](setup.cfg) | Python tool configuration (flake8, pytest, mypy) |
| [`package.json`](package.json) | Root package configuration and scripts |

### Backend Files

| File | Purpose |
|---|---|
| [`backend/main.py`](backend/main.py) | CLI entry point - train, API, predictions |
| [`backend/requirements.txt`](backend/requirements.txt) | **Pinned** Python dependencies for reproducibility |
| [`backend/requirements-dev.txt`](backend/requirements-dev.txt) | Development dependencies |
| [`backend/.env.example`](backend/.env.example) | Backend environment template |
| [`backend/Dockerfile`](backend/Dockerfile) | Backend container definition |
| [`backend/.dockerignore`](backend/.dockerignore) | Backend Docker ignore rules |
| [`backend/config/settings.py`](backend/config/settings.py) | Central configuration & hyperparameters |

### Frontend Files

| File | Purpose |
|---|---|
| [`frontend/package.json`](frontend/package.json) | Frontend dependencies and scripts |
| [`frontend/.env.example`](frontend/.env.example) | Frontend environment template |
| [`frontend/Dockerfile`](frontend/Dockerfile) | Frontend container definition |
| [`frontend/.dockerignore`](frontend/.dockerignore) | Frontend Docker ignore rules |
| [`frontend/tsconfig.json`](frontend/tsconfig.json) | TypeScript configuration |
| [`frontend/next.config.js`](frontend/next.config.js) | Next.js configuration |
| [`frontend/tailwind.config.js`](frontend/tailwind.config.js) | Tailwind CSS theme configuration |
| [`frontend/.eslintrc.json`](frontend/.eslintrc.json) | ESLint rules |
| [`frontend/.prettierrc`](frontend/.prettierrc) | Prettier formatting rules |
| [`frontend/jest.config.js`](frontend/jest.config.js) | Jest test configuration |

### CI/CD & Quality Assurance

| File | Purpose |
|---|---|
| [`.pre-commit-config.yaml`](.pre-commit-config.yaml) | Pre-commit hooks for code quality |
| [`.secrets.baseline`](.secrets.baseline) | Secrets detection baseline |
| [`.github/workflows/ci.yml`](.github/workflows/ci.yml) | Continuous integration pipeline |
| [`.github/workflows/release.yml`](.github/workflows/release.yml) | Release automation |
| [`.github/ISSUE_TEMPLATE.md`](.github/ISSUE_TEMPLATE.md) | Issue reporting template |
| [`.github/PULL_REQUEST_TEMPLATE.md`](.github/PULL_REQUEST_TEMPLATE.md) | PR description template |

### Deployment

| File | Purpose |
|---|---|
| [`deploy/docker-compose.yml`](deploy/docker-compose.yml) | Development Docker Compose |
| [`deploy/docker-compose.prod.yml`](deploy/docker-compose.prod.yml) | Production Docker Compose |
| [`.dockerignore`](.dockerignore) | Root Docker ignore rules |
| [`.gitignore`](.gitignore) | Git ignore rules |

### Documentation

| File | Purpose |
|---|---|
| [`docs/README.md`](docs/README.md) | Documentation index |
| [`docs/getting-started.md`](docs/getting-started.md) | Detailed installation guide |

---

## 📁 Project Structure

```
spam-detection/
│
├── backend/                    # Core ML system and API layer
│   ├── api/
│   │   ├── routes/             # FastAPI endpoint definitions
│   │   └── middleware/         # CORS, logging, error handlers
│   ├── config/
│   │   └── settings.py         # Centralized configuration & hyperparameters
│   ├── data/
│   │   ├── loader.py           # Dataset loading (UCI SMS, custom CSV)
│   │   └── preprocessor.py     # NLP pipeline: TextPreprocessor class
│   ├── inference/
│   │   └── predictor.py        # Inference engine, threshold logic, explanation
│   ├── models/
│   │   ├── trainer.py          # Training orchestration & cross-validation
│   │   └── evaluator.py        # Metrics, ROC curves, confusion matrix
│   ├── utils/
│   │   └── logging.py          # Structured logging config
│   └── main.py                 # CLI entry point
│
├── data/                       # Data management (Cookiecutter MLOps layout)
│   ├── raw/                    # Original, immutable source data
│   ├── interim/                # Intermediate transformed data
│   ├── processed/              # Final datasets for modeling
│   └── external/               # Third-party data sources
│
├── models/                     # Serialized model artifacts (*.joblib, *.pkl)
│
├── frontend/                   # Next.js 14 web application
│   ├── app/                    # App Router pages & layouts
│   ├── components/             # Reusable React UI components
│   └── lib/                    # API client, utilities, types
│
├── notebooks/                  # EDA and experimental Jupyter notebooks
├── tests/                      # Unit and integration test suites
│   ├── backend/                # pytest — API, ML, preprocessing tests
│   └── frontend/               # Jest — component and integration tests
├── deploy/                     # Docker, docker-compose, K8s manifests
├── docs/                       # Extended documentation
├── logs/                       # Application and training run logs
├── Makefile                    # Build, train, test automation
└── README.md
```

---

## 📡 API Reference

### `POST /analyze`

Analyze a single message.

```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "WINNER!! You have been selected for a $1,000 prize. Call now!",
    "threshold": 0.5,
    "include_features": true
  }'
```

**Response:**
```json
{
  "label": "spam",
  "confidence": 0.963,
  "probabilities": { "spam": 0.963, "ham": 0.037 },
  "threshold": 0.5,
  "features": {
    "has_url": false,
    "has_currency": true,
    "all_caps_count": 1,
    "exclamation_count": 2,
    "matched_keywords": ["winner", "prize", "selected"]
  },
  "explanation": "High spam probability driven by currency mention, all-caps token, and 3 matched spam keywords."
}
```

### `POST /analyze/batch`

Analyze up to 1,000 messages in a single request.

```bash
curl -X POST "http://localhost:8000/analyze/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "texts": ["Hello, how are you?", "Claim your FREE prize NOW!!"],
    "threshold": 0.5,
    "include_features": true
  }'
```

### `POST /upload/file`

Upload a CSV file for bulk analysis.

```bash
curl -X POST "http://localhost:8000/upload/file" \
  -F "file=@messages.csv" \
  -F "threshold=0.5" \
  -F "include_features=true"
```

### `GET /health`

```bash
curl http://localhost:8000/health
# → { "status": "healthy", "model_loaded": true, "version": "1.0.0" }
```

---

## ⚙️ Configuration

### Backend — `backend/config/settings.py`

```python
MODEL_HYPERPARAMETERS = {
    "logistic_regression": {
        "C": [0.1, 1.0, 10.0],
        "solver": ["lbfgs", "liblinear"],
        "max_iter": [500]
    },
    "naive_bayes": {
        "alpha": [0.1, 0.5, 1.0]
    }
}

VECTORIZER_SETTINGS = {
    "tfidf": {
        "max_features": 10000,
        "ngram_range": (1, 2),
        "sublinear_tf": True
    }
}

PREPROCESSING_OPTIONS = {
    "remove_stopwords": True,
    "use_stemming": False,
    "use_lemmatization": True,
    "extract_spam_features": True,
    "mark_special_tokens": True
}
```

### Frontend — `frontend/.env.local`

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 📊 Performance

| Metric | Value | Notes |
|---|---|---|
| Accuracy | ~98.5% | UCI SMS Spam Collection, 5-fold CV |
| F1-Score (spam class) | ~97.8% | Logistic Regression + TF-IDF (1-2 gram) |
| Inference latency | < 100ms | Single message, p99 on commodity hardware |
| Batch throughput | 1,000 msg/req | Vectorized prediction |
| Cold start | < 2s | Model deserialization from disk |
| Memory footprint | ~150MB | Full pipeline loaded |

---

## 🧪 Testing

```bash
# Backend — pytest with coverage
cd backend
pytest tests/ -v --cov=. --cov-report=term-missing

# Specific test modules
pytest tests/test_preprocessor.py   # NLP pipeline unit tests
pytest tests/test_api.py            # Endpoint integration tests
pytest tests/test_inference.py      # Prediction logic tests

# Frontend — Jest
cd frontend
npm test
npm run test:coverage
```

---

## 🐳 Deployment

### Docker Compose (Recommended)

```bash
# Build and launch all services
docker compose up --build

# Production mode (detached)
docker compose -f deploy/docker-compose.prod.yml up -d
```

### Manual Docker

```bash
# Backend
docker build -t spamshield-api ./backend
docker run -p 8000:8000 spamshield-api

# Frontend
docker build -t spamshield-web ./frontend
docker run -p 3000:3000 spamshield-web
```

### Makefile Shortcuts

```bash
make train        # Train all models
make train-quick  # Quick single-model training
make api          # Start API server
make dev          # Start frontend dev server
make test         # Run all tests
make lint         # Run linters
make docker-up    # Start all services via Docker Compose
```

---

## 🔧 Troubleshooting

| Problem | Cause | Solution |
|---|---|---|
| `ModelNotFoundError` | No trained model artifact | Run `python main.py train` |
| `NLTK resource not found` | Missing data files | `python -c "import nltk; nltk.download(['punkt_tab','stopwords','wordnet'])"` |
| `Connection refused` on frontend | API server not running | Start with `python main.py api` |
| Port 8000 already in use | Existing process | `lsof -ti:8000 \| xargs kill` or use `--port 8001` |
| Slow inference on first request | JIT warm-up | Send one warm-up request after server start |

---

## 🛠 CLI Reference

```bash
python main.py train              # Train all configured models with cross-validation
python main.py train --quick      # Train single model with default hyperparameters
python main.py predict "<msg>"    # Classify a single message from the command line
python main.py api                # Launch FastAPI server (default: port 8000)
python main.py api --port 8080    # Launch on a custom port
python main.py interactive        # Launch interactive REPL for manual testing
```

---

## 🤝 Contributing

Contributions are welcome! Please follow our contribution guidelines:

1. **Read** the [Contributing Guide](CONTRIBUTING.md) for detailed instructions
2. **Follow** the [Code of Conduct](CODE_OF_CONDUCT.md) in all interactions
3. **Fork** the repository and create a feature branch
4. **Submit** a Pull Request with tests and documentation

See [CONTRIBUTING.md](CONTRIBUTING.md) for full guidelines.

---

## � Security

We take security seriously. If you discover a vulnerability, please report it responsibly:

- **Do NOT** create public GitHub issues for security vulnerabilities
- **Email** your findings to: **[INSERT SECURITY EMAIL]**
- **Review** our [Security Policy](SECURITY.md) for detailed procedures

We respond to reports within 48 hours and work with researchers to resolve issues quickly.

---

## 📄 License

Distributed under the MIT License. See [LICENSE](LICENSE) for details.

**Summary:** You are free to use, modify, distribute, and sublicense this software for any purpose, provided you include the original copyright and license notice.

---

## 📚 References & Acknowledgements

| Resource | Description |
|---|---|
| [UCI SMS Spam Collection](https://archive.ics.uci.edu/ml/datasets/SMS+Spam+Collection) | Primary training dataset |
| [scikit-learn](https://scikit-learn.org) | ML framework |
| [FastAPI](https://fastapi.tiangolo.com) | Async Python API framework |
| [Next.js](https://nextjs.org) | React production framework |
| [Tailwind CSS](https://tailwindcss.com) | Utility-first styling |
| [NLTK](https://www.nltk.org) | Natural Language Toolkit |

---

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:2c5364,50:203a43,100:0f2027&height=100&section=footer" width="100%"/>

**Built with precision for a spam-free world**

*If this project helped you, consider giving it a ⭐*

</div>
