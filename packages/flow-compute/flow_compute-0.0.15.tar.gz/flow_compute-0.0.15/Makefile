.PHONY: help install dev test build publish-test publish clean

help:
	@echo "Flow SDK Development Commands"
	@echo "============================"
	@echo "install      Install flow-sdk in current environment"
	@echo "dev          Install with dev dependencies"
	@echo "test         Run tests"
	@echo "build        Build distribution packages"
	@echo "publish      Publish to PyPI"
	@echo "clean        Remove build artifacts"

install:
	uv sync

dev:
	uv sync --dev

test:
	uv run pytest

build:
	uv run python -m build

publish: build
	uv run twine upload dist/*

clean:
	rm -rf dist/ build/ *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete