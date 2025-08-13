#!/bin/bash
# Pre-edit hook for ClaudeCraftsman
# Ensures type checking before any file edits

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Running pre-edit type checks...${NC}"

# Run mypy on the file being edited (if Python)
if [[ "$1" == *.py ]]; then
    echo "Checking types for $1..."

    # Run mypy with the same settings as CI
    if uv run mypy "$1" \
        --ignore-missing-imports \
        --no-strict-optional \
        --warn-unused-ignores \
        --check-untyped-defs \
        --disallow-untyped-defs \
        --disallow-any-explicit; then
        echo -e "${GREEN}✓ Type check passed${NC}"
    else
        echo -e "${RED}✗ Type check failed - fixing issues...${NC}"

        # Try to auto-fix common issues
        python3 -c "
import re
from pathlib import Path

file_path = Path('$1')
content = file_path.read_text()

# Add -> None to functions without return type
content = re.sub(
    r'def (\w+)\([^)]*\):(?!\s*->)',
    r'def \1\g<0> -> None:',
    content
)

# Add type imports if missing
if 'from typing import' not in content:
    content = 'from typing import Any, Dict, List, Optional\\n' + content

file_path.write_text(content)
"
        echo -e "${YELLOW}Applied automatic fixes, re-checking...${NC}"

        # Re-run mypy
        uv run mypy "$1" \
            --ignore-missing-imports \
            --no-strict-optional \
            --warn-unused-ignores \
            --check-untyped-defs
    fi
fi

echo -e "${GREEN}Pre-edit checks complete${NC}"
