# Makefile for ReqNinja development

.PHONY: help install install-dev test test-cov lint format type-check clean build upload docs

help:
	@echo "ReqNinja Development Commands:"
	@echo "  install      Install package in development mode"
	@echo "  install-dev  Install with development dependencies"
	@echo "  test         Run tests"
	@echo "  test-cov     Run tests with coverage"
	@echo "  lint         Run linting (flake8)"
	@echo "  format       Format code (black + isort)"
	@echo "  type-check   Run type checking (mypy)"
	@echo "  clean        Clean build artifacts"
	@echo "  build        Build distribution packages"
	@echo "  upload       Upload to PyPI"
	@echo "  docs         Build documentation"

install:
	pip install -e .

install-dev:
	pip install -e ".[dev,test]"
	pre-commit install

test:
	pytest

test-cov:
	pytest --cov=reqninja --cov-report=html --cov-report=term

lint:
	flake8 reqninja tests

format:
	black reqninja tests
	isort reqninja tests

type-check:
	mypy reqninja

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean
	python -m build

upload: build
	twine upload dist/*

docs:
	@echo "Documentation build not implemented yet"

# Development shortcuts
dev: install-dev

check: lint type-check test

all: format check test-cov
