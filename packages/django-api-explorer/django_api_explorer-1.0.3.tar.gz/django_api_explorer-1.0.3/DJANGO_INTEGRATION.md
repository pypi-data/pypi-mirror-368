# 🔗 Django Integration Guide

A comprehensive guide on how to integrate Django API Explorer with your Django projects.

## 📋 Table of Contents

- [Quick Integration](#-quick-integration)
- [Project Structure](#-project-structure)
- [URL Configuration](#-url-configuration)
- [Django REST Framework](#-django-rest-framework)
- [Authentication & Permissions](#-authentication--permissions)
- [Custom Views](#-custom-views)
- [Advanced Configuration](#-advanced-configuration)
- [Troubleshooting](#-troubleshooting)

## 🚀 Quick Integration

### Step 1: Install Django API Explorer

```bash
# Option 1: Install from PyPI (recommended)
pip install django-api-explorer

# Option 2: Install from source
git clone https://github.com/SketchG2001/api-explorer.git
cd django-api-explorer
pip install -e .
```

### Step 2: Navigate to Your Django Project

```bash
cd /path/to/your/django/project
```

### Step 3: Run the Explorer

```bash
# Basic usage - scan all apps
django-api-explorer --browser

# Scan specific app
django-api-explorer --app myapp --browser

# Use custom settings
django-api-explorer --settings myproject.settings.dev --browser

# Enable file watching
django-api-explorer --browser --watch
```

## 🏗️ Project Structure

The Django API Explorer works with any standard Django project structure:

```
myproject/
├── manage.py
├── myproject/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── myapp/
│   ├── __init__.py
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── serializers.py
└── requirements.txt
```

### Supported Django Versions

- **Django 3.2+** (LTS versions)
- **Django 4.0+** (Current versions)
- **Django 5.0+** (Latest versions)

## 🔗 URL Configuration

### Main Project URLs (`myproject/urls.py`)

```python
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from myapp.views import UserViewSet, ProductViewSet

# DRF Router
router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'products', ProductViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/', include('myapp.urls')),
    path('api/', include('auth.urls')),
]
```

### App-Specific URLs (`myapp/urls.py`)

```python
from django.urls import path
from . import views

urlpatterns = [
    # Function-based views
    path('hello/', views.hello_world, name='hello'),
    
    # Class-based views
    path('users/', views.UserListView.as_view(), name='user-list'),
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='user-detail'),
    
    # DRF APIViews
    path('products/', views.ProductListAPIView.as_view(), name='product-list'),
    path('products/<int:pk>/', views.ProductDetailAPIView.as_view(), name='product-detail'),
    
    # Custom patterns with parameters
    path('search/<str:query>/', views.SearchView.as_view(), name='search'),
    path('users/<int:user_id>/posts/<int:post_id>/', views.UserPostView.as_view(), name='user-post'),
]
```

### URL Pattern Types Supported

```python
# Standard Django patterns
path('users/<int:pk>/', views.UserDetailView.as_view())
path('users/<str:username>/', views.UserByUsernameView.as_view())
path('posts/<slug:slug>/', views.PostBySlugView.as_view())
path('files/<path:file_path>/', views.FileView.as_view())

# Custom regex patterns
re_path(r'^users/(?P<user_id>\d+)/$', views.UserView.as_view())
re_path(r'^api/v1/(?P<version>\w+)/users/$', views.UserView.as_view())

# DRF router patterns (auto-generated)
# GET /api/users/ (list)
# POST /api/users/ (create)
# GET /api/users/{id}/ (retrieve)
# PUT /api/users/{id}/ (update)
# DELETE /api/users/{id}/ (destroy)
```

## 🎯 Django REST Framework

### ViewSets

```python
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import User, Post
from .serializers import UserSerializer, PostSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    # Custom actions
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        user = self.get_object()
        user.is_active = True
        user.save()
        return Response({'status': 'activated'})
    
    @action(detail=False, methods=['get'])
    def active_users(self, request):
        users = User.objects.filter(is_active=True)
        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def posts(self, request, pk=None):
        user = self.get_object()
        posts = user.posts.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

# Detected endpoints:
# GET    /api/users/ (list)
# POST   /api/users/ (create)
# GET    /api/users/{id}/ (retrieve)
# PUT    /api/users/{id}/ (update)
# PATCH  /api/users/{id}/ (partial_update)
# DELETE /api/users/{id}/ (destroy)
# POST   /api/users/{id}/activate/ (custom action)
# GET    /api/users/active_users/ (custom action)
# GET    /api/users/{id}/posts/ (custom action)
```

### APIViews

```python
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Product
from .serializers import ProductSerializer

class ProductListAPIView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class ProductDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class ProductSearchAPIView(APIView):
    def get(self, request, query):
        products = Product.objects.filter(name__icontains=query)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

# Detected endpoints:
# GET    /api/products/ (list)
# POST   /api/products/ (create)
# GET    /api/products/{id}/ (retrieve)
# PUT    /api/products/{id}/ (update)
# DELETE /api/products/{id}/ (destroy)
# GET    /api/products/search/{query}/ (custom)
```

### Function-Based Views

```python
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET', 'POST'])
def user_list(request):
    if request.method == 'GET':
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Detected endpoints:
# GET    /api/users/ (function-based)
# POST   /api/users/ (function-based)
```

## 🔐 Authentication & Permissions

### DRF Authentication Classes

```python
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.authentication import JWTAuthentication

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    # Authentication
    authentication_classes = [JWTAuthentication, TokenAuthentication]
    
    # Permissions
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.action == 'create':
            return []  # Allow registration without auth
        return super().get_permissions()

# The explorer will detect:
# - Authentication required: True
# - Auth type: JWT
# - Permissions: IsAuthenticated
```

### Custom Authentication

```python
from rest_framework.authentication import BaseAuthentication
from rest_framework.permissions import BasePermission

class CustomAuthentication(BaseAuthentication):
    def authenticate(self, request):
        # Custom authentication logic
        pass

class CustomPermission(BasePermission):
    def has_permission(self, request, view):
        # Custom permission logic
        pass

class SecureViewSet(viewsets.ModelViewSet):
    authentication_classes = [CustomAuthentication]
    permission_classes = [CustomPermission]
```

## 🎨 Custom Views

### Class-Based Views

```python
from django.views.generic import ListView, DetailView
from django.views import View
from django.http import JsonResponse

class UserListView(ListView):
    model = User
    template_name = 'users/user_list.html'
    
    def get(self, request, *args, **kwargs):
        if request.headers.get('Accept') == 'application/json':
            users = self.get_queryset()
            data = [{'id': user.id, 'name': user.name} for user in users]
            return JsonResponse(data, safe=False)
        return super().get(request, *args, **kwargs)

class UserDetailView(DetailView):
    model = User
    template_name = 'users/user_detail.html'
    
    def get(self, request, *args, **kwargs):
        if request.headers.get('Accept') == 'application/json':
            user = self.get_object()
            data = {'id': user.id, 'name': user.name}
            return JsonResponse(data)
        return super().get(request, *args, **kwargs)

# Detected endpoints:
# GET /users/ (list)
# GET /users/{id}/ (detail)
```

### Function-Based Views

```python
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

@require_http_methods(["GET"])
def user_list(request):
    users = User.objects.all()
    data = [{'id': user.id, 'name': user.name} for user in users]
    return JsonResponse(data, safe=False)

@require_http_methods(["GET", "POST"])
@csrf_exempt
def user_create(request):
    if request.method == 'POST':
        # Handle POST logic
        pass
    return JsonResponse({'message': 'User created'})

# Detected endpoints:
# GET  /users/ (list)
# GET  /users/create/ (create view)
# POST /users/create/ (create action)
```

## ⚙️ Advanced Configuration

### Custom Settings Module

```python
# myproject/settings/dev.py
from .base import *

DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'dev.example.com']

# Custom API settings
API_VERSION = 'v1'
API_PREFIX = 'api/v1'

# Run with custom settings
django-api-explorer --settings myproject.settings.dev --browser
```

### Environment Variables

```bash
# Set Django settings
export DJANGO_SETTINGS_MODULE=myproject.settings.production

# Set custom host
export API_HOST=https://api.example.com

# Run with environment
django-api-explorer --browser
```

### Custom Port Configuration

```bash
# Avoid conflicts with Django development server
django-api-explorer --browser --port 8001

# Use with Django server on 8000
python manage.py runserver 8000  # Django server
django-api-explorer --browser --port 8001  # API Explorer
```

### File Watching Integration

```bash
# Watch for changes in Django files
django-api-explorer --browser --watch

# Monitored files:
# - *.py (Python files)
# - urls.py (URL configurations)
# - views.py (View files)
# - models.py (Model files)
# - serializers.py (DRF serializers)
# - settings.py (Settings files)
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Import Errors

```bash
# Error: No module named 'myapp'
# Solution: Make sure you're in the Django project root
cd /path/to/your/django/project
django-api-explorer --browser
```

#### 2. Settings Not Found

```bash
# Error: ROOT_URLCONF is not defined
# Solution: Specify the settings module
django-api-explorer --settings myproject.settings.dev --browser
```

#### 3. No Endpoints Found

```python
# Check your urls.py configuration
# Make sure URL patterns are properly defined

# urls.py
from django.urls import path, include

urlpatterns = [
    path('api/', include('myapp.urls')),  # Make sure this exists
]

# myapp/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('users/', views.UserListView.as_view(), name='user-list'),
]
```

#### 4. DRF Views Not Detected

```python
# Make sure DRF is properly installed
pip install djangorestframework

# Add to INSTALLED_APPS
INSTALLED_APPS = [
    'rest_framework',
    'myapp',
]

# Use proper DRF views
from rest_framework import viewsets
from rest_framework.views import APIView
```

#### 5. Authentication Issues

```python
# Make sure authentication classes are properly configured
class MyViewSet(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
```

### Debug Mode

```bash
# Enable verbose output
django-api-explorer --browser --verbose

# Check Django settings
python manage.py check

# Test URL resolution
python manage.py show_urls
```

### Common Import Issues (Fixed in v1.0.3+)

If you encounter `ModuleNotFoundError` or import-related issues:

```bash
# Ensure you're using the latest version
pip install --upgrade django-api-explorer

# Verify installation
django-api-explorer --version

# Check if package is properly installed
pip list | grep django-api-explorer
```

**Note**: v1.0.3+ includes comprehensive fixes for import issues that ensure the package works correctly whether installed from PyPI or in development mode.

### Performance Optimization

```python
# For large projects, scan specific apps
django-api-explorer --app myapp --browser

# Use custom host to avoid DNS resolution
django-api-explorer --host http://127.0.0.1:8000 --browser
```

## 📚 Best Practices

### 1. URL Organization

```python
# Use consistent URL patterns
urlpatterns = [
    path('api/v1/', include([
        path('users/', include('users.urls')),
        path('products/', include('products.urls')),
        path('orders/', include('orders.urls')),
    ])),
]
```

### 2. ViewSet Naming

```python
# Use descriptive ViewSet names
class UserManagementViewSet(viewsets.ModelViewSet):
    # Better than just UserViewSet for complex operations
    pass

class ProductCatalogViewSet(viewsets.ModelViewSet):
    # Clear purpose indication
    pass
```

### 3. Custom Actions

```python
# Use descriptive action names
@action(detail=True, methods=['post'])
def activate_account(self, request, pk=None):
    # Better than just 'activate'
    pass

@action(detail=False, methods=['get'])
def get_active_users(self, request):
    # Clear action purpose
    pass
```

### 4. Error Handling

```python
# Provide meaningful error responses
from rest_framework import status
from rest_framework.response import Response

class UserViewSet(viewsets.ModelViewSet):
    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except ValidationError as e:
            return Response(
                {'error': 'Validation failed', 'details': e.detail},
                status=status.HTTP_400_BAD_REQUEST
            )
```

## 🎉 Integration Complete!

Your Django project is now fully integrated with Django API Explorer! You can:

- **Discover APIs**: Automatically find all your endpoints
- **Test APIs**: Generate cURL commands with sample data
- **Export to Postman**: Create collections for your APIs
- **Monitor Changes**: Watch for file changes and auto-reload
- **Document APIs**: Generate comprehensive API documentation

For more information, see the [main README](README.md) and [quick start guide](QUICK_START.md).
