
.PHONY: install train api dev setup test clean

install:
pip install -r backend/requirements.txt
cd frontend && npm install

setup: install
mkdir -p data/raw data/processed notebooks/experiments
@echo "🔥 MLOps Environment Ready"

train:
python backend/main.py train

api:
python backend/main.py api

dev:
npm run dev

clean:
find . -type d -name "__pycache__" -exec rm -rf {} +

