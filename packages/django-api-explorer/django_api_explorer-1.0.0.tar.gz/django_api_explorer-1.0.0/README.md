# 🚀 Django API Explorer

A powerful command-line tool and web interface for discovering, documenting, and testing API endpoints in Django projects. Automatically extracts URL patterns, HTTP methods, and generates ready-to-use cURL commands with comprehensive dummy data.

## ✨ Features

### 🔍 **Smart API Discovery**
- **Automatic URL Pattern Detection**: Parse Django URL patterns and DRF routers
- **HTTP Method Detection**: Support for GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS
- **Django REST Framework Support**: Handle ViewSets, APIViews, and action decorators
- **App-Specific Scanning**: Scan individual Django apps or entire projects
- **URL Parameter Extraction**: Detect path parameters (`{id}`, `<pk>`, `(?P<name>...)`)

### 🎨 **Modern Web Interface**
- **Interactive Dashboard**: Responsive, gradient-based UI with real-time search
- **Shutter System**: Click any API row to see detailed cURL commands
- **Smart Filtering**: Filter by app, method, or search terms
- **Copy Functionality**: One-click copy with visual feedback
- **Auto-reload**: Real-time updates when Django files change

### 🔧 **Developer Workflow**
- **File Watching**: Monitor Django project files for changes
- **Hot Reload**: Automatic UI updates without manual refresh
- **CLI Interface**: Modern Click-based command-line tool
- **Multiple Output Formats**: Terminal, browser, JSON, HTML
- **Custom Ports**: Avoid conflicts with existing servers

### 📊 **Comprehensive Data Generation**
- **Smart cURL Commands**: Replace URL parameters with sample values
- **Dummy Data**: Context-aware payloads for all endpoint types
- **Authentication Headers**: Realistic JWT tokens and API keys
- **Complete Coverage**: Include all fields, even optional ones
- **Shell Compatibility**: Properly escaped for terminal use

### 📤 **Postman Integration**
- **One-Click Export**: Export filtered APIs to Postman collection
- **Smart Organization**: Group requests by Django app
- **Environment Variables**: Pre-configured base URL and auth tokens
- **Parameter Handling**: Convert URL parameters to Postman variables
- **Sample Data**: Include request bodies for POST/PUT/PATCH
- **Filter-Based Export**: Export only selected APIs

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd api-exporer

# Install dependencies
pip install -r requirements.txt

# Or using pipenv
pipenv install
```

### Basic Usage

```bash
# Scan all apps in current Django project
python cli.py --browser

# Scan specific app
python cli.py --app users --browser

# Use custom Django settings
python cli.py --settings myproject.settings.dev --browser

# Enable file watching for auto-reload
python cli.py --app users --browser --watch

# Use custom port to avoid conflicts
python cli.py --app users --browser --watch --port 8005
```

### Advanced Usage

```bash
# Export as JSON
python cli.py --json -o apis.json

# Generate cURL commands for terminal
python cli.py --curl

# Specify custom host
python cli.py --host https://api.example.com --browser

# Scan from different project directory
python cli.py --project-root /path/to/django/project --browser
```

## 📖 Detailed Documentation

### Command Line Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--project-root` | `-p` | Django project root path | Current directory |
| `--settings` | `-s` | Django settings module | Auto-detect |
| `--app` | `-a` | Scan specific Django app | All apps |
| `--browser` | `-b` | Open results in browser | Terminal output |
| `--watch` | `-w` | Watch for file changes | Disabled |
| `--curl` | | Generate cURL commands | Plain URLs |
| `--json` | `-j` | Output in JSON format | Text format |
| `--output` | `-o` | Save output to file | Console output |
| `--host` | | Override host URL | From ALLOWED_HOSTS |
| `--port` | | Web server port | 8001 |

### Web Interface Features

#### **Interactive Dashboard**
- **Real-time Search**: Filter endpoints by path, method, or app name
- **App Filtering**: Dropdown to filter by Django app
- **Statistics**: View total endpoints, methods, and apps
- **Responsive Design**: Works on desktop and mobile devices

#### **Shutter System**
- **Inline Details**: Opens directly below the clicked API row
- **Method Separation**: cURL commands grouped by HTTP method
- **Copy Buttons**: One-click copy with visual feedback
- **Smart Highlighting**: Visual feedback for selected endpoints

#### **cURL Generation**
- **Parameter Replacement**: URL parameters replaced with sample values
- **Comprehensive Headers**: Authentication, Content-Type, User-Agent, etc.
- **Dummy Data**: Context-aware sample payloads for POST/PUT requests
- **Shell Compatibility**: Properly escaped for terminal use

#### **Postman Export**
- **One-Click Export**: Export button in the top-right corner
- **Filter-Based Export**: Only exports currently filtered endpoints
- **Smart Collection Naming**: Names based on active filters
- **App Organization**: Groups requests by Django app
- **Environment Variables**: Pre-configured `base_url`, `auth_token`, `api_key`
- **Parameter Variables**: URL parameters converted to Postman variables
- **Sample Data**: Includes request bodies for POST/PUT/PATCH methods
- **Download Ready**: Direct download as `.json` file

### File Watching & Auto-Reload

The file watcher monitors your Django project for changes and automatically reloads the UI:

```bash
# Enable file watching
python cli.py --browser --watch

# Use custom port
python cli.py --browser --watch --port 8005
```

**Monitored Files:**
- `*.py` - Python files
- `urls.py` - URL configurations
- `views.py` - View files
- `models.py` - Model files
- `serializers.py` - DRF serializers
- `settings.py` - Settings files

**Ignored Files:**
- `__pycache__/`
- `*.pyc`
- `.git/`
- `node_modules/`
- `.venv/`, `venv/`, `env/`
- `.pytest_cache/`
- `migrations/`

### Django Integration

#### **Project Setup**
The Django API Explorer integrates seamlessly with your Django project:

```bash
# Navigate to your Django project root
cd /path/to/your/django/project

# Run the explorer from your project directory
python /path/to/api-explorer/cli.py --browser

# Or install it as a package and run from anywhere
pip install django-api-explorer
django-api-explorer --browser
```

#### **Settings Loading**
The tool automatically detects and loads Django settings:

```python
# Auto-detection order:
1. Current directory settings
2. Specified --settings module
3. Fallback to minimal settings

# Example with custom settings
python cli.py --settings myproject.settings.dev --browser
```

#### **Host Detection**
Extracts hosts from Django's `ALLOWED_HOSTS` setting:

```python
# From settings.py
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'api.example.com']

# Tool will use: http://127.0.0.1:8000 (fallback)
```

#### **App Discovery**
Automatically discovers installed Django apps:

```python
# From settings.py
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'myapp',
    'api',
]
```

#### **URL Pattern Integration**
Works with all Django URL pattern types:

```python
# urls.py - Main project URLs
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from myapp.views import UserViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/', include('myapp.urls')),
]

# myapp/urls.py - App-specific URLs
from django.urls import path
from . import views

urlpatterns = [
    path('users/', views.UserListView.as_view(), name='user-list'),
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='user-detail'),
]
```

#### **Django REST Framework Integration**
Fully supports DRF patterns and conventions:

```python
# views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        user = self.get_object()
        user.is_active = True
        user.save()
        return Response({'status': 'activated'})

# The explorer will detect:
# - GET /api/users/ (list)
# - POST /api/users/ (create)
# - GET /api/users/{id}/ (retrieve)
# - PUT /api/users/{id}/ (update)
# - DELETE /api/users/{id}/ (destroy)
# - POST /api/users/{id}/activate/ (custom action)
```

### cURL Command Generation

The tool generates comprehensive cURL commands with:

#### **URL Parameter Replacement**
```bash
# Original URL: /api/users/{id}/profile/{field}
# Generated: /api/users/1/profile/email
```

#### **Authentication Headers**
```bash
# JWT Token
-H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# API Key
-H "X-API-Key: api_key_123456789abcdef"

# Client ID
-H "X-Client-ID: client_987654321fedcba"
```

#### **Sample Data Generation**
```json
{
  "name": "Premium Gaming Campaign 2024",
  "description": "High-performance gaming campaign",
  "budget": 50000.00,
  "start_date": "2024-01-01",
  "end_date": "2024-12-31",
  "target_audience": {
    "age_range": "18-35",
    "interests": ["gaming", "technology"],
    "location": "Worldwide"
  }
}
```

## 🏗️ Project Structure

```
api-exporer/
├── cli.py                 # Main command-line interface
├── requirements.txt       # Python dependencies
├── README.md             # This documentation
├── pyproject.toml        # Project metadata
├── MANIFEST.in           # Package manifest
├── core/                 # Core functionality
│   ├── __init__.py
│   ├── url_extractor.py  # URL pattern extraction
│   ├── method_detector.py # HTTP method detection
│   ├── settings_loader.py # Django settings loading
│   ├── formatter.py      # Output formatting
│   └── models.py         # Data models
├── web/                  # Web interface
│   ├── __init__.py
│   ├── enhanced_server.py # Enhanced HTTP server
│   ├── file_watcher_server.py # File watching server
│   └── templates/
│       └── enhanced_index.html # Main UI template
├── utils/                # Utility functions
│   ├── __init__.py
│   └── path_utils.py     # Path utilities
└── tests/                # Test suite
    ├── __init__.py
    ├── test_basic.py     # Basic functionality tests
    └── test_url_extractor.py # URL extraction tests
```

## 🔧 Development

### Setup Development Environment

```bash
# Clone and setup
git clone <repository-url>
cd api-exporer

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest black flake8
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_basic.py

# Run with coverage
pytest --cov=core --cov=web
```

### Code Quality

```bash
# Format code
black .

# Lint code
flake8 .

# Type checking (if using mypy)
mypy .
```

## 🐛 Troubleshooting

### Common Issues

#### **Port Already in Use**
```bash
# Error: OSError: [Errno 48] Address already in use
# Solution: Use different port
python cli.py --browser --port 8005
```

#### **Django Settings Not Found**
```bash
# Error: Error loading Django settings
# Solution: Specify settings module
python cli.py --settings myproject.settings.dev --browser
```

#### **Module Import Errors**
```bash
# Error: No module named 'some_module'
# Solution: Activate Django project's virtual environment
cd /path/to/django/project
pipenv run python /path/to/api-exporer/cli.py --browser
```

#### **JavaScript Errors in Browser**
```bash
# Check browser console for errors
# Common fix: Clear browser cache and reload
```

### Debug Mode

Enable debug output for troubleshooting:

```bash
# Set debug environment variable
export DEBUG=1
python cli.py --browser

# Or modify cli.py to add debug logging
```

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Guidelines

- **Code Style**: Follow PEP 8 and use Black for formatting
- **Testing**: Add tests for new features
- **Documentation**: Update README.md for new features
- **Type Hints**: Use type hints for function parameters and return values

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/SketchG2001/api-explorer/blob/main/LICENSE) file for details.

## 🙏 Acknowledgments

- **Django**: For the amazing web framework
- **Django REST Framework**: For API development tools
- **Click**: For the command-line interface
- **Rich**: For beautiful terminal output
- **Watchdog**: For file system monitoring

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/SketchG2001/api-explorer/issues)
- **Discussions**: [GitHub Discussions](https://github.com/SketchG2001/api-explorer/discussions)
- **Email**: vikasgole089@gmail.com

---

**Made with ❤️ for the Django community**
