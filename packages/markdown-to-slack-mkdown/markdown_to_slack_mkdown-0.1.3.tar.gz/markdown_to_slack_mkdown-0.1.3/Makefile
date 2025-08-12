.PHONY: help install lint format test coverage build clean

help: ## Show this help message
	@echo "Usage: make [target]"
	@echo ""
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

install: ## Install the package and dependencies with uv
	uv sync --group dev

lint: ## Run linting (flake8 and mypy)
	uv run flake8 markdown_to_slack_mkdown tests
	uv run mypy markdown_to_slack_mkdown

format: ## Format code with black
	uv run black .

test: ## Run tests with pytest
	uv run pytest

coverage: ## Run tests with coverage report
	uv run pytest --cov=markdown_to_slack_mkdown --cov-report=html --cov-report=term

build: ## Build the package
	uv run python -m build

check: ## Check package with twine
	uv run twine check dist/*

clean: ## Clean build artifacts
	rm -rf build dist *.egg-info
	rm -rf .pytest_cache .coverage htmlcov
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete