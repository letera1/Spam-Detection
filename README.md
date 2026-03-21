# Advanced Spam Detection System

A modern, AI-powered spam detection system with a sleek web interface and advanced ML capabilities.

## Features

### Backend (FastAPI + ML)
- **Advanced NLP Preprocessing**
  - URL, email, and phone number detection
  - Emoji and emoticon processing
  - Social media pattern handling (mentions, hashtags)
  - Spam-specific feature extraction
  - Stopword removal, stemming, and lemmatization

- **Machine Learning Models**
  - Multiple model support (Naive Bayes, Logistic Regression)
  - TF-IDF and Count vectorization
  - Hyperparameter tuning with grid search
  - Model comparison and selection

- **REST API Endpoints**
  - `/analyze` - Detailed message analysis with explanations
  - `/predict` - Quick spam/ham classification
  - `/analyze/batch` - Batch message analysis
  - `/upload/file` - CSV/TXT file upload for bulk analysis
  - `/health` - Model and API health check
  - `/docs` - Interactive API documentation

### Frontend (Next.js 14 + Tailwind CSS v4)
- **Modern UI Components**
  - Real-time spam analysis
  - Detailed feature extraction display
  - Prediction explanations
  - Analysis history with localStorage persistence
  - Statistics dashboard
  - Dark/Light mode toggle
  - Responsive design

- **User Features**
  - Instant spam/ham classification
  - Confidence scoring
  - Probability breakdown
  - Detected spam indicators
  - Historical analysis tracking
  - Visual statistics and charts

## Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- npm or yarn

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Train the model:
```bash
python main.py train
```

For quick training (single best model):
```bash
python main.py train --quick
```

4. Start the API server:
```bash
python main.py api
```

The API will be available at `http://localhost:8000`
API documentation at `http://localhost:8000/docs`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Usage

### Web Interface

1. Open your browser and navigate to `http://localhost:3000`
2. Enter a message in the text area
3. Click "Analyze" to get spam detection results
4. View detailed analysis including:
   - Spam/Ham classification
   - Confidence score
   - Probability breakdown
   - Detected spam indicators
   - Human-readable explanation

### API Usage

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

### CLI Usage

```bash
# Train all models and compare
python main.py train

# Quick training (single model)
python main.py train --quick

# Predict single message
python main.py predict "Your message here"

# Start API server
python main.py api

# Interactive mode
python main.py interactive
```

## Project Structure

```
Spam-Detection/
├── backend/
│   ├── api/           # FastAPI endpoints
│   ├── config/        # Configuration and settings
│   ├── data/          # Data loading and preprocessing
│   ├── inference/     # Prediction and analysis
│   ├── models/        # ML model training and evaluation
│   ├── utils/         # Utility functions
│   └── main.py        # CLI entry point
├── frontend/
│   ├── app/           # Next.js app router pages
│   ├── components/    # React components
│   ├── lib/           # Utilities and API client
│   └── public/        # Static assets
└── models/            # Trained model files (auto-created)
```

## Advanced Features

### Spam Feature Extraction
The system detects various spam indicators:
- URLs and shortened links
- Email addresses
- Phone numbers
- Money/currency symbols
- Excessive punctuation
- All-caps words (shouting)
- Suspicious keywords
- Emoji usage patterns

### Model Training Options

```python
# Custom training with specific model
from backend.models.trainer import train_model

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

## API Documentation

Interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Configuration

### Backend Settings
Edit `backend/config/settings.py` to customize:
- Model hyperparameters
- Vectorizer settings
- Preprocessing options
- Training configuration

### Frontend Settings
Edit `frontend/.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Testing

### Backend Tests
```bash
pytest backend/tests
```

### Frontend Tests
```bash
npm test
```

## Performance

The system is optimized for:
- Fast inference (< 100ms per message)
- Batch processing (up to 1000 messages)
- Low memory footprint
- Scalable API design

## Troubleshooting

### Model Not Found
```bash
# Train a model first
python main.py train
```

### API Connection Error
```bash
# Ensure the API server is running
python main.py api

# Check frontend .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### NLTK Data Download
```python
import nltk
nltk.download('punkt_tab')
nltk.download('stopwords')
nltk.download('wordnet')
```

## License

MIT License - See LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

- SMS Spam Collection Dataset (UCI)
- scikit-learn
- FastAPI
- Next.js
- Tailwind CSS
