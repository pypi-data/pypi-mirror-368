.PHONY: help install install-dev test test-integration test-all coverage lint format clean

help:
	@echo "Available commands:"
	@echo "  make install        Install the package"
	@echo "  make install-dev    Install with development dependencies"
	@echo "  make test           Run unit tests"
	@echo "  make test-integration Run integration tests (requires env vars)"
	@echo "  make test-all       Run all tests"
	@echo "  make coverage       Run tests with coverage report"
	@echo "  make lint           Run linting checks"
	@echo "  make format         Format code"
	@echo "  make clean          Clean up generated files"

install:
	pip install -e .

install-dev:
	pip install -r requirements-dev.txt
	pip install -e .

test:
	pytest -m "not integration"

test-integration:
	@if [ -z "$$GLIMPS_TEST_API_URL" ]; then \
		echo "Error: GLIMPS_TEST_API_URL environment variable not set"; \
		exit 1; \
	fi
	pytest -m integration -v

test-all:
	pytest

coverage:
	pytest --cov=gaudit --cov-report=html --cov-report=term-missing -m "not integration"

lint:
	ruff check src tests

format:
	ruff format src tests

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .ruff_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete