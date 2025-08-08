# GitHub Actions Deployment Workflow for GeneInfo Package

**Author**: Chunjie Liu
**Contact**: chunjie.sam.liu@gmail.com
**Date**: 2025-08-06
**AI Model**: copilot-claude-sonnet
**Description**: Complete setup for automated package publishing using GitHub Actions
**Version**: 0.1

## Overview

This document outlines the GitHub Actions workflow setup for automatically testing, building, and publishing the `geneinfo` Python package to PyPI and TestPyPI.

## Workflow Components

### 1. Automated Testing (`test` job)
- **Triggers**: Push to main, pull requests
- **Python versions**: 3.11, 3.12
- **Tools**: uv, pytest, coverage
- **Features**:
  - Multi-version testing matrix
  - Code coverage reporting
  - Optional linting with ruff
  - Codecov integration

### 2. Package Building (`build` job)
- **Dependencies**: Requires successful tests
- **Features**:
  - Uses modern `uv` package manager
  - Builds both wheel and source distributions
  - Validates build artifacts
  - Stores distributions as artifacts

### 3. PyPI Publishing (`publish-to-pypi` job)
- **Trigger**: GitHub release published
- **Security**: Uses trusted publishing (no API tokens needed)
- **Target**: Main PyPI repository

### 4. TestPyPI Publishing (`publish-to-testpypi` job)
- **Trigger**: Push to main branch
- **Purpose**: Testing releases before official PyPI
- **Target**: TestPyPI repository

## Setup Requirements

### 1. PyPI Trusted Publishing Configuration

#### For PyPI (Production):
1. Go to [PyPI Account Settings](https://pypi.org/manage/account/publishing/)
2. Add a new "pending publisher":
   - **PyPI Project Name**: `geneinfo`
   - **Owner**: `chunjie-sam-liu`
   - **Repository name**: `geneinfo`
   - **Workflow name**: `python-package.yml`
   - **Environment name**: `pypi`

#### For TestPyPI (Testing):
1. Go to [TestPyPI Account Settings](https://test.pypi.org/manage/account/publishing/)
2. Add a new "pending publisher" with same details but:
   - **Environment name**: `testpypi`

### 2. GitHub Repository Settings

#### Required Environments:
Create these environments in GitHub repository settings:

1. **Environment: `pypi`**
   - Protection rule: Require review (optional)
   - Deployment branches: Only selected branches → `main`

2. **Environment: `testpypi`**
   - Protection rule: None needed
   - Deployment branches: Only selected branches → `main`

### 3. Package Metadata Enhancements

The `pyproject.toml` has been updated with:
- Author and maintainer information
- License specification
- Keywords for discoverability
- PyPI classifiers
- Project URLs (homepage, docs, issues)

## Publishing Process

### For Testing (TestPyPI)
```bash
# Every push to main automatically publishes to TestPyPI
git push origin main
```

### For Production (PyPI)
```bash
# 1. Update version in pyproject.toml and __init__.py
# 2. Create and push a git tag
git tag v0.1.1
git push origin v0.1.1

# 3. Create a GitHub release
# Go to GitHub → Releases → Create new release
# Choose the tag, add release notes, publish
```

## Workflow Features

### Modern Python Tooling
- **uv**: Fast Python package manager and project manager
- **hatchling**: Modern build backend
- **trusted publishing**: Secure, token-free publishing

### Security Best Practices
- Uses OpenID Connect (OIDC) for authentication
- No API tokens stored in repository
- Environment protection rules
- Minimal required permissions

### Quality Assurance
- Multi-version testing matrix
- Code coverage tracking
- Optional linting integration
- Build artifact validation

## Monitoring and Maintenance

### Success Indicators
- ✅ Tests pass on all Python versions
- ✅ Package builds successfully
- ✅ TestPyPI deployment succeeds
- ✅ PyPI deployment on releases

### Common Issues and Solutions

1. **Build Failures**
   ```bash
   # Check dependencies and build system
   uv sync --dev
   uv build
   ```

2. **Test Failures**
   ```bash
   # Run tests locally
   uv run pytest -v
   ```

3. **Publishing Issues**
   - Verify trusted publishing configuration
   - Check environment settings in GitHub
   - Ensure version numbers are unique

### Version Management Strategy

1. **Development**: Push to main → TestPyPI
2. **Releases**: Create GitHub release → PyPI
3. **Versioning**: Semantic versioning (MAJOR.MINOR.PATCH)

## Future Enhancements

- [ ] Add automated dependency updates (Dependabot)
- [ ] Implement security scanning (CodeQL)
- [ ] Add performance benchmarking
- [ ] Set up documentation deployment
- [ ] Configure release notes automation

## Related Documentation

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [PyPI Trusted Publishing](https://docs.pypi.org/trusted-publishers/)
- [uv Documentation](https://docs.astral.sh/uv/)
- [Hatchling Build Backend](https://hatch.pypa.io/latest/config/build/)
