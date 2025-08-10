# ReqNinja PyPI Publishing Guide

## 📦 Publishing to PyPI

ReqNinja is ready for PyPI publication! Here's how to publish it:

### Prerequisites

1. **PyPI Account**: Create accounts on:
   - [PyPI](https://pypi.org/account/register/) (production)
   - [TestPyPI](https://test.pypi.org/account/register/) (testing)

2. **API Tokens**: Generate API tokens for secure uploading:
   - Go to Account Settings → API tokens
   - Create tokens for both PyPI and TestPyPI

### Step 1: Test on TestPyPI First

```bash
# Upload to TestPyPI first
twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ reqninja
```

### Step 2: Publish to Production PyPI

```bash
# Upload to PyPI
twine upload dist/*

# Test the production installation
pip install reqninja
```

### Step 3: Verify Installation

```bash
# Test CLI
reqninja --version
reqninja http get https://httpbin.org/get

# Test Python API
python -c "import reqninja; print('✅ ReqNinja installed successfully!')"
```

## 🔐 Security Setup

### Using API Tokens

1. Create `.pypirc` file in your home directory:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-your-api-token-here

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-your-test-api-token-here
```

2. Set proper permissions:
```bash
chmod 600 ~/.pypirc
```

### Environment Variables

Alternative method using environment variables:

```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-your-api-token-here
twine upload dist/*
```

## 🚀 Automated Publishing

### GitHub Actions (Already Set Up)

The repository includes `.github/workflows/publish.yml` that automatically publishes to PyPI when you create a release tag:

```bash
git tag v1.0.0
git push origin v1.0.0
```

This will:
1. Run all tests
2. Build the package
3. Upload to PyPI automatically

## 📋 Pre-Publication Checklist

✅ **Package Quality**
- [x] All tests passing (24/24)
- [x] Code quality checks pass
- [x] Documentation complete
- [x] Examples working
- [x] CLI and API functional

✅ **PyPI Requirements**
- [x] Package builds successfully
- [x] Twine check passes
- [x] README.md displays properly
- [x] License included
- [x] Proper version numbering
- [x] Entry points configured

✅ **Testing**
- [x] Package installs correctly
- [x] CLI commands work
- [x] Python API imports
- [x] Dependencies resolve

## 🎯 Post-Publication Steps

After successful publication:

1. **Update README.md** - Change installation instructions to:
   ```bash
   pip install reqninja
   ```

2. **Create GitHub Release** - Create a proper GitHub release with:
   - Release notes
   - Installation instructions
   - Feature highlights

3. **Documentation** - Set up documentation site (optional):
   - GitHub Pages
   - Read the Docs
   - Custom domain

4. **Community** - Announce the release:
   - GitHub Discussions
   - Python community forums
   - Social media

## 🔄 Future Releases

For future versions:

1. Update version in `pyproject.toml` or use git tags
2. Update CHANGELOG.md
3. Run tests
4. Build and upload:
   ```bash
   python -m build
   twine upload dist/*
   ```

## 📊 Package Status

Current build status:
- **Version**: 1.0.1.dev0+g8c7ec6b.d20250810 (ready for v1.0.0 release)
- **Python Support**: 3.8+
- **Platform**: Cross-platform (Windows, macOS, Linux)
- **Dependencies**: All available on PyPI
- **Size**: ~16KB wheel, ~34KB source

ReqNinja is production-ready and ready for the world! 🌟
