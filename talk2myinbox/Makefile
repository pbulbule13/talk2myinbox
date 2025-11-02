# Makefile for talk2myinbox
# Common development and testing commands

.PHONY: help install test test-unit test-integration test-e2e test-all test-fast test-smoke clean coverage lint format check run docker-build docker-run

# Default target
.DEFAULT_GOAL := help

# Variables
PYTHON := python
PIP := pip
PYTEST := pytest
BACKEND_DIR := backend
TESTS_DIR := $(BACKEND_DIR)/tests

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)talk2myinbox - Available Commands$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""

install: ## Install all dependencies
	@echo "$(BLUE)Installing dependencies...$(NC)"
	$(PIP) install -r requirements.txt
	$(PIP) install pytest pytest-asyncio pytest-cov pytest-xdist pytest-timeout
	@echo "$(GREEN)✓ Dependencies installed$(NC)"

install-dev: ## Install development dependencies
	@echo "$(BLUE)Installing development dependencies...$(NC)"
	$(PIP) install -r requirements.txt
	$(PIP) install pytest pytest-asyncio pytest-cov pytest-xdist pytest-timeout
	$(PIP) install black isort flake8 pylint mypy bandit safety
	@echo "$(GREEN)✓ Development dependencies installed$(NC)"

test: test-all ## Run all tests (alias for test-all)

test-unit: ## Run unit tests only
	@echo "$(BLUE)Running unit tests...$(NC)"
	cd $(BACKEND_DIR) && $(PYTEST) $(TESTS_DIR)/unit/ -v -m "unit" --cov=voice_agent --cov-report=term-missing

test-integration: ## Run integration tests only
	@echo "$(BLUE)Running integration tests...$(NC)"
	cd $(BACKEND_DIR) && $(PYTEST) $(TESTS_DIR)/integration/ -v -m "integration" --cov=voice_agent

test-e2e: ## Run end-to-end tests only
	@echo "$(BLUE)Running E2E tests...$(NC)"
	cd $(BACKEND_DIR) && $(PYTEST) $(TESTS_DIR)/e2e/ -v -m "e2e"

test-all: ## Run all test suites
	@echo "$(BLUE)Running all test suites...$(NC)"
	cd $(BACKEND_DIR) && $(PYTEST) $(TESTS_DIR)/ -v \
		--cov=voice_agent \
		--cov-report=html:$(TESTS_DIR)/coverage/html \
		--cov-report=term-missing

test-fast: ## Run fast tests only (skip slow tests)
	@echo "$(BLUE)Running fast tests...$(NC)"
	cd $(BACKEND_DIR) && $(PYTEST) $(TESTS_DIR)/unit/ -v -m "unit and not slow"

test-smoke: ## Run smoke tests (critical paths)
	@echo "$(BLUE)Running smoke tests...$(NC)"
	cd $(BACKEND_DIR) && $(PYTEST) $(TESTS_DIR)/ -v -m "smoke"

test-watch: ## Run tests in watch mode
	@echo "$(BLUE)Running tests in watch mode...$(NC)"
	cd $(BACKEND_DIR) && $(PYTEST) $(TESTS_DIR)/ -v --looponfail

coverage: ## Generate coverage report
	@echo "$(BLUE)Generating coverage report...$(NC)"
	cd $(BACKEND_DIR) && $(PYTEST) $(TESTS_DIR)/ --cov=voice_agent --cov-report=html
	@echo "$(GREEN)✓ Coverage report generated at: backend/tests/coverage/html/index.html$(NC)"

lint: ## Run linting checks
	@echo "$(BLUE)Running linting checks...$(NC)"
	flake8 $(BACKEND_DIR)/voice_agent || true
	pylint $(BACKEND_DIR)/voice_agent --exit-zero || true
	@echo "$(GREEN)✓ Linting complete$(NC)"

format: ## Format code with Black and isort
	@echo "$(BLUE)Formatting code...$(NC)"
	black $(BACKEND_DIR)/
	isort $(BACKEND_DIR)/
	@echo "$(GREEN)✓ Code formatted$(NC)"

format-check: ## Check code formatting without making changes
	@echo "$(BLUE)Checking code formatting...$(NC)"
	black --check $(BACKEND_DIR)/
	isort --check-only $(BACKEND_DIR)/

type-check: ## Run type checking with mypy
	@echo "$(BLUE)Running type checks...$(NC)"
	mypy $(BACKEND_DIR)/voice_agent --ignore-missing-imports || true

security-check: ## Run security checks
	@echo "$(BLUE)Running security checks...$(NC)"
	bandit -r $(BACKEND_DIR)/voice_agent || true
	safety check || true
	@echo "$(GREEN)✓ Security check complete$(NC)"

check: lint type-check security-check ## Run all code quality checks

clean: ## Clean generated files
	@echo "$(BLUE)Cleaning generated files...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	rm -rf $(BACKEND_DIR)/tests/coverage/ 2>/dev/null || true
	rm -rf $(BACKEND_DIR)/tests/logs/ 2>/dev/null || true
	rm -rf htmlcov/ .coverage 2>/dev/null || true
	@echo "$(GREEN)✓ Cleanup complete$(NC)"

run: ## Run the application
	@echo "$(BLUE)Starting application...$(NC)"
	cd $(BACKEND_DIR) && $(PYTHON) server.py

run-dev: ## Run the application in development mode
	@echo "$(BLUE)Starting application in development mode...$(NC)"
	cd $(BACKEND_DIR) && ENV=development $(PYTHON) server.py

docker-build: ## Build Docker image
	@echo "$(BLUE)Building Docker image...$(NC)"
	docker build -t talk2myinbox:latest -f infrastructure/docker/Dockerfile.backend .
	@echo "$(GREEN)✓ Docker image built$(NC)"

docker-run: ## Run Docker container
	@echo "$(BLUE)Running Docker container...$(NC)"
	docker run -p 8000:8000 --env-file .env talk2myinbox:latest

docker-compose-up: ## Start all services with docker-compose
	@echo "$(BLUE)Starting services with docker-compose...$(NC)"
	docker-compose -f infrastructure/docker/docker-compose.yml up

docker-compose-down: ## Stop all services
	@echo "$(BLUE)Stopping services...$(NC)"
	docker-compose -f infrastructure/docker/docker-compose.yml down

setup: install ## Initial project setup
	@echo "$(BLUE)Setting up project...$(NC)"
	mkdir -p config/credentials
	mkdir -p backend/tests/logs
	mkdir -p backend/tests/coverage
	[ ! -f .env ] && cp .env.example .env || true
	@echo "$(GREEN)✓ Project setup complete$(NC)"
	@echo "$(YELLOW)Remember to configure your .env file$(NC)"

ci: format-check lint type-check test-all ## Run CI checks locally

# Development workflow targets
dev-test: format lint test-fast ## Quick dev check (format, lint, fast tests)

full-check: clean format check test-all coverage ## Full check before commit

# Release targets
pre-release: full-check ## Run full check before release
	@echo "$(GREEN)✓ Pre-release checks passed$(NC)"

# Documentation
docs-serve: ## Serve documentation locally
	@echo "$(BLUE)Serving documentation...$(NC)"
	cd docs && python -m http.server 8080

# Database (if needed in future)
db-migrate: ## Run database migrations
	@echo "$(BLUE)Running database migrations...$(NC)"
	alembic upgrade head || true

db-rollback: ## Rollback database migration
	@echo "$(BLUE)Rolling back database...$(NC)"
	alembic downgrade -1 || true

# Utility targets
logs: ## Show application logs
	@tail -f backend/logs/*.log || echo "No logs found"

ps: ## Show running processes
	@ps aux | grep python | grep -v grep

kill: ## Kill all Python processes (use with caution)
	@pkill -f "python.*server.py" || true
	@echo "$(GREEN)✓ Processes killed$(NC)"

# Test markers info
test-markers: ## Show available pytest markers
	@echo "$(BLUE)Available test markers:$(NC)"
	@echo "  unit          - Unit tests (fast, isolated)"
	@echo "  integration   - Integration tests"
	@echo "  e2e           - End-to-end tests"
	@echo "  slow          - Slow running tests"
	@echo "  fast          - Fast tests"
	@echo "  smoke         - Smoke tests (critical)"
	@echo "  voice         - Voice mode tests"
	@echo "  email         - Email tests"
	@echo "  calendar      - Calendar tests"
	@echo "  api           - API tests"
	@echo "  performance   - Performance tests"
	@echo "  security      - Security tests"

version: ## Show project version
	@echo "talk2myinbox v1.0.0"
