.PHONY: help install install-dev run dev test lint format clean docker-build docker-up docker-down

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install production dependencies
	pip install -r requirements.txt

install-dev: ## Install development dependencies
	pip install -r requirements.txt -r requirements-dev.txt

run: ## Run the application
	uvicorn main:app --host 0.0.0.0 --port 8000

dev: ## Run the application in development mode with auto-reload
	uvicorn main:app --host 0.0.0.0 --port 8000 --reload

test: ## Run tests with coverage
	pytest

test-verbose: ## Run tests with verbose output
	pytest -vv

lint: ## Run linters
	ruff check app/ main.py
	mypy app/ main.py

format: ## Format code with black
	black app/ main.py
	ruff check --fix app/ main.py

clean: ## Clean up cache files
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.coverage" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .ruff_cache
	rm -rf .mypy_cache

docker-build: ## Build Docker image
	docker-compose build

docker-up: ## Start Docker containers
	docker-compose up -d

docker-down: ## Stop Docker containers
	docker-compose down

docker-logs: ## Show Docker logs
	docker-compose logs -f

check: lint test ## Run all checks (lint + test)

