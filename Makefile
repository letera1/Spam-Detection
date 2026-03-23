.PHONY: install setup train api dev test lint clean

install:
	pip install -r backend/requirements.txt
	cd frontend && npm install

setup: install
	mkdir -p data/raw data/interim data/processed data/external notebooks models logs tests docs deploy
	@echo "🔥 MLOps Environment Ready"

train:
	python backend/main.py train

api:
	python backend/main.py api

dev:
	npm run dev

test:
	pytest tests/
	cd frontend && npm test

lint:
	flake8 backend/
	cd frontend && npm run lint

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
