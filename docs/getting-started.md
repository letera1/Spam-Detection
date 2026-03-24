# Getting Started with SpamShield ML

This guide will help you get up and running with SpamShield ML in minutes.

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

| Tool | Version | Purpose | Download |
|------|---------|---------|----------|
| Python | 3.9+ | Backend & ML | [python.org](https://www.python.org/downloads/) |
| Node.js | 20+ | Frontend | [nodejs.org](https://nodejs.org/) |
| Git | Latest | Version control | [git-scm.com](https://git-scm.com/) |
| pip | 21.0+ | Python packages | Included with Python |
| npm | 9.0+ | Node packages | Included with Node.js |

### Verify Installation

```bash
# Check Python version
python --version  # Should be 3.9 or higher

# Check Node.js version
node --version  # Should be 18 or higher

# Check npm version
npm --version  # Should be 9 or higher

# Check Git version
git --version
```

---

## 🚀 Quick Installation

### Option 1: Using Make (Recommended for Linux/Mac)

```bash
# Clone the repository
git clone https://github.com/yourusername/spam-detection.git
cd spam-detection

# Setup everything (install dependencies + create directories)
make setup

# Download NLTK data
python -c "import nltk; nltk.download(['punkt_tab', 'stopwords', 'wordnet'])"

# Train a model (required before using the API)
make train-quick

# Start both backend and frontend
make dev
```

### Option 2: Manual Installation (All Platforms)

#### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/spam-detection.git
cd spam-detection
```

#### Step 2: Install Backend Dependencies

```bash
cd backend

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Step 3: Install Frontend Dependencies

```bash
cd ../frontend
npm install
```

#### Step 4: Download NLTK Data

```bash
cd ..
python -c "import nltk; nltk.download(['punkt_tab', 'stopwords', 'wordnet'])"
```

#### Step 5: Train a Model

```bash
cd backend
python main.py train-quick
```

#### Step 6: Configure Environment

```bash
# Backend (optional - defaults work for local development)
cd backend
cp .env.example .env

# Frontend
cd ../frontend
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
```

#### Step 7: Start the Application

**Terminal 1 - Backend:**
```bash
cd backend
python main.py api
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

---

## ✅ Verify Installation

### 1. Check Backend Health

Open your browser or use curl:

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "version": "1.0.0"
}
```

### 2. Check Frontend

Open your browser to: **http://localhost:3000**

You should see the SpamShield ML dashboard.

### 3. Test a Prediction

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "Congratulations! You won a free iPhone. Click here to claim!", "threshold": 0.5}'
```

Expected response:
```json
{
  "label": "spam",
  "confidence": 0.96,
  "probabilities": {
    "spam": 0.96,
    "ham": 0.04
  },
  "threshold": 0.5,
  "features": {
    "has_currency": true,
    "all_caps_count": 1,
    "exclamation_count": 2,
    "matched_keywords": ["congratulations", "won", "free", "claim"]
  },
  "explanation": "High spam probability driven by currency mention, all-caps token, and 4 matched spam keywords."
}
```

---

## 📁 Project Structure Overview

```
spam-detection/
├── backend/           # FastAPI server & ML pipeline
│   ├── api/          # REST endpoints
│   ├── config/       # Configuration
│   ├── data/         # Data loading & preprocessing
│   ├── inference/    # Prediction engine
│   ├── models/       # Training & evaluation
│   └── main.py       # Entry point
├── frontend/          # Next.js web application
│   ├── app/          # Pages & layouts
│   ├── components/   # React components
│   └── lib/          # Utilities & API client
├── data/             # Data directories (MLOps pattern)
├── models/           # Trained model artifacts
├── deploy/           # Docker & deployment configs
└── docs/             # Documentation
```

---

## 🎯 Next Steps

### Learn More

- [Architecture Overview](README.md#-architecture) - Understand system design
- [ML Pipeline Guide](README.md#-ml-pipeline) - How the ML works
- [API Reference](README.md#-api-reference) - Available endpoints
- [Configuration](README.md#-configuration) - Customize settings

### Development

- [Contributing Guide](CONTRIBUTING.md) - How to contribute
- [Testing](README.md#-testing) - Run tests
- [Code Quality](CONTRIBUTING.md#-coding-standards) - Standards & linting

### Deployment

- [Docker Deployment](README.md#-deployment) - Container deployment
- [Production Guide](docs/deployment.md) - Production best practices

---

## 🛠 Common Issues & Solutions

### Issue: ModuleNotFoundError

**Solution:** Ensure virtual environment is activated and dependencies are installed:
```bash
cd backend
pip install -r requirements.txt
```

### Issue: NLTK Data Not Found

**Solution:** Download required NLTK data:
```bash
python -c "import nltk; nltk.download(['punkt_tab', 'stopwords', 'wordnet'])"
```

### Issue: Model Not Found

**Solution:** Train a model first:
```bash
cd backend
python main.py train-quick
```

### Issue: Port Already in Use

**Solution:** Change the port:
```bash
# Backend
python main.py api --port 8001

# Frontend (in frontend/.env.local)
NEXT_PUBLIC_API_URL=http://localhost:8001
```

### Issue: Frontend Can't Connect to Backend

**Solution:** Verify backend is running and `.env.local` is configured:
```bash
# Check backend
curl http://localhost:8000/health

# Update frontend config
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > frontend/.env.local
```

---

## 📞 Getting Help

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/yourusername/spam-detection/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/spam-detection/discussions)

---

## 🎉 You're Ready!

You now have SpamShield ML running locally. Start analyzing messages, explore the codebase, or contribute to the project!

For more detailed guides, see the [docs/](docs/) directory.
