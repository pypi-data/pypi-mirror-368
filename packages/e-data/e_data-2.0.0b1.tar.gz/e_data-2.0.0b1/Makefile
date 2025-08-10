.PHONY: help install install-dev test lint format build clean publish publish-test

help:  ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install the package in development mode
	pip install -e .

install-dev:  ## Install with development dependencies
	pip install -e ".[dev,test]"

test:  ## Run tests
	pytest

test-cov:  ## Run tests with coverage
	pytest --cov=edata --cov-report=html --cov-report=term

lint:  ## Run linting checks
	flake8 edata/
	mypy edata/

format:  ## Format code with black
	black edata/

format-check:  ## Check if code is formatted
	black --check edata/

clean:  ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build:  ## Build the package
	python -m build

publish-test:  ## Publish to TestPyPI
	python -m twine upload --repository testpypi dist/*

publish:  ## Publish to PyPI
	python -m twine upload dist/*

# Combined workflow commands
dev-setup: install-dev  ## Setup development environment

pre-commit: format lint test  ## Run all pre-commit checks

release: clean build publish  ## Build and publish to PyPI

release-test: clean build publish-test  ## Build and publish to TestPyPI
