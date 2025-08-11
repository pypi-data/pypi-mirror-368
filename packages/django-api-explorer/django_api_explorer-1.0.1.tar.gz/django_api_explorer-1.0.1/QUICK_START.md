# ⚡ Quick Start Guide

Get up and running with Django API Explorer in minutes!

## 🚀 Installation

### From PyPI (Recommended)

```bash
# Install the package
pip install django-api-explorer

# Or with pipenv
pipenv install django-api-explorer
```

### From Source

```bash
# Clone the repository
git clone https://github.com/SketchG2001/api-explorer.git
cd django-api-explorer

# Install in development mode
pip install -e .
```

## 🎯 Basic Usage

### 1. Navigate to Your Django Project

```bash
cd /path/to/your/django/project
```

### 2. Run the Explorer

```bash
# Scan all apps and open in browser
django-api-explorer --browser

# Scan specific app
django-api-explorer --app users --browser

# Use custom Django settings
django-api-explorer --settings myproject.settings.dev --browser
```

### 3. Enable File Watching (Optional)

```bash
# Auto-reload when files change
django-api-explorer --browser --watch

# Use custom port
django-api-explorer --browser --watch --port 8005
```

## 🎨 Web Interface Features

### Interactive Dashboard
- **Real-time Search**: Filter endpoints by path, method, or app
- **App Filtering**: Dropdown to filter by Django app
- **Statistics**: View total endpoints, methods, and apps

### Shutter System
- **Click any API row** to see detailed cURL commands
- **Method separation**: Commands grouped by HTTP method
- **Copy buttons**: One-click copy with visual feedback

### Smart cURL Generation
- **Parameter replacement**: URL params replaced with sample values
- **Comprehensive headers**: Auth, Content-Type, User-Agent, etc.
- **Dummy data**: Context-aware payloads for POST/PUT requests

## 🔧 Advanced Usage

### Command Line Options

```bash
# Basic scanning
django-api-explorer                    # Terminal output
django-api-explorer --curl             # Generate cURL commands
django-api-explorer --json -o apis.json # Export as JSON

# Web interface
django-api-explorer --browser          # Open in browser
django-api-explorer --browser --watch  # With file watching

# Custom configuration
django-api-explorer --project-root /path/to/project
django-api-explorer --settings myproject.settings.prod
django-api-explorer --host https://api.example.com
django-api-explorer --port 8005
```

### Examples

#### Scan Specific App
```bash
django-api-explorer --app users --browser
```

#### Export to JSON
```bash
django-api-explorer --json -o api_documentation.json
```

#### Generate cURL Commands
```bash
django-api-explorer --curl > curl_commands.sh
```

#### Custom Host and Port
```bash
django-api-explorer --host https://api.example.com --port 8005 --browser
```

## 🐛 Troubleshooting

### Common Issues

#### **Port Already in Use**
```bash
# Use different port
django-api-explorer --browser --port 8005
```

#### **Django Settings Not Found**
```bash
# Specify settings module
django-api-explorer --settings myproject.settings.dev --browser
```

#### **Module Import Errors**
```bash
# Activate Django project's virtual environment
cd /path/to/django/project
pipenv run django-api-explorer --browser
```

#### **Permission Errors**
```bash
# Install with user flag
pip install --user django-api-explorer
```

### Getting Help

```bash
# Show help
django-api-explorer --help

# Show version
django-api-explorer --version
```

## 📚 Next Steps

- **Read the full documentation**: [README.md](README.md)
- **Check examples**: [Examples directory](examples/)
- **Report issues**: [GitHub Issues](https://github.com/SketchG2001/api-explorer/issues)
- **Contribute**: [Contributing Guide](CONTRIBUTING.md)

## 🎉 What You Get

✅ **Automatic API Discovery**: Find all endpoints in your Django project
✅ **Modern Web Interface**: Beautiful, responsive UI
✅ **Smart cURL Generation**: Ready-to-use commands with dummy data
✅ **File Watching**: Auto-reload when files change
✅ **Multiple Output Formats**: Terminal, browser, JSON, HTML
✅ **Django REST Framework Support**: ViewSets, APIViews, routers

---

**🚀 Ready to explore your Django APIs? Run `django-api-explorer --browser` and start discovering!**
