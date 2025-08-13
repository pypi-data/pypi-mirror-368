# ClaudeCraftsman PyPI Publishing Guide
*Comprehensive guide for packaging and publishing ClaudeCraftsman to PyPI*

**Document**: PUBLISHING-GUIDE-pypi-release-2025-08-08.md
**Type**: Guide
**Created**: 2025-08-08
**Purpose**: Step-by-step instructions for releasing ClaudeCraftsman to PyPI

## Table of Contents
- [Prerequisites](#prerequisites)
- [Pre-Release Checklist](#pre-release-checklist)
- [Building the Package](#building-the-package)
- [Testing the Package](#testing-the-package)
- [Publishing to PyPI](#publishing-to-pypi)
- [Post-Release Tasks](#post-release-tasks)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### 1. PyPI Account Setup

Create accounts on both Test PyPI and Production PyPI:
- **Test PyPI**: https://test.pypi.org/account/register/
- **Production PyPI**: https://pypi.org/account/register/

**Security Recommendations**:
- Enable 2FA on both accounts
- Use a strong, unique password
- Generate API tokens instead of using passwords

### 2. Generate API Tokens

Generate API tokens for secure authentication:

1. **Test PyPI Token**:
   - Navigate to: https://test.pypi.org/manage/account/token/
   - Create token with scope "Entire account" or project-specific
   - Save the token securely (starts with `pypi-`)

2. **Production PyPI Token**:
   - Navigate to: https://pypi.org/manage/account/token/
   - Create token with scope "Entire account" or project-specific
   - Save the token securely

### 3. Configure Authentication

Create `~/.pypirc` configuration file:

```bash
cat > ~/.pypirc << 'EOF'
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-[your-production-token-here]

[testpypi]
username = __token__
password = pypi-[your-test-token-here]
repository = https://test.pypi.org/legacy/
EOF

# Secure the file
chmod 600 ~/.pypirc
```

### 4. Install Publishing Tools

```bash
# Install twine for secure uploads
uv tool install twine

# Verify installation
twine --version
```

## Pre-Release Checklist

Before releasing, ensure all items are complete:

### Code Quality
- [ ] All tests pass: `uv run pytest`
- [ ] No linting errors: `uv run ruff check src/`
- [ ] Type checking passes: `uv run mypy src/`
- [ ] Code coverage acceptable: `uv run pytest --cov`

### Documentation
- [ ] README.md is up-to-date
- [ ] CHANGELOG.md updated with release notes
- [ ] API documentation current
- [ ] Installation instructions verified

### Version Management
- [ ] Version bumped in `pyproject.toml`
- [ ] Version follows semantic versioning (MAJOR.MINOR.PATCH)
- [ ] No version conflicts with previous releases

### Legal and Metadata
- [ ] LICENSE file exists and is correct
- [ ] Copyright notices updated
- [ ] Author information accurate in `pyproject.toml`
- [ ] Project URLs correct in `pyproject.toml`

### Git Repository
- [ ] All changes committed
- [ ] Working directory clean: `git status`
- [ ] Changes pushed to remote repository
- [ ] Ready to create release tag

## Building the Package

### 1. Clean Previous Builds

```bash
# Remove old distribution files
rm -rf dist/
rm -rf build/
rm -rf src/*.egg-info/
```

### 2. Build Distributions

```bash
# Build both wheel and source distributions
uv build

# This creates:
# - dist/claudecraftsman-X.Y.Z-py3-none-any.whl (wheel)
# - dist/claudecraftsman-X.Y.Z.tar.gz (source)
```

### 3. Verify Build Contents

```bash
# Check what files are included
tar -tzf dist/claudecraftsman-*.tar.gz | head -20

# Verify wheel contents
unzip -l dist/claudecraftsman-*.whl | head -20
```

## Testing the Package

### 1. Local Installation Test

```bash
# Create test environment
uv venv test-release
source test-release/bin/activate  # On Windows: test-release\Scripts\activate

# Install the built wheel
uv pip install dist/claudecraftsman-*.whl

# Test basic functionality
cc --version
cc --help
cc init --help

# Clean up
deactivate
rm -rf test-release/
```

### 2. Test PyPI Upload

Always test on Test PyPI first:

```bash
# Upload to Test PyPI
twine upload --repository testpypi dist/*

# You should see:
# Uploading distributions to https://test.pypi.org/legacy/
# Uploading claudecraftsman-X.Y.Z-py3-none-any.whl
# Uploading claudecraftsman-X.Y.Z.tar.gz
```

### 3. Install from Test PyPI

```bash
# Test installation from Test PyPI
uvx --from claudecraftsman --index-url https://test.pypi.org/simple/ cc --version

# Or create a fresh environment
uv venv test-pypi
source test-pypi/bin/activate
# Use --extra-index-url to allow dependencies from main PyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ claudecraftsman
cc --version
deactivate
rm -rf test-pypi/
```

## Publishing to PyPI

### 1. Final Version Check

```bash
# Ensure version is correct
grep version pyproject.toml

# Ensure no test or dev suffixes in version
```

### 2. Upload to Production PyPI

```bash
# Upload to production
twine upload dist/*

# Expected output:
# Uploading distributions to https://upload.pypi.org/legacy/
# Uploading claudecraftsman-X.Y.Z-py3-none-any.whl
# Uploading claudecraftsman-X.Y.Z.tar.gz
# View at: https://pypi.org/project/claudecraftsman/X.Y.Z/
```

### 3. Verify Production Release

```bash
# Wait 1-2 minutes for PyPI CDN to update

# Test with uvx
uvx --from claudecraftsman cc --version

# Test global installation
uv tool install claudecraftsman
cc --version

# Verify on PyPI page
# https://pypi.org/project/claudecraftsman/
```

## Post-Release Tasks

### 1. Create Git Tag

```bash
# Create annotated tag
git tag -a v1.0.0 -m "Release version 1.0.0

- Feature: Self-managing framework
- Feature: Pure Python implementation
- Feature: Enhanced CLI with health monitoring
- Fix: Document archival system
- See CHANGELOG.md for details"

# Push tag to remote
git push origin v1.0.0
```

### 2. Create GitHub Release

1. Navigate to: https://github.com/[your-org]/claudecraftsman/releases/new
2. Select the tag you just created
3. Title: "ClaudeCraftsman v1.0.0"
4. Description: Copy from CHANGELOG.md
5. Attach files:
   - `dist/claudecraftsman-1.0.0-py3-none-any.whl`
   - `dist/claudecraftsman-1.0.0.tar.gz`
6. Check "Set as the latest release"
7. Publish release

### 3. Update Documentation

- [ ] Update installation instructions if needed
- [ ] Update framework version references
- [ ] Announce in project discussions/forums
- [ ] Update any external documentation

### 4. Monitor Release

- Check PyPI download statistics
- Monitor GitHub issues for problems
- Watch for user feedback
- Be ready to release patch version if critical issues found

## Troubleshooting

### Common Issues

**Authentication Failed**
```bash
# Verify token is correct in ~/.pypirc
# Ensure token hasn't expired
# Check token has correct permissions
```

**Package Already Exists**
```bash
# You cannot re-upload the same version
# Bump version in pyproject.toml
# Rebuild and re-upload
```

**Missing Required Fields**
```bash
# Check pyproject.toml has all required fields:
# - name, version, description
# - authors with email
# - license
# - readme
```

**Build Errors**
```bash
# Ensure all files exist that are referenced
# Check for syntax errors in pyproject.toml
# Verify hatchling is installed: uv pip install hatchling
```

### Validation Commands

```bash
# Check package metadata
twine check dist/*

# Test installation in isolated environment
uvx --from dist/claudecraftsman-*.whl cc --version

# Verify all entry points work
cc --help
claudecraftsman --help
```

## Version Management

### Semantic Versioning

Follow semantic versioning (MAJOR.MINOR.PATCH):
- **MAJOR**: Breaking API changes
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, backward compatible

### Pre-release Versions

For testing releases:
```toml
version = "1.0.0rc1"  # Release candidate
version = "1.0.0b1"   # Beta
version = "1.0.0a1"   # Alpha
```

### Post-release Versions

For hotfixes:
```toml
version = "1.0.0.post1"  # Post-release fix
```

## Security Best Practices

1. **Use API Tokens**: Never use password authentication
2. **Secure Storage**: Keep ~/.pypirc with 600 permissions
3. **Test First**: Always test on Test PyPI before production
4. **Sign Releases**: Use GPG signing for extra security
   ```bash
   twine upload --sign dist/*
   ```
5. **Verify Downloads**: Check package integrity after upload
6. **Monitor Package**: Watch for unauthorized changes

## Automation (Future Enhancement)

Consider setting up GitHub Actions for automated releases:

```yaml
# .github/workflows/publish.yml
name: Publish to PyPI
on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install --upgrade pip
          pip install build twine
      - name: Build package
        run: python -m build
      - name: Publish to PyPI
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
        run: twine upload dist/*
```

## Quick Reference

### Complete Release Command Sequence

```bash
# 1. Update version in pyproject.toml
# 2. Update CHANGELOG.md
# 3. Commit changes
git add pyproject.toml CHANGELOG.md
git commit -m "chore: prepare release v1.0.0"
git push

# 4. Build
rm -rf dist/
uv build

# 5. Test locally
uv venv test-env && source test-env/bin/activate
uv pip install dist/*.whl
cc --version
deactivate && rm -rf test-env

# 6. Upload to Test PyPI
twine upload --repository testpypi dist/*

# 7. Test from Test PyPI
uvx --from claudecraftsman --index-url https://test.pypi.org/simple/ cc --version

# 8. Upload to Production
twine upload dist/*

# 9. Create git tag
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0

# 10. Create GitHub release
```

---

*This guide should be updated with lessons learned from each release.*
