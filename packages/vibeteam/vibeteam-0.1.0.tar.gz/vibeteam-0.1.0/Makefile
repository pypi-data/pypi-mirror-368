.PHONY: install build lint format test clean publish help

# Default target
help:
	@echo "Available commands:"
	@echo "  install    Install dependencies with uv"
	@echo "  build      Build the package"
	@echo "  lint       Run linting with ruff"
	@echo "  format     Format code with ruff"
	@echo "  test       Run tests"
	@echo "  clean      Clean build artifacts"
	@echo "  publish    Publish to PyPI"
	@echo "  test-pub   Publish to Test PyPI"

install:
	uv sync

build:
	@echo "Building package..."
	rm -rf dist/ build/ *.egg-info
	uv build
	@echo "Build complete. Files in dist/:"
	@ls -la dist/

lint:
	@echo "Running linting..."
	uvx ruff check src/

format:
	@echo "Formatting code..."
	uvx ruff format src/
	uvx ruff check --fix src/

test:
	@echo "Running tests..."
	uv run test_server.py

clean:
	@echo "Cleaning build artifacts..."
	rm -rf dist/ build/ *.egg-info
	rm -rf src/__pycache__ src/*/__pycache__
	find . -name "*.pyc" -delete

publish: build
	@echo "Publishing to PyPI..."
	@echo "Make sure TWINE_PASSWORD is set!"
	uv tool run twine upload dist/*

test-pub: build
	@echo "Publishing to Test PyPI..."
	uv tool run twine upload --repository testpypi dist/*
	@echo "Test with: pip install --index-url https://test.pypi.org/simple/ vibeteam"
