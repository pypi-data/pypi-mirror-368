# MANIFEST.in to pyproject.toml Consolidation

## What We Did
We consolidated the MANIFEST.in file configuration into pyproject.toml, which is the modern approach for Python packaging.

## Why This Is Better
1. **Single Configuration File**: Everything is now in pyproject.toml instead of spread across multiple files
2. **Better Comments**: We can add detailed comments explaining each section
3. **Modern Standard**: pyproject.toml is the current best practice for Python packaging
4. **Build Tool Integration**: Hatchling natively understands these settings

## The Configuration

### For Wheel Distribution (what gets installed)
```toml
[tool.hatch.build]
include = [
    "src/claudecraftsman/**/*.py",      # All Python source files
    "src/claudecraftsman/**/*.md",      # All markdown files (for framework)
    "src/claudecraftsman/templates/**/*",  # Everything in templates
]
```

### For Source Distribution (what gets uploaded to PyPI)
```toml
[tool.hatch.build.targets.sdist]
include = [
    "/src",           # All source code
    "/tests",         # Test suite
    "/.claude",       # Framework files (for development/reference)
    "/README.md",     # Project documentation
    "/LICENSE",       # License file
    "/pyproject.toml", # This build configuration
]
```

## How It Works
1. When building a wheel (`uv build`), Hatchling includes all files matching the patterns in `[tool.hatch.build]`
2. The markdown files in `templates/` get packaged with the Python code
3. When users install (`uv add claudecraftsman`), these files are available in site-packages
4. The `cc init` command can then copy these files to the project's `.claude/` directory

## Verification
We verified the markdown files are included:
```bash
unzip -l dist/claudecraftsman-1.0.0-py3-none-any.whl | grep "\.md$"
```

This shows all our framework markdown files are properly packaged! 🎉
