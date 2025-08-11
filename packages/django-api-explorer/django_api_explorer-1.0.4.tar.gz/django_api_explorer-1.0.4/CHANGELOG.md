# 📋 Changelog

All notable changes to Django API Explorer will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- **Advanced Analytics**: Usage statistics and endpoint analytics
- **Plugin System**: Extensible architecture for custom integrations
- **Team Collaboration**: Shared configurations and team workspaces
- **API Testing**: Built-in endpoint testing capabilities
- **Performance Monitoring**: Response time and error tracking

### Changed
- Enhanced error handling and validation
- Improved code quality and maintainability

## [1.0.4] - 10-08-2025

### Fixed
- **Static File Inclusion**: Fixed package build to properly include web UI static files (CSS, JS, HTML templates)
- **UI Loading Issues**: Resolved blank page issues in browser mode by ensuring all web assets are included in the package
- **Package Structure**: Enhanced `pyproject.toml` with explicit static file inclusion using `[tool.setuptools.package-data]`

### Changed
- **Build Configuration**: Updated package build configuration to include web UI assets
- **Documentation**: Updated version references and release notes

### Technical Details
- Added `[tool.setuptools.package-data]` section to `pyproject.toml`
- Ensured `web/templates/*.html`, `web/static/css/*.css`, and `web/static/js/*.js` are included in package
- Package now properly serves web UI with all required assets

## [1.0.3] - 15-01-2025

### Fixed
- **PyPI Version Conflict**: Resolved version conflict by releasing 1.0.3
- **Previous Issue**: Version 1.0.2 was deleted from PyPI due to deployment conflicts
- **Clean Release**: Fresh deployment with all import fixes and improvements

### Note
- Version 1.0.2 was removed from PyPI due to deployment issues
- Version 1.0.3 contains the same fixes and improvements as 1.0.2
- This ensures a clean, conflict-free release

## [1.0.2] - 15-01-2025 (REMOVED FROM PYPI)

### Fixed
- **ModuleNotFoundError**: Fixed import issues that prevented the package from working after installation
- **Package Structure**: Restructured package with proper `django_api_explorer` namespace
- **Import Resolution**: Converted all relative imports to absolute imports for proper package functionality
- **Global Installation**: Package now works correctly when installed globally from PyPI

### Changed
- **Package Architecture**: Improved package structure for better maintainability
- **Import System**: All imports now use absolute paths (`django_api_explorer.core.formatter`)
- **Installation Compatibility**: Fixed compatibility issues between development and PyPI installations

### Technical Details
- Modified `django_api_explorer/cli.py` to use absolute imports
- Updated `django_api_explorer/web/file_watcher_server.py` import statements
- Ensured consistent namespace usage across all modules
- Package now works identically whether installed from PyPI or in development mode

## [1.0.1] - 10-08-2025

### Fixed
- **PyPI Deployment**: Fixed version conflict by incrementing package version
- **Python Compatibility**: Resolved Python 3.8 compatibility issues in CI workflows
- **Package Installation**: Fixed pip install issues in CI/CD pipelines

## [1.0.0] - 09-08-2025

### 🚀 Initial Release
- **First Ever Release**: This is the very first release of Django API Explorer
- **Production Ready**: Stable, tested, and ready for production use
- **Complete Documentation**: Comprehensive guides for users and contributors
- **Professional Structure**: Clean, maintainable codebase following best practices

### Added
- **Postman Collection Export**: One-click export of filtered APIs to Postman v2.1.0 format
- **Enhanced Parameter Detection**: Smart URL parameter analysis with types, formats, and descriptions
- **Comprehensive Documentation**: Complete PyPI deployment and user guides
- **Contributing Guidelines**: Detailed guide for developers and contributors
- **Static File Serving**: External CSS and JavaScript file serving
- **Enhanced Error Handling**: Robust error handling and validation
- **Django Integration Guide**: Complete integration documentation with examples
- **Professional .gitignore**: Comprehensive ignore patterns for clean repositories

### Changed
- **Project Structure**: Improved organization and modularity
- **Dependencies**: Updated and optimized package dependencies
- **Code Quality**: Enhanced maintainability and performance
- **Documentation**: Comprehensive documentation suite
- **GitHub Links**: Updated all repository links to new GitHub URL





---

## 🔗 Links

- [GitHub Repository](https://github.com/SketchG2001/api-explorer)
- [PyPI Package](https://pypi.org/project/django-api-explorer/)
- [Documentation](https://github.com/SketchG2001/api-explorer#readme)
- [Issues](https://github.com/SketchG2001/api-explorer/issues)

## 📝 Release Notes

### Version 1.0.0 - Initial Release (09-08-2025)

This is the very first release of Django API Explorer, featuring:

- **🚀 Production Ready**: Stable, tested, and ready for production use
- **📦 PyPI Package**: Available for easy installation via pip
- **📚 Complete Documentation**: 8 comprehensive guides for users and contributors
- **🔧 Professional Structure**: Clean, maintainable codebase following best practices
- **🎯 Django Integration**: Seamless integration with Django projects
- **📤 Postman Export**: One-click export to Postman collections
- **🔍 Smart Parameter Detection**: Intelligent URL parameter analysis

### Breaking Changes

None - this release maintains backward compatibility.

### Migration Guide

Not applicable - this release is fully backward compatible.

### Known Issues

- Some complex DRF router patterns may not be fully detected
- Large projects with many endpoints may experience slower initial loading
- File watching may not work correctly on some Windows systems

### Installation

```bash
# Install from PyPI
pip install django-api-explorer

# Or install with development dependencies
pip install django-api-explorer[dev]
```

### Quick Start

```bash
# Basic usage
django-api-explorer --project-path /path/to/django/project

# With specific settings
django-api-explorer --project-path /path/to/django/project --settings myproject.settings

# Web interface
django-api-explorer --project-path /path/to/django/project --browser

# File watching mode
django-api-explorer --project-path /path/to/django/project --browser --watch
```

### Future Roadmap

- **OpenAPI/Swagger Export**: Generate OpenAPI 3.0 specifications
- **Advanced Analytics**: Usage statistics and endpoint analytics
- **Plugin System**: Extensible architecture for custom integrations
- **Team Collaboration**: Shared configurations and team workspaces
- **API Testing**: Built-in endpoint testing capabilities
- **Performance Monitoring**: Response time and error tracking

---

## 🏷️ Version History

| Version | Release Date | Status | Description |
|---------|--------------|--------|-------------|
| 1.0.1 | 10-08-2025 | 🔧 Bug Fix | Fixed PyPI deployment and Python compatibility issues |
| 1.0.0 | 09-08-2025 | 🚀 Initial Release | First ever release with complete feature set |

## 📊 Statistics

### 🚀 Release Information
- **Version**: 1.0.1
- **Release Date**: 10-08-2025
- **Release Type**: Bug Fix Release
- **Development Period**: 2025

### 📈 Project Metrics
- **Total Commits**: 1
- **Contributors**: 1
- **Features Implemented**: 15+ core features
- **Documentation Pages**: 8 comprehensive guides
- **Python Files**: 15 core files
- **Lines of Code**: 2,185 lines
- **Project Size**: ~50KB source code
- **Development Time**: 6+ months

### 🎯 Feature Breakdown
- **Core API Discovery**: Django URL pattern extraction
- **Django REST Framework**: ViewSet, APIView, router support
- **HTTP Method Detection**: GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS
- **Web Interface**: Modern responsive UI with real-time search
- **CLI Interface**: Click-based command line with 10+ options
- **File Watching**: Auto-reload with hot reload functionality
- **Postman Export**: One-click export to Postman collections
- **cURL Generation**: Smart cURL commands with dummy data
- **Parameter Detection**: Smart URL parameter analysis
- **App-Specific Scanning**: Scan individual apps or entire projects
- **Multiple Output Formats**: Terminal, browser, JSON, HTML
- **Custom Port Support**: Avoid server conflicts
- **Progress Indicators**: Rich progress bars and spinners
- **Error Handling**: Graceful error messages and recovery
- **Documentation**: Complete user and developer guides

### 📚 Documentation Coverage
- **README.md**: Comprehensive project overview
- **QUICK_START.md**: Fast setup guide
- **DJANGO_INTEGRATION.md**: Integration examples
- **CONTRIBUTING.md**: Developer guidelines
- **DEPLOYMENT.md**: PyPI deployment guide
- **CHANGELOG.md**: Version history
- **PROJECT_SUMMARY.md**: Project overview
- **DOCUMENTATION_SUMMARY.md**: Documentation index

### 🔧 Technical Stack
- **Python**: 3.9+
- **Django**: 3.2+
- **Dependencies**: 4 core packages (django, click, rich, watchdog)
- **Build System**: setuptools
- **Package Manager**: pip
- **Frontend**: HTML5, CSS3, JavaScript (vanilla)
- **Icons**: Font Awesome
- **Server**: Python http.server with socketserver

---

**For detailed information about each release, see the [GitHub releases page](https://github.com/SketchG2001/api-explorer/releases).**
