#!/bin/bash
# Post-save hook for ClaudeCraftsman
# Runs type checking and linting after file saves

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Running post-save checks...${NC}"

# Only process Python files
if [[ "$1" == *.py ]]; then
    echo "Processing $1..."

    # Run ruff formatting
    echo "Formatting with ruff..."
    uv run ruff format "$1"

    # Run ruff linting with fixes
    echo "Linting with ruff..."
    uv run ruff check --fix "$1"

    # Run mypy type checking
    echo "Type checking with mypy..."
    if uv run mypy "$1" \
        --ignore-missing-imports \
        --no-strict-optional \
        --warn-unused-ignores \
        --check-untyped-defs \
        --disallow-untyped-defs \
        --disallow-any-explicit; then
        echo -e "${GREEN}✓ All checks passed${NC}"
    else
        echo -e "${YELLOW}⚠ Type issues detected - consider fixing${NC}"
    fi
fi

echo -e "${GREEN}Post-save checks complete${NC}"
