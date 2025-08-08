# Release Process

## Prerequisites

1. PyPI account with maintainer access
2. GitHub repository secrets configured:
   - `PYPI_API_TOKEN` - PyPI token

## Package Names

We maintain multiple package names on PyPI:

- **`flow-sdk`** - Primary package name
- **`mithril-ai`** - Alternative branding
- **`flow-acc`** - Accelerator branding

## Release Steps

### 1. Reserve Package Names (First Time Only)

```bash
cd scripts
python reserve_packages.py
pip install twine
twine upload dist/*.whl
```

### 2. Prepare Release

1. Update version in `pyproject.toml`
2. Update CHANGELOG.md
3. Run tests: `uv run pytest`
4. Create PR and merge to main

### 3. Create GitHub Release

1. Go to GitHub Releases
2. Click "Create a new release"
3. Create new tag (e.g., `v2.0.0`)
4. Write release notes
5. Publish release

This triggers the automated PyPI publish workflow.

### 4. Manual Publishing (if needed)

```bash
# Build
uv run python -m build

# Check
uv run twine check dist/*

# Upload to PyPI
uv run twine upload dist/*
```

### 5. Publish Alternative Names

Use the GitHub Actions workflow:

1. Go to Actions → "Publish to PyPI"
2. Click "Run workflow"
3. Select package name (mithril-ai or flow-acc)
4. Click "Run workflow"

## Versioning

We follow semantic versioning:
- MAJOR.MINOR.PATCH (e.g., 2.0.0)
- MAJOR: Breaking API changes
- MINOR: New features, backwards compatible
- PATCH: Bug fixes

## Post-Release

1. Verify installation: `pip install flow-sdk`
2. Update documentation if needed
3. Announce release in appropriate channels