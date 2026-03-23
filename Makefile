.PHONY: help install setup train train-quick api dev test lint format clean docker-up docker-down docker-build

help:
	@echo "SpamShield ML - Available Commands"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make install      - Install all dependencies (backend + frontend)"
	@echo "  make setup        - Create directory structure and install dependencies"
	@echo ""
	@echo "Development:"
	@echo "  make dev          - Start both backend and frontend in development mode"
	@echo "  make api          - Start the FastAPI backend server"
	@echo "  make train        - Train all models with cross-validation"
	@echo "  make train-quick  - Quick training with single model"
	@echo ""
	@echo "Testing & Quality:"
	@echo "  make test         - Run all tests (backend + frontend)"
	@echo "  make test-backend - Run backend tests with coverage"
	@echo "  make test-frontend- Run frontend tests"
	@echo "  make lint         - Run linters (flake8, black, eslint)"
	@echo "  make format       - Format code with black and prettier"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-up    - Start all services with Docker Compose"
	@echo "  make docker-down  - Stop all Docker services"
	@echo "  make docker-build - Build Docker images"
	@echo "  make docker-prod  - Start production Docker Compose"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean        - Remove build artifacts and cache"

install:
	pip install -r backend/requirements.txt
	cd frontend && npm install

setup: install
	mkdir -p data/raw data/interim data/processed data/external notebooks models logs tests docs deploy
	touch data/raw/.gitkeep data/interim/.gitkeep data/processed/.gitkeep data/external/.gitkeep
	touch models/.gitkeep logs/.gitkeep
	@echo "🔥 MLOps Environment Ready"

train:
	python backend/main.py train

train-quick:
	python backend/main.py train --quick

api:
	python backend/main.py api

dev:
	npm run concurrently -D -- "npm run start:backend" "npm run start:frontend"

test: test-backend test-frontend

test-backend:
	cd backend && pytest tests/ -v --cov=. --cov-report=term-missing

test-frontend:
	cd frontend && npm test

lint:
	cd backend && flake8 . --count --max-line-length=88 --max-complexity=10
	cd backend && black --check .
	cd frontend && npm run lint

format:
	cd backend && black .
	cd frontend && npm run format

docker-up:
	docker compose -f deploy/docker-compose.yml up --build

docker-down:
	docker compose -f deploy/docker-compose.yml down

docker-build:
	docker compose -f deploy/docker-compose.yml build

docker-prod:
	docker compose -f deploy/docker-compose.prod.yml up -d

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -exec rm -rf {} +
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
	find . -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/ dist/ .eggs/
	cd frontend && npm run clean 2>/dev/null || true
	@echo "✨ Cleanup complete"

