# GitHub Actions Publishing Setup Checklist

**Author**: Chunjie Liu
**Contact**: chunjie.sam.liu@gmail.com
**Date**: 2025-08-06
**Description**: Step-by-step checklist for setting up automated PyPI publishing
**Version**: 0.1

## ✅ Completed Setup

- [x] Created GitHub Actions workflow (`.github/workflows/python-package.yml`)
- [x] Enhanced `pyproject.toml` with publishing metadata
- [x] Verified package builds successfully
- [x] Confirmed version information is accessible
- [x] Created comprehensive documentation

## 🔧 Required Manual Setup (Do These Next)

### 1. PyPI Trusted Publishing Setup

#### For Production PyPI:
1. **Go to**: [PyPI Account Settings](https://pypi.org/manage/account/publishing/)
2. **Click**: "Add a new pending publisher"
3. **Fill in**:
   - PyPI Project Name: `geneinfo`
   - Owner: `chunjie-sam-liu`
   - Repository name: `geneinfo`
   - Workflow name: `python-package.yml`
   - Environment name: `pypi`
4. **Click**: "Add"

#### For TestPyPI (Optional but Recommended):
1. **Go to**: [TestPyPI Account Settings](https://test.pypi.org/manage/account/publishing/)
2. **Repeat the same process** with environment name: `testpypi`

### 2. GitHub Repository Environment Setup

1. **Go to**: Repository Settings → Environments
2. **Create environment**: `pypi`
   - Deployment branches: `main` only
   - Add protection rule (optional): Require reviewer
3. **Create environment**: `testpypi`
   - Deployment branches: `main` only

## 🚀 Testing the Workflow

### Test 1: Automatic TestPyPI Publishing
```bash
# This will trigger TestPyPI publishing
git add .
git commit -m "Setup automated publishing"
git push origin main
```

### Test 2: Manual PyPI Publishing
```bash
# 1. Update version (if needed)
# Edit pyproject.toml and geneinfo/__init__.py

# 2. Create and push tag
git tag v0.1.0
git push origin v0.1.0

# 3. Create GitHub release
# Go to: https://github.com/chunjie-sam-liu/geneinfo/releases
# Click "Create a new release"
# Choose tag v0.1.0
# Add release notes
# Click "Publish release"
```

## 📊 Monitoring Success

### Check Workflow Status:
- **Actions Tab**: [GitHub Actions](https://github.com/chunjie-sam-liu/geneinfo/actions)
- **TestPyPI**: [test.pypi.org/project/geneinfo](https://test.pypi.org/project/geneinfo/)
- **PyPI**: [pypi.org/project/geneinfo](https://pypi.org/project/geneinfo/)

### Success Indicators:
- ✅ All workflow jobs pass (test, build, publish)
- ✅ Package appears on TestPyPI after push to main
- ✅ Package appears on PyPI after GitHub release
- ✅ Package can be installed: `pip install geneinfo`

## 🔧 Common Issues & Solutions

### Issue: "Publisher not found"
**Solution**: Verify trusted publishing is configured correctly on PyPI/TestPyPI

### Issue: "Environment not found"
**Solution**: Create the required environments in GitHub repository settings

### Issue: Build failures
**Solution**:
```bash
# Test locally first
uv build
uv run pytest
```

### Issue: Version conflicts
**Solution**: Ensure version in `pyproject.toml` and `__init__.py` match and are unique

## 📝 Next Steps After Setup

1. **Test the workflow** by pushing changes
2. **Monitor the first few deployments** closely
3. **Set up branch protection** for main branch
4. **Configure Codecov** for coverage reporting (optional)
5. **Add badges** to README.md for build status

## 🎯 Future Enhancements

- [ ] Add automated dependency updates (Dependabot)
- [ ] Set up documentation publishing
- [ ] Configure security scanning
- [ ] Add performance benchmarks
- [ ] Implement changelog automation

---

**Note**: After completing the manual setup steps, your package will automatically:
- Publish to TestPyPI on every push to main
- Publish to PyPI when you create a GitHub release
- Run comprehensive tests on multiple Python versions
