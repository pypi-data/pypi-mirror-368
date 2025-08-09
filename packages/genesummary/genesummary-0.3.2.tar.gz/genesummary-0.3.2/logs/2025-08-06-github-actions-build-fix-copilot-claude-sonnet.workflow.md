# GitHub Actions Build Fix

## Issue Description

The GitHub Actions workflow was failing during the build verification step with multiple errors:

1. First error:
```
/home/runner/work/geneinfo/geneinfo/.venv/bin/python: No module named pip
Error: Process completed with exit code 1.
```

2. Second error (after initial fix):
```
error: No virtual environment found; run `uv venv` to create an environment, or pass `--system` to install into a non-virtual environment
```

3. Third error (after temporary venv approach):
```
error: No virtual environment found; run `uv venv` to create an environment, or pass `--system` to install into a non-virtual environment
Error: Process completed with exit code 2.
```

## Root Cause

1. **Initial Issue**: The workflow was attempting to use `python -m pip` instead of `uv pip`.

2. **Secondary Issue**: The build job wasn't creating a proper uv environment with synced dependencies like the test job does.

3. **Inconsistent Approach**: Using temporary environments instead of following uv best practices with `uv sync`.

## Solution Applied

**File:** `.github/workflows/python-package.yml`

**Problem**: Build job was missing proper environment setup
**Solution**: Added the same dependency installation pattern as the test job:

```bash
- name: Install dependencies
  run: |
    uv sync --all-extras --dev
```

**Final build verification**:
```bash
ls -la dist/
uv pip install --no-deps dist/*.whl
uv run python -c "import geneinfo; print(f'Successfully imported geneinfo version: {geneinfo.__version__ if hasattr(geneinfo, \"__version__\") else \"unknown\"}')"
```

## Reasoning

1. **Consistency**: The build job should follow the same pattern as the test job - both should use `uv sync` to create and populate the virtual environment.

2. **uv Best Practices**: Using `uv sync --all-extras --dev` ensures:
   - Proper virtual environment creation
   - All dependencies are installed
   - Development dependencies are available if needed
   - Lock file consistency

3. **Reliability**: This approach eliminates environment-related errors by ensuring a proper uv-managed environment exists before any package operations.

4. **Maintainability**: Having consistent environment setup across all jobs makes the workflow easier to understand and maintain.

## Additional Notes

- The package is built as `genesummary-0.1.0-py3-none-any.whl` (package name from pyproject.toml)
- The module import is still `geneinfo` (module directory name)
- This name discrepancy is intentional based on the project configuration

## Testing

The fix should resolve all GitHub Actions build failures by:
1. Establishing a proper uv environment with `uv sync` (same as test job)
2. Using native uv commands throughout the workflow
3. Ensuring consistent environment setup across all jobs

## Benefits

- **Consistency**: Both test and build jobs now follow the same environment setup pattern
- **uv Best Practices**: Uses `uv sync` to properly manage the virtual environment and dependencies
- **Reliability**: Eliminates environment-related errors by ensuring proper setup
- **Maintainability**: Simpler, more predictable workflow structure
