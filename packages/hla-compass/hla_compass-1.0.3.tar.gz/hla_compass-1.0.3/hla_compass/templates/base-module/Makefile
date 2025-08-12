# Makefile for Simple Peptide Analyzer Template
# Provides convenient commands for development, testing, and deployment

.PHONY: help install test lint format clean docker-build docker-test docker-shell run package deploy docs

# Default target
.DEFAULT_GOAL := help

# Variables
PYTHON := python3
PIP := pip3
MODULE_NAME := simple-analyzer-template
DOCKER_IMAGE := $(MODULE_NAME)
PACKAGE_VERSION := 1.0.0

# Colors for output
RED := \033[31m
GREEN := \033[32m
YELLOW := \033[33m
BLUE := \033[34m
RESET := \033[0m

help: ## Show this help message
	@echo "$(BLUE)Simple Peptide Analyzer Template - Development Commands$(RESET)"
	@echo ""
	@echo "$(GREEN)Setup Commands:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E '^(install|setup|clean)' | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-15s$(RESET) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(GREEN)Development Commands:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E '^(run|test|lint|format)' | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-15s$(RESET) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(GREEN)Docker Commands:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E '^docker-' | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-15s$(RESET) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(GREEN)Deployment Commands:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E '^(package|deploy|docs)' | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-15s$(RESET) %s\n", $$1, $$2}'
	@echo ""

# Setup and Installation
install: ## Install dependencies for development
	@echo "$(BLUE)Installing dependencies...$(RESET)"
	$(PIP) install -r backend/requirements.txt
	$(PIP) install pytest pytest-cov black isort flake8 mypy bandit safety
	@echo "$(GREEN)Dependencies installed successfully$(RESET)"

install-dev: ## Install development dependencies only
	@echo "$(BLUE)Installing development dependencies...$(RESET)"
	$(PIP) install pytest pytest-cov pytest-mock pytest-benchmark black isort flake8 mypy bandit safety ipython jupyter
	@echo "$(GREEN)Development dependencies installed$(RESET)"

setup: install ## Complete setup (alias for install)
	@echo "$(GREEN)Setup complete! Run 'make test' to verify installation$(RESET)"

# Development Commands
run: ## Run the module with example data
	@echo "$(BLUE)Running module with sample input...$(RESET)"
	cd backend && $(PYTHON) main.py

test: ## Run all tests with coverage
	@echo "$(BLUE)Running tests with coverage...$(RESET)"
	$(PYTHON) -m pytest backend/tests/ -v --cov=backend --cov-report=term --cov-report=html

test-quick: ## Run tests without coverage (faster)
	@echo "$(BLUE)Running quick tests...$(RESET)"
	$(PYTHON) -m pytest backend/tests/ -v

test-coverage: ## Generate detailed coverage report
	@echo "$(BLUE)Generating coverage report...$(RESET)"
	$(PYTHON) -m pytest backend/tests/ --cov=backend --cov-report=html --cov-report=term
	@echo "$(GREEN)Coverage report generated in htmlcov/index.html$(RESET)"

test-performance: ## Run performance benchmarks
	@echo "$(BLUE)Running performance benchmarks...$(RESET)"
	$(PYTHON) -m pytest backend/tests/ -v --benchmark-only --benchmark-json=benchmark_results.json

test-all: lint test test-performance ## Run all tests including linting and performance

# Code Quality
lint: ## Run all linting tools
	@echo "$(BLUE)Running linting tools...$(RESET)"
	@echo "$(YELLOW)Running flake8...$(RESET)"
	flake8 backend/ --max-line-length=88 --extend-ignore=E203,W503
	@echo "$(YELLOW)Running mypy...$(RESET)"
	mypy backend/main.py --ignore-missing-imports || true
	@echo "$(YELLOW)Running bandit (security)...$(RESET)"
	bandit -r backend/ -f json -o bandit-report.json || true
	@echo "$(GREEN)Linting complete$(RESET)"

format: ## Format code with black and isort
	@echo "$(BLUE)Formatting code...$(RESET)"
	black backend/ --line-length=88
	isort backend/
	@echo "$(GREEN)Code formatted$(RESET)"

format-check: ## Check if code needs formatting
	@echo "$(BLUE)Checking code format...$(RESET)"
	black --check backend/ --line-length=88
	isort --check-only backend/

security-check: ## Run security checks
	@echo "$(BLUE)Running security checks...$(RESET)"
	safety check -r backend/requirements.txt
	bandit -r backend/

# Docker Commands
docker-build: ## Build Docker image
	@echo "$(BLUE)Building Docker image...$(RESET)"
	docker build -t $(DOCKER_IMAGE):latest .
	docker build -t $(DOCKER_IMAGE):dev --target development .
	@echo "$(GREEN)Docker images built successfully$(RESET)"

docker-build-prod: ## Build production Docker image
	@echo "$(BLUE)Building production Docker image...$(RESET)"
	docker build -t $(DOCKER_IMAGE):prod --target production .
	@echo "$(GREEN)Production image built successfully$(RESET)"

docker-build-lambda: ## Build AWS Lambda deployment image
	@echo "$(BLUE)Building Lambda deployment image...$(RESET)"
	docker build -t $(DOCKER_IMAGE):lambda --target lambda-deployment .
	@echo "$(GREEN)Lambda image built successfully$(RESET)"

docker-test: ## Run tests in Docker container
	@echo "$(BLUE)Running tests in Docker...$(RESET)"
	docker build -t $(DOCKER_IMAGE):test --target testing .
	docker run --rm $(DOCKER_IMAGE):test
	@echo "$(GREEN)Docker tests completed$(RESET)"

docker-shell: ## Start interactive shell in development container
	@echo "$(BLUE)Starting development shell...$(RESET)"
	docker run -it --rm \
		-v $(PWD):/app \
		-w /app \
		$(DOCKER_IMAGE):dev \
		/bin/bash

docker-run: ## Run module in Docker container
	@echo "$(BLUE)Running module in Docker...$(RESET)"
	docker run --rm $(DOCKER_IMAGE):prod

docker-clean: ## Remove Docker images
	@echo "$(BLUE)Cleaning Docker images...$(RESET)"
	docker rmi $(DOCKER_IMAGE):latest $(DOCKER_IMAGE):dev $(DOCKER_IMAGE):prod 2>/dev/null || true
	@echo "$(GREEN)Docker images cleaned$(RESET)"

# Testing variations
test-local: run ## Run module locally (alias for run)

test-integration: ## Run integration tests
	@echo "$(BLUE)Running integration tests...$(RESET)"
	$(PYTHON) -m pytest backend/tests/test_main.py::TestIntegrationScenarios -v

test-unit: ## Run only unit tests
	@echo "$(BLUE)Running unit tests...$(RESET)"
	$(PYTHON) -m pytest backend/tests/ -v -k "not TestIntegrationScenarios and not TestPerformanceBenchmarks"

# Package and Deployment
package: clean ## Create deployment package
	@echo "$(BLUE)Creating deployment package...$(RESET)"
	mkdir -p dist
	cp -r backend/ dist/
	cp manifest.json dist/
	cp -r examples/ dist/
	cp README.md dist/
	cd dist && zip -r ../$(MODULE_NAME)-$(PACKAGE_VERSION).zip .
	@echo "$(GREEN)Package created: $(MODULE_NAME)-$(PACKAGE_VERSION).zip$(RESET)"

build: package ## Create distribution build (alias for package)

deploy-dev: package ## Deploy to development environment (placeholder)
	@echo "$(BLUE)Deploying to development environment...$(RESET)"
	@echo "$(YELLOW)Note: This is a placeholder. Implement with your deployment tool.$(RESET)"
	@echo "$(YELLOW)Example: hla-compass deploy $(MODULE_NAME)-$(PACKAGE_VERSION).zip --env dev$(RESET)"

deploy-staging: package ## Deploy to staging environment (placeholder)
	@echo "$(BLUE)Deploying to staging environment...$(RESET)"
	@echo "$(YELLOW)Note: This is a placeholder. Implement with your deployment tool.$(RESET)"

deploy-prod: package ## Deploy to production environment (placeholder)
	@echo "$(BLUE)Deploying to production environment...$(RESET)"
	@echo "$(YELLOW)Note: This is a placeholder. Implement with your deployment tool.$(RESET)"
	@echo "$(RED)Warning: This will deploy to production!$(RESET)"

# AWS Lambda deployment
deploy-lambda: docker-build-lambda ## Deploy to AWS Lambda
	@echo "$(BLUE)Deploying to AWS Lambda...$(RESET)"
	@echo "$(YELLOW)Note: Requires AWS CLI and proper permissions$(RESET)"
	@echo "$(YELLOW)Example commands:$(RESET)"
	@echo "  aws lambda create-function --function-name $(MODULE_NAME) \\"
	@echo "    --package-type Image --code ImageUri=<ECR_URI> \\"
	@echo "    --role <LAMBDA_ROLE_ARN> --timeout 300 --memory-size 512"

# Documentation
docs: ## Generate documentation
	@echo "$(BLUE)Generating documentation...$(RESET)"
	@echo "$(YELLOW)Documentation already available in:$(RESET)"
	@echo "  - README.md (main documentation)"
	@echo "  - backend/main.py (code documentation)"
	@echo "  - examples/ (usage examples)"
	@echo "  - manifest.json (API specification)"

docs-serve: ## Serve documentation locally (if using mkdocs)
	@echo "$(BLUE)Note: Install mkdocs to serve documentation locally$(RESET)"
	@echo "$(YELLOW)pip install mkdocs mkdocs-material$(RESET)"
	@echo "$(YELLOW)mkdocs serve$(RESET)"

# Maintenance
clean: ## Clean up generated files
	@echo "$(BLUE)Cleaning up...$(RESET)"
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type f -name "*.coverage" -delete 2>/dev/null || true
	rm -rf htmlcov/ .coverage .pytest_cache/ dist/ *.egg-info/ 2>/dev/null || true
	rm -f *.zip *.tar.gz bandit-report.json benchmark_results.json 2>/dev/null || true
	@echo "$(GREEN)Cleanup complete$(RESET)"

clean-all: clean docker-clean ## Clean everything including Docker images

# Development workflow shortcuts
dev-setup: install format ## Setup development environment
	@echo "$(GREEN)Development environment ready!$(RESET)"
	@echo "$(YELLOW)Next steps:$(RESET)"
	@echo "  1. Edit backend/main.py to implement your analysis"
	@echo "  2. Update manifest.json with your module details"
	@echo "  3. Run 'make test' to verify changes"
	@echo "  4. Run 'make run' to test with sample data"

quick-test: format-check test-quick ## Quick development test cycle

ci-test: lint test ## Run CI-style tests (linting + full tests)

pre-commit: format lint test ## Run pre-commit checks

# Release workflow
release-check: clean ci-test package ## Check if ready for release
	@echo "$(GREEN)Release check complete$(RESET)"
	@echo "$(YELLOW)Ready to release $(MODULE_NAME)-$(PACKAGE_VERSION).zip$(RESET)"

# Monitoring and debugging
logs: ## Show recent logs (placeholder)
	@echo "$(BLUE)Recent logs:$(RESET)"
	@echo "$(YELLOW)Note: Implement log viewing based on your deployment$(RESET)"

status: ## Show module status (placeholder)  
	@echo "$(BLUE)Module Status:$(RESET)"
	@echo "  Name: $(MODULE_NAME)"
	@echo "  Version: $(PACKAGE_VERSION)"
	@echo "  Python: $(shell $(PYTHON) --version)"
	@echo "  Dependencies: $(shell [ -f backend/requirements.txt ] && echo "✓ Found" || echo "✗ Missing")"
	@echo "  Tests: $(shell [ -d backend/tests ] && echo "✓ Found" || echo "✗ Missing")"
	@echo "  Docker: $(shell command -v docker >/dev/null 2>&1 && echo "✓ Available" || echo "✗ Not found")"

# Example usage patterns
examples: ## Show usage examples
	@echo "$(BLUE)Common Usage Examples:$(RESET)"
	@echo ""
	@echo "$(GREEN)Development Workflow:$(RESET)"
	@echo "  make dev-setup     # Setup development environment"
	@echo "  make run           # Test your changes"
	@echo "  make test          # Run comprehensive tests"
	@echo "  make package       # Create deployment package"
	@echo ""
	@echo "$(GREEN)Docker Workflow:$(RESET)"
	@echo "  make docker-build  # Build all Docker images"
	@echo "  make docker-test   # Test in containerized environment"
	@echo "  make docker-run    # Run production image"
	@echo ""
	@echo "$(GREEN)CI/CD Pipeline:$(RESET)"
	@echo "  make ci-test       # Run CI-style tests"
	@echo "  make package       # Create deployment artifact"
	@echo "  make deploy-dev    # Deploy to development"
	@echo ""

# Debugging helpers
debug: ## Run module in debug mode
	@echo "$(BLUE)Running in debug mode...$(RESET)"
	cd backend && $(PYTHON) -u main.py 2>&1 | tee debug.log
	@echo "$(GREEN)Debug output saved to backend/debug.log$(RESET)"

profile: ## Profile module performance
	@echo "$(BLUE)Profiling module performance...$(RESET)"
	cd backend && $(PYTHON) -m cProfile -o profile.stats main.py
	@echo "$(GREEN)Profile saved to backend/profile.stats$(RESET)"
	@echo "$(YELLOW)View with: python -m pstats backend/profile.stats$(RESET)"