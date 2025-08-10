# 🚀 Deployment Guide

This guide covers deploying Django API Explorer to PyPI and managing releases.

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [PyPI Account Setup](#pypi-account-setup)
- [Build Configuration](#build-configuration)
- [Testing Build](#testing-build)
- [PyPI Deployment](#pypi-deployment)
- [Release Management](#release-management)
- [CI/CD Setup](#cicd-setup)
- [Troubleshooting](#troubleshooting)

## 🔧 Prerequisites

### Required Tools

```bash
# Install build tools
pip install build twine

# Install development tools
pip install pytest black flake8 mypy

# Install documentation tools
pip install sphinx sphinx-rtd-theme
```

### Python Version Support

- **Python**: 3.8, 3.9, 3.10, 3.11, 3.12
- **Django**: 3.2, 4.0, 4.1, 4.2, 5.0
- **Platforms**: macOS, Linux, Windows

## 📦 PyPI Account Setup

### 1. Create PyPI Account

1. **Visit PyPI**: https://pypi.org/account/register/
2. **Create account**: Use a strong password
3. **Verify email**: Check your email for verification
4. **Enable 2FA**: Recommended for security

### 2. Create TestPyPI Account (Optional)

1. **Visit TestPyPI**: https://test.pypi.org/account/register/
2. **Create account**: Same process as PyPI
3. **Use for testing**: Test releases before PyPI

### 3. Configure Credentials

```bash
# Create .pypirc file in your home directory
touch ~/.pypirc

# Add configuration
cat > ~/.pypirc << EOF
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
repository = https://pypi.org/pypi
username = your-pypi-username
password = your-pypi-password

[testpypi]
repository = https://test.pypi.org/legacy/
username = your-testpypi-username
password = your-testpypi-password
EOF

# Set proper permissions
chmod 600 ~/.pypirc
```

## ⚙️ Build Configuration

### 1. Update pyproject.toml

Ensure your `pyproject.toml` is properly configured:

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "django-api-explorer"
version = "0.1.0"
description = "A powerful command-line tool and web interface for discovering, documenting, and testing API endpoints in Django projects"
readme = "README.md"
requires-python = ">=3.8"
license = {text = "MIT"}
authors = [
    {name = "Your Name", email = "vikasgole089@gmail.com"}
]
keywords = ["django", "api", "documentation", "discovery", "endpoints", "rest", "framework"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Framework :: Django",
    "Framework :: Django :: 3.2",
    "Framework :: Django :: 4.0",
    "Framework :: Django :: 4.1",
    "Framework :: Django :: 4.2",
    "Framework :: Django :: 5.0",
    "Topic :: Software Development :: Documentation",
    "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Operating System :: OS Independent",
    "Environment :: Console",
    "Environment :: Web Environment",
]

dependencies = [
    "django>=3.2,<5.1",
    "click>=8.0.0",
    "rich>=12.0.0",
    "watchdog>=3.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-django>=4.5.0",
    "black>=22.0.0",
    "flake8>=5.0.0",
    "mypy>=1.0.0",
    "pre-commit>=2.20.0",
    "build>=0.10.0",
    "twine>=4.0.0",
]

docs = [
    "sphinx>=5.0.0",
    "sphinx-rtd-theme>=1.0.0",
    "myst-parser>=0.18.0",
]

[project.scripts]
django-api-explorer = "cli:main"

[project.urls]
Homepage = "https://github.com/SketchG2001/api-explorer"
Repository = "https://github.com/SketchG2001/api-explorer"
Documentation = "https://github.com/SketchG2001/api-explorer#readme"
Issues = "https://github.com/SketchG2001/api-explorer/issues"
Changelog = "https://github.com/SketchG2001/api-explorer/blob/main/CHANGELOG.md"

[tool.setuptools.packages.find]
where = ["."]
include = ["core*", "utils*", "web*"]

[tool.setuptools.package-data]
"*" = ["*.html", "*.css", "*.js"]

[tool.black]
line-length = 88
target-version = ['py38']

[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

### 2. Update MANIFEST.in

Ensure `MANIFEST.in` includes all necessary files:

```ini
include README.md
include CHANGELOG.md
include CONTRIBUTING.md
include LICENSE
include requirements.txt
include pyproject.toml

recursive-include web/templates *.html
recursive-include web/static *.css *.js

global-exclude *.pyc
global-exclude __pycache__
global-exclude .git*
global-exclude .DS_Store
global-exclude *.egg-info
```

## 🧪 Testing Build

### 1. Clean Previous Builds

```bash
# Remove previous builds
rm -rf build/ dist/ *.egg-info/

# Clean Python cache
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete
```

### 2. Test Build Locally

```bash
# Build the package
python -m build

# Check the built package
ls -la dist/

# Test installation in virtual environment
python -m venv test_env
source test_env/bin/activate  # On Windows: test_env\Scripts\activate
pip install dist/django_api_explorer-0.1.0.tar.gz

# Test the command
django-api-explorer --help
```

### 3. Validate Package

```bash
# Check package with twine
twine check dist/*

# Test upload to TestPyPI (optional)
twine upload --repository testpypi dist/*
```

## 📤 PyPI Deployment

### 1. Prepare Release

```bash
# Ensure all tests pass
pytest

# Run code quality checks
black --check .
flake8 .
mypy .

# Update version in pyproject.toml
# Update CHANGELOG.md
# Commit changes
git add .
git commit -m "chore: prepare release v0.1.0"
git tag -a v0.1.0 -m "Release v0.1.0"
git push origin main --tags
```

### 2. Build Package

```bash
# Clean and build
rm -rf build/ dist/ *.egg-info/
python -m build
```

### 3. Upload to PyPI

```bash
# Upload to PyPI
twine upload dist/*

# Verify upload
pip install django-api-explorer --upgrade
django-api-explorer --version
```

## 🏷️ Release Management

### 1. Version Numbering

Follow [Semantic Versioning](https://semver.org/):

- **MAJOR.MINOR.PATCH**
- **MAJOR**: Incompatible API changes
- **MINOR**: New functionality (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### 2. Release Checklist

- [ ] **Update version** in `pyproject.toml`
- [ ] **Update CHANGELOG.md** with new version
- [ ] **Run all tests** and ensure they pass
- [ ] **Check code quality** (black, flake8, mypy)
- [ ] **Build package** and test locally
- [ ] **Create Git tag** for the release
- [ ] **Upload to PyPI**
- [ ] **Create GitHub release** with release notes
- [ ] **Update documentation** if needed

### 3. GitHub Release

1. **Go to GitHub**: https://github.com/SketchG2001/api-explorer/releases
2. **Create new release**: Click "Create a new release"
3. **Choose tag**: Select the version tag (e.g., v0.1.0)
4. **Add title**: "Release v0.1.0"
5. **Add description**: Copy from CHANGELOG.md
6. **Upload assets**: Attach built packages (optional)
7. **Publish release**

## 🔄 CI/CD Setup

### 1. GitHub Actions Workflow

Create `.github/workflows/release.yml`:

```yaml
name: Release to PyPI

on:
  push:
    tags:
      - 'v*'

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, 3.10, 3.11, 3.12]
        django-version: [3.2, 4.0, 4.1, 4.2, 5.0]

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-django
    
    - name: Run tests
      run: |
        pytest
    
    - name: Run code quality checks
      run: |
        pip install black flake8 mypy
        black --check .
        flake8 .
        mypy .

  build-and-publish:
    needs: test
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: 3.11
    
    - name: Install build dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine
    
    - name: Build package
      run: python -m build
    
    - name: Check package
      run: twine check dist/*
    
    - name: Publish to PyPI
      env:
        TWINE_USERNAME: ${{ secrets.PYPI_USERNAME }}
        TWINE_PASSWORD: ${{ secrets.PYPI_PASSWORD }}
      run: twine upload dist/*
```

### 2. GitHub Secrets

Add these secrets to your GitHub repository:

- `PYPI_USERNAME`: Your PyPI username
- `PYPI_PASSWORD`: Your PyPI password (or API token)

### 3. Automated Testing

Create `.github/workflows/test.yml`:

```yaml
name: Test

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, 3.10, 3.11, 3.12]

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-django black flake8 mypy
    
    - name: Run tests
      run: pytest
    
    - name: Run code quality checks
      run: |
        black --check .
        flake8 .
        mypy .
```

## 🐛 Troubleshooting

### Common Issues

#### **1. Build Errors**

```bash
# Error: No module named 'setuptools'
pip install --upgrade setuptools wheel

# Error: Invalid package name
# Check pyproject.toml name field (use hyphens, not underscores)
```

#### **2. Upload Errors**

```bash
# Error: File already exists
# Increment version number in pyproject.toml

# Error: Authentication failed
# Check ~/.pypirc credentials
# Use API token instead of password
```

#### **3. Import Errors**

```bash
# Error: Module not found after installation
# Check MANIFEST.in includes all necessary files
# Verify package structure in pyproject.toml
```

#### **4. Version Conflicts**

```bash
# Error: Version conflict with existing package
# Use different package name or version
# Check PyPI for existing packages
```

### Debug Commands

```bash
# Check package contents
tar -tzf dist/django_api_explorer-0.1.0.tar.gz

# Test installation
pip install --force-reinstall dist/django_api_explorer-0.1.0.tar.gz

# Check installed package
pip show django-api-explorer

# Test command
django-api-explorer --help
```

## 📚 Additional Resources

- [PyPI Packaging Guide](https://packaging.python.org/tutorials/packaging-projects/)
- [setuptools Documentation](https://setuptools.pypa.io/en/latest/)
- [Twine Documentation](https://twine.readthedocs.io/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

---

**🎉 Congratulations! Your Django API Explorer is now ready for PyPI deployment!**
