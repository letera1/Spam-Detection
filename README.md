# 🛡️ Advanced Spam Detection System

> **A modern, AI-powered spam detection system with a sleek web interface and advanced machine learning capabilities.**

![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-14-black?style=for-the-badge&logo=next.js&logoColor=white)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-v4-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

---

## ✨ Features

### 🧠 Backend (FastAPI + ML)

| Feature | Description |
|---------|-------------|
| **Advanced NLP Preprocessing** | URL, email, phone detection • Emoji processing • Social media patterns • Spam-specific feature extraction |
| **Machine Learning Models** | Naive Bayes • Logistic Regression • TF-IDF & Count vectorization • Hyperparameter tuning |
| **REST API Endpoints** | `/analyze` • `/predict` • `/batch` • `/upload` • `/health` • Interactive docs |

### 🎨 Frontend (Next.js 14 + Tailwind CSS v4)

| Feature | Description |
|---------|-------------|
| **Modern UI** | Real-time analysis • Detailed feature display • Prediction explanations • Dark/Light mode |
| **Analytics** | Confidence scoring • Probability breakdown • History tracking • Visual statistics & charts |
| **Responsive** | Mobile-first design • Cross-browser compatible • Accessible components |

---

## 🚀 Quick Start

### Prerequisites

```bash
Python 3.9+    # Backend
Node.js 18+    # Frontend
npm or yarn    # Package manager
```

### Backend Setup

```bash
# 1. Navigate to backend
cd backend

# 2. Install dependencies
pip install -r requirements.txt

# 3. Train the model
python main.py train           # Full training
python main.py train --quick   # Quick training (single model)

# 4. Start the API server
python main.py api
```

> 📍 **API available at:** `http://localhost:8000`  
> 📚 **Docs available at:** `http://localhost:8000/docs`

### Frontend Setup

```bash
# 1. Navigate to frontend
cd frontend

# 2. Install dependencies
npm install

# 3. Start development server
npm run dev
```

> 🌐 **Frontend available at:** `http://localhost:3000`

---

## 💻 Usage

### Web Interface

1. Navigate to `http://localhost:3000`
2. Enter a message in the text area
3. Click **"Analyze"** for spam detection results
4. View detailed analysis:
   - 🎯 Spam/Ham classification
   - 📊 Confidence score
   - 📈 Probability breakdown
   - 🔍 Detected spam indicators
   - 💡 Human-readable explanation

### API Examples

#### Single Message Analysis
```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{"text": "Congratulations! You won a free iPhone. Click here to claim!", "threshold": 0.5}'
```

#### Batch Analysis
```bash
curl -X POST "http://localhost:8000/analyze/batch" \
  -H "Content-Type: application/json" \
  -d '{"texts": ["Message 1", "Message 2"], "threshold": 0.5, "include_features": true}'
```

#### File Upload
```bash
curl -X POST "http://localhost:8000/upload/file" \
  -F "file=@messages.csv" \
  -F "threshold=0.5" \
  -F "include_features=true"
```

### CLI Commands

```bash
python main.py train           # Train all models and compare
python main.py train --quick   # Quick training (single model)
python main.py predict "msg"   # Predict single message
python main.py api             # Start API server
python main.py interactive     # Interactive mode
```

---

## 📁 Project Structure

```
Spam-Detection/
├── 📂 backend/           # ML source code and FastAPI endpoints
│   ├── 📂 api/              # FastAPI routes and controllers
│   ├── 📂 config/           # Configuration and hyperparameters
│   ├── 📂 data/             # Data loaders and text preprocessors
│   ├── 📂 inference/        # ML prediction logic
│   ├── 📂 models/           # Training pipelines and evaluators
│   ├── 📂 utils/            # Shared utilities and logging
│   └── 📄 main.py           # CLI entry point for training & serving
├── 📂 data/              # Data layer (Cookiecutter standard)
│   ├── 📂 external/         # Data from third party sources
│   ├── 📂 interim/          # Intermediate data that has been transformed
│   ├── 📂 processed/        # The final, canonical data sets for modeling
│   └── 📂 raw/              # The original, immutable data dump
├── 📂 deploy/            # Deployment and containerization files
├── 📂 docs/              # Project documentation
├── 📂 frontend/          # Next.js web application
│   ├── 📂 app/              # App router pages
│   ├── 📂 components/       # React UI components
│   └── 📂 lib/              # Frontend API clients
├── 📂 logs/              # Application and training logs
├── 📂 models/            # Serialized models and pipeline artifacts (joblib, pkl)
├── 📂 notebooks/         # Exploratory data analysis (EDA) and experimental notebooks
├── 📂 tests/             # Unit and integration tests for ML and API
├── 📄 .gitignore         # Configured for modern MLOps (Python, Node, Jupyter, Data)
├── 📄 Makefile           # Build, train, and run automation
└── 📄 README.md          # You are here!
```

---

## 🔬 Advanced Features

### Spam Feature Extraction

The system detects various spam indicators:

| Indicator | Description |
|-----------|-------------|
| 🔗 URLs | Shortened links, suspicious domains |
| 📧 Email Addresses | Potential phishing attempts |
| 📞 Phone Numbers | Contact info in spam messages |
| 💰 Currency Symbols | Money-related spam keywords |
| ❗ Excessive Punctuation | Multiple exclamation/question marks |
| 🔠 All-Caps Words | Shouting patterns |
| ⚠️ Suspicious Keywords | "Win", "Free", "Claim", "Urgent" |
| 😊 Emoji Patterns | Emotional manipulation tactics |

### Custom Training

```python
from backend.models.trainer import train_model

# Train with custom configuration
pipeline = train_model(
    vectorizer_type="tfidf",
    model_type="logistic_regression"
)

# Save model
pipeline.save("custom_model.joblib")
```

### Custom Preprocessing

```python
from backend.data.preprocessor import TextPreprocessor

preprocessor = TextPreprocessor(
    remove_stopwords=True,
    use_stemming=False,
    use_lemmatization=True,
    extract_spam_features=True,
    mark_special_tokens=True
)
```

---

## ⚙️ Configuration

### Backend Settings

Edit `backend/config/settings.py`:

| Setting | Description |
|---------|-------------|
| `MODEL_HYPERPARAMETERS` | Model-specific parameters |
| `VECTORIZER_SETTINGS` | TF-IDF / Count vectorizer config |
| `PREPROCESSING_OPTIONS` | NLP pipeline configuration |
| `TRAINING_CONFIG` | Training strategy settings |

### Frontend Settings

Create `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 🧪 Testing

```bash
# Backend tests
pytest backend/tests

# Frontend tests
npm test
```

---

## ⚡ Performance

| Metric | Target |
|--------|--------|
| Inference Time | < 100ms per message |
| Batch Processing | Up to 1000 messages |
| Memory Footprint | Optimized for low usage |
| API Design | Scalable & async-ready |

---

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| **Model Not Found** | Run `python main.py train` first |
| **API Connection Error** | Ensure API server is running • Check `.env.local` |
| **NLTK Data Missing** | Run `nltk.download('punkt_tab')`, `nltk.download('stopwords')`, `nltk.download('wordnet')` |
| **Port 8000 in Use** | Kill existing process or use `--port` flag |

---

## 📚 API Documentation

| Interface | URL |
|-----------|-----|
| Swagger UI | `http://localhost:8000/docs` |
| ReDoc | `http://localhost:8000/redoc` |

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- 📊 **SMS Spam Collection Dataset** - UCI Machine Learning Repository
- 🤖 **scikit-learn** - Machine Learning library
- ⚡ **FastAPI** - Modern Python web framework
- ⚛️ **Next.js** - React framework
- 🎨 **Tailwind CSS** - Utility-first CSS framework

---

<p align="center">
  <strong>Built with ❤️ for a spam-free world</strong>
</p>
