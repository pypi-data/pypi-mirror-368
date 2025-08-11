# Makefile for building and installing markdown_normalization Python wheel

PACKAGE_NAME := markdown_normalization
PYTHON := python

.PHONY: all check-deps install-deps build install clean test

all: check-deps install-deps build test install clean

check-deps:
	@command -v rustc >/dev/null 2>&1 || { echo >&2 "❌ rustc not found. Please install Rust: https://rustup.rs"; exit 1; }
	@command -v cargo >/dev/null 2>&1 || { echo >&2 "❌ cargo not found. Please install Rust: https://rustup.rs"; exit 1; }
	@command -v uv >/dev/null 2>&1 || { echo >&2 "❌ uv not found. Please install uv: https://docs.astral.sh/uv/"; exit 1; }
	
install-deps:
	@echo "📦 Installing dependencies with uv..."
	@uv add --dev maturin pytest
	
build:
	@echo "🔨 Building wheel with maturin..."
	@uv run maturin build --release --strip
	@rm -f target/wheels/*linux_x86_64.whl 2>/dev/null || true
	
test:
	@echo "🧪 Running tests..."
	@uv run pytest -v -s

install:
	@echo "📦 Installing wheel locally..."
	@uv pip install --force-reinstall --no-cache $(shell ls target/wheels/$(PACKAGE_NAME)-*.whl | head -n1)

clean:
	@echo "🧹 Cleaning build artifacts..."
	@rm -rf build dist target *.egg-info
	@find . -type d -name '__pycache__' -exec rm -rf {} +

dev:
	@echo "🔧 Installing in development mode..."
	@uv run maturin develop --release

publish:
	@echo "🚀 Publishing to PyPI..."
	@uv run maturin publish