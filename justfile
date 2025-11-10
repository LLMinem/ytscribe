# Format all Python code and Markdown documentation
format:
    uv run ruff format .
    uv run mdformat .

# Lint Python code for errors
lint:
    uv run ruff check .

# Run all formatting and linting checks
check: format lint
    @echo "✓ All checks passed!"

# Run the test suite
test:
    uv run pytest

# Sync dependencies
sync:
    uv sync
