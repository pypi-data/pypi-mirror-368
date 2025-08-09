#!/bin/bash
cd "$(dirname "$0")"
echo "Installing package in development mode..."
uv pip install -e .
echo "Running tests..."
uv run --active python -m pytest --tb=short