# 🤝 Contributing to Django API Explorer

Thank you for your interest in contributing to Django API Explorer! This document provides guidelines and information for contributors.

## 📋 Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Code Style](#code-style)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Feature Development](#feature-development)
- [Bug Reports](#bug-reports)
- [Documentation](#documentation)

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- A Django project for testing (optional but recommended)

### Fork and Clone

1. **Fork the repository** on GitHub
2. **Clone your fork**:
   ```bash
   git clone https://github.com/SketchG2001/api-explorer.git
   cd django-api-explorer
   ```

3. **Add the upstream remote**:
   ```bash
   git remote add upstream https://github.com/SketchG2001/api-explorer.git
   ```

## 🔧 Development Setup

### 1. Create Virtual Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate
```

### 2. Install Dependencies

```bash
# Install development dependencies
pip install -r requirements.txt

# Install additional development tools
pip install pytest black flake8 mypy pre-commit
```

### 3. Install Pre-commit Hooks

```bash
# Install pre-commit hooks
pre-commit install

# Run pre-commit on all files
pre-commit run --all-files
```

### 4. Test Your Setup

```bash
# Run tests
pytest

# Test the CLI
python cli.py --help
```

## 📝 Code Style

### Python Code Style

We follow **PEP 8** with some modifications:

- **Line length**: 88 characters (Black default)
- **Import sorting**: Use `isort` or Black's import sorting
- **Type hints**: Use type hints for all function parameters and return values
- **Docstrings**: Use Google-style docstrings

### Code Formatting

We use **Black** for code formatting:

```bash
# Format all Python files
black .

# Check formatting without making changes
black --check .
```

### Linting

We use **flake8** for linting:

```bash
# Run flake8
flake8 .

# Run with specific configuration
flake8 --max-line-length=88 --extend-ignore=E203,W503 .
```

### Type Checking

We use **mypy** for type checking:

```bash
# Run mypy
mypy .

# Run with specific configuration
mypy --ignore-missing-imports --disallow-untyped-defs .
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=core --cov=web --cov-report=html

# Run specific test file
pytest tests/test_basic.py

# Run with verbose output
pytest -v

# Run tests in parallel
pytest -n auto
```

### Writing Tests

- **Test files**: Place in `tests/` directory
- **Test naming**: Use descriptive test names
- **Test structure**: Use `pytest` fixtures and parametrize when appropriate
- **Coverage**: Aim for at least 80% code coverage

### Example Test

```python
import pytest
from core.models import APIEndpoint, APIMethod

def test_api_endpoint_creation():
    """Test creating an APIEndpoint."""
    endpoint = APIEndpoint(
        path="/api/users/",
        name="User List",
        app_name="users",
        methods=[APIMethod.GET, APIMethod.POST]
    )
    
    assert endpoint.path == "/api/users/"
    assert endpoint.name == "User List"
    assert endpoint.app_name == "users"
    assert len(endpoint.methods) == 2
    assert APIMethod.GET in endpoint.methods
    assert APIMethod.POST in endpoint.methods
```

## 🔄 Pull Request Process

### 1. Create a Feature Branch

```bash
# Create and switch to a new branch
git checkout -b feature/amazing-feature

# Or for bug fixes
git checkout -b fix/bug-description
```

### 2. Make Your Changes

- Write your code following the style guidelines
- Add tests for new functionality
- Update documentation as needed
- Ensure all tests pass

### 3. Commit Your Changes

```bash
# Add your changes
git add .

# Commit with a descriptive message
git commit -m "feat: add new feature for better API discovery

- Add support for custom URL patterns
- Improve method detection accuracy
- Add comprehensive tests
- Update documentation"
```

### 4. Push and Create Pull Request

```bash
# Push to your fork
git push origin feature/amazing-feature
```

Then create a Pull Request on GitHub with:

- **Clear title**: Describe the change concisely
- **Detailed description**: Explain what, why, and how
- **Related issues**: Link to any related issues
- **Screenshots**: If UI changes are involved

### 5. Pull Request Review

- **Code review**: Address reviewer comments
- **CI/CD checks**: Ensure all checks pass
- **Documentation**: Update README.md if needed
- **Testing**: Ensure all tests pass

## 🚀 Feature Development

### Before Starting

1. **Check existing issues**: Look for similar features or bugs
2. **Create an issue**: Discuss the feature before implementing
3. **Plan the implementation**: Consider architecture and design
4. **Update roadmap**: If applicable

### Development Guidelines

#### **Core Features**
- **Location**: `core/` directory
- **Testing**: Comprehensive unit tests
- **Documentation**: Update docstrings and README
- **Backward compatibility**: Maintain compatibility when possible

#### **Web Interface**
- **Location**: `web/` directory
- **Testing**: Test both server and client-side functionality
- **Responsive design**: Ensure mobile compatibility
- **Accessibility**: Follow WCAG guidelines

#### **CLI Interface**
- **Location**: `cli.py`
- **Testing**: Test all command-line options
- **Help text**: Provide clear help messages
- **Error handling**: Graceful error messages

### Example Feature Implementation

```python
# core/new_feature.py
from typing import List, Dict, Any
from .models import APIEndpoint

def new_feature_function(endpoints: List[APIEndpoint]) -> Dict[str, Any]:
    """
    New feature that processes API endpoints.
    
    Args:
        endpoints: List of APIEndpoint objects to process
        
    Returns:
        Dictionary containing processed results
        
    Raises:
        ValueError: If endpoints list is empty
    """
    if not endpoints:
        raise ValueError("Endpoints list cannot be empty")
    
    # Implementation here
    return {"processed": len(endpoints)}
```

## 🐛 Bug Reports

### Before Reporting

1. **Check existing issues**: Search for similar bugs
2. **Reproduce the issue**: Ensure it's reproducible
3. **Check documentation**: Verify it's not a usage issue
4. **Test with minimal setup**: Isolate the problem

### Bug Report Template

```markdown
## Bug Description
Brief description of the bug

## Steps to Reproduce
1. Step 1
2. Step 2
3. Step 3

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS: [e.g., macOS 12.0]
- Python: [e.g., 3.9.7]
- Django: [e.g., 4.0.2]
- Django API Explorer: [e.g., 0.1.0]

## Additional Information
- Error messages
- Screenshots
- Logs
```

## 📚 Documentation

### Documentation Standards

- **README.md**: Main project documentation
- **Docstrings**: Google-style docstrings for all functions
- **Type hints**: Use type hints for better IDE support
- **Examples**: Include usage examples

### Updating Documentation

When updating documentation:

1. **README.md**: Update for user-facing changes
2. **Docstrings**: Update for API changes
3. **Examples**: Ensure examples work with current version
4. **Changelog**: Update CHANGELOG.md for releases

### Documentation Structure

```
docs/
├── README.md              # Main documentation
├── CONTRIBUTING.md        # This file
├── CHANGELOG.md           # Release history
├── API.md                 # API documentation
├── DEPLOYMENT.md          # Deployment guide
└── examples/              # Usage examples
    ├── basic_usage.py
    ├── advanced_usage.py
    └── custom_integration.py
```

## 🏷️ Versioning

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR**: Incompatible API changes
- **MINOR**: New functionality (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Process

1. **Update version**: Update version in `pyproject.toml`
2. **Update changelog**: Add entry to `CHANGELOG.md`
3. **Create release branch**: `git checkout -b release/v1.2.3`
4. **Test thoroughly**: Run all tests and manual testing
5. **Create tag**: `git tag -a v1.2.3 -m "Release v1.2.3"`
6. **Push changes**: `git push origin release/v1.2.3 --tags`
7. **Create GitHub release**: With release notes

## 🎯 Areas for Contribution

### High Priority
- **Bug fixes**: Any reported bugs
- **Documentation**: Improving existing docs
- **Tests**: Increasing test coverage
- **Performance**: Optimizing slow operations

### Medium Priority
- **New features**: Based on roadmap
- **UI improvements**: Web interface enhancements
- **CLI enhancements**: New command-line options
- **Integration**: Support for more frameworks

### Low Priority
- **Code refactoring**: Improving code structure
- **Style improvements**: Code formatting and linting
- **Examples**: Additional usage examples
- **Translations**: Internationalization support

## 📞 Getting Help

### Communication Channels

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and discussions
- **Pull Requests**: For code contributions
- **Email**: For private or sensitive matters

### Code of Conduct

- **Be respectful**: Treat all contributors with respect
- **Be inclusive**: Welcome contributors from all backgrounds
- **Be constructive**: Provide constructive feedback
- **Be patient**: Allow time for review and discussion

## 🙏 Recognition

Contributors will be recognized in:

- **README.md**: Contributors section
- **CHANGELOG.md**: For significant contributions
- **GitHub**: Contributor statistics
- **Releases**: Release notes

---

**Thank you for contributing to Django API Explorer! 🚀**

Your contributions help make this tool better for the entire Django community.
