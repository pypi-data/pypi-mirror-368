"""
URL extraction module for Django API Explorer.

This module is responsible for parsing Django URL patterns and extracting
API endpoint information from Django projects.

extract_urls() → Main function that walks through Django's urlpatterns.
URLPattern → Direct path like /api/users/.
URLResolver → Nested include, so we go deeper.
get_view_name() → Finds full Python path to the view.
get_app_name() → Matches view to a Django app using INSTALLED_APPS.
normalize_path() → Ensures /path/ format.
"""

import importlib
import re
from typing import Any, Dict, List

from django.apps import apps
from django.urls import URLPattern, URLResolver, get_resolver

from .models import APIEndpoint, APIMethod, AuthType


class URLPatternExtractor:
    """Extracts API endpoints from Django URL patterns."""

    def __init__(self, project_root: str):
        self.project_root = project_root
        self.discovered_endpoints: List[APIEndpoint] = []

    def extract_all_endpoints(self) -> List[APIEndpoint]:
        """Extract all API endpoints from the Django project."""
        try:
            # Get the main URL resolver
            resolver = get_resolver()
            self._extract_from_resolver(resolver, "")
            return self.discovered_endpoints
        except Exception as e:
            print(f"Error extracting endpoints: {e}")
            return []

    def _extract_from_resolver(self, resolver, base_path: str):
        """Recursively extract endpoints from URL resolver."""
        for pattern in resolver.url_patterns:
            if isinstance(pattern, URLPattern):
                self._extract_from_pattern(pattern, base_path)
            elif isinstance(pattern, URLResolver):
                new_base = base_path + str(pattern.pattern)
                self._extract_from_resolver(pattern, new_base)

    def _extract_from_pattern(self, pattern: URLPattern, base_path: str):
        """Extract endpoint information from a single URL pattern."""
        try:
            full_path = base_path + str(pattern.pattern)

            full_path = self._clean_path(full_path)

            if self._should_skip_path(full_path):
                return

            view_info = self._extract_view_info(pattern.callback)

            if hasattr(pattern.callback, "cls"):
                view_class = pattern.callback.cls
                methods = self._get_viewset_methods_for_pattern(pattern, view_class)
                if methods:
                    view_info["methods"] = methods
            else:
                from .method_detector import get_allowed_methods

                detected_methods = get_allowed_methods(pattern.callback)
                if detected_methods:
                    api_methods = []
                    for method_name in detected_methods:
                        if hasattr(APIMethod, method_name):
                            api_methods.append(APIMethod(method_name))
                    if api_methods:
                        view_info["methods"] = api_methods

            methods = view_info.get("methods", [APIMethod.GET])
            if methods:
                seen = set()
                unique_methods = []
                for method in methods:
                    if method not in seen:
                        seen.add(method)
                        unique_methods.append(method)
                methods = unique_methods

            endpoint = APIEndpoint(
                path=full_path,
                name=view_info.get("name", ""),
                app_name=view_info.get("app_name", ""),
                methods=methods,
                auth_required=view_info.get("auth_required", False),
                auth_type=view_info.get("auth_type", AuthType.NONE),
                url_params=self._extract_url_params(full_path),
                view_class=view_info.get("view_class"),
                serializer_class=view_info.get("serializer_class"),
                permissions=view_info.get("permissions", []),
                description=view_info.get("description"),
            )

            if hasattr(pattern, "_app_name_override"):
                endpoint.app_name = pattern._app_name_override

            self.discovered_endpoints.append(endpoint)

        except Exception as e:
            print(f"Error extracting from pattern {pattern}: {e}")

    def _get_viewset_methods_for_pattern(self, pattern, view_class):
        """Get HTTP methods for a specific ViewSet pattern."""
        from .comprehensive_method_detector import (
            detect_methods_for_pattern,
            detect_methods_for_viewset_pattern,
        )

        pattern_str = str(pattern.pattern)

        methods = detect_methods_for_viewset_pattern(pattern_str, view_class)

        if not methods:
            methods = detect_methods_for_pattern(pattern_str, view_class)

        return methods

    def _infer_action_from_pattern(self, pattern_str: str, view_class) -> str:
        """Infer the action name from the URL pattern."""

        pattern_str = pattern_str.replace(r"\.(?P<format>[a-z0-9]+)/?$", "")

        if pattern_str.endswith("/$") and not pattern_str.endswith("/(?P<pk>[^/.]+)/$"):

            if hasattr(view_class, "list") and hasattr(view_class, "create"):
                return "list"
            elif hasattr(view_class, "list"):
                return "list"
            elif hasattr(view_class, "create"):
                return "create"

        elif pattern_str.endswith("/(?P<pk>[^/.]+)/$"):
            if (
                hasattr(view_class, "retrieve")
                and hasattr(view_class, "update")
                and hasattr(view_class, "destroy")
            ):
                return "retrieve"
            elif hasattr(view_class, "retrieve"):
                return "retrieve"
            elif hasattr(view_class, "update"):
                return "update"
            elif hasattr(view_class, "destroy"):
                return "destroy"

        if hasattr(view_class, "get_extra_actions"):
            extra_actions = view_class.get_extra_actions()
            for action_func in extra_actions:
                action_name = action_func.__name__
                if (
                    f"/{action_name}/" in pattern_str
                    or f"/{action_name.replace('_', '-')}/" in pattern_str
                ):
                    return action_name

        return None

    def _clean_path(self, path: str) -> str:
        """Clean and normalize URL path."""
        path = re.sub(r"<[^>]+>", "{param}", path)
        path = re.sub(r"\(\?P<[^>]+>[^)]+\)", "{param}", path)
        path = re.sub(r"[^/a-zA-Z0-9\-_\.{}]", "", path)

        if not path.startswith("/"):
            path = "/" + path

        return path

    def _should_skip_path(self, path: str) -> bool:
        """Check if path should be skipped."""
        skip_patterns = [
            "/admin/",
            "/static/",
            "/media/",
            "/__debug__/",
            "/silk/",
            "/django-debug-toolbar/",
        ]

        return any(pattern in path for pattern in skip_patterns)

    def _extract_url_params(self, path: str) -> List[Dict[str, str]]:
        """Extract URL parameters from path with enhanced information."""
        params = []

        matches = re.findall(r"\{([^}]+)\}", path)
        for match in matches:
            param_info = self._analyze_parameter(match, path)
            params.append(param_info)

        matches = re.findall(r"<([^>]+)>", path)
        for match in matches:
            param_info = self._analyze_parameter(match, path)
            params.append(param_info)

        matches = re.findall(r"\(\?P<([^>]+)>", path)
        for match in matches:
            param_info = self._analyze_parameter(match, path)
            params.append(param_info)

        regex_matches = re.findall(r"\(\?P<([^>]+)>[^)]*\)", path)
        for match in regex_matches:
            param_info = self._analyze_parameter(match, path)
            params.append(param_info)

        seen_names = set()
        unique_params = []
        for param in params:
            if param["name"] not in seen_names:
                seen_names.add(param["name"])
                unique_params.append(param)

        return unique_params

    def _analyze_parameter(self, param_name: str, path: str) -> Dict[str, str]:
        """Analyze a parameter and extract detailed information."""
        clean_name = param_name.strip()

        param_type = self._infer_parameter_type(clean_name, path)
        param_format = self._infer_parameter_format(clean_name, path)

        descriptive_name = self._generate_descriptive_name(clean_name, path)

        return {
            "name": clean_name,
            "descriptive_name": descriptive_name,
            "type": param_type,
            "format": param_format,
            "required": True,
            "description": self._generate_parameter_description(clean_name, path),
        }

    def _infer_parameter_type(self, param_name: str, path: str) -> str:
        """Infer the parameter type based on name and context."""
        param_lower = param_name.lower()

        if any(id_pattern in param_lower for id_pattern in ["id", "pk", "uuid"]):
            return "integer" if "uuid" not in param_lower else "string"

        if any(
            str_pattern in param_lower
            for str_pattern in ["name", "title", "slug", "email", "username"]
        ):
            return "string"

        if any(
            date_pattern in param_lower
            for date_pattern in ["date", "time", "created", "updated"]
        ):
            return "string"

        if any(
            num_pattern in param_lower
            for num_pattern in ["count", "limit", "offset", "page", "size"]
        ):
            return "integer"

        return "string"

    def _infer_parameter_format(self, param_name: str, path: str) -> str:
        """Infer the parameter format based on name and context."""
        param_lower = param_name.lower()

        if "uuid" in param_lower:
            return "uuid"

        if "email" in param_lower:
            return "email"

        if any(
            date_pattern in param_lower
            for date_pattern in ["date", "created", "updated"]
        ):
            return "date"

        if "time" in param_lower:
            return "date-time"

        if "slug" in param_lower:
            return "slug"

        return "string"

    def _generate_descriptive_name(self, param_name: str, path: str) -> str:
        """Generate a more descriptive parameter name."""
        param_lower = param_name.lower()

        name_mappings = {
            "id": "user_id",
            "pk": "primary_key",
            "uuid": "user_uuid",
            "slug": "article_slug",
            "name": "user_name",
            "title": "article_title",
            "email": "user_email",
            "username": "username",
            "date": "created_date",
            "time": "created_time",
            "count": "item_count",
            "limit": "page_limit",
            "offset": "page_offset",
            "page": "page_number",
            "size": "page_size",
        }

        if param_lower in name_mappings:
            return name_mappings[param_lower]

        for key, value in name_mappings.items():
            if key in param_lower:
                return value

        path_lower = path.lower()

        path_parts = path_lower.split("/")
        resource_name = None

        for part in path_parts:
            if part and part not in [
                "api",
                "v1",
                "v2",
                "v3",
                "admin",
                "auth",
                "static",
                "media",
            ]:
                resource_name = part
                break

        if resource_name:
            if param_lower in ["id", "pk", "uuid"]:
                return f"{resource_name}_id"
            else:
                return f"{resource_name}_{param_lower}"

        # Handle common patterns
        if "user" in path_lower and param_lower not in ["id", "pk", "uuid"]:
            return f"user_{param_lower}"
        elif "article" in path_lower or "post" in path_lower:
            return f"article_{param_lower}"
        elif "product" in path_lower:
            return f"product_{param_lower}"
        elif "order" in path_lower:
            return f"order_{param_lower}"

        return param_lower.replace("-", "_")

    def _generate_parameter_description(self, param_name: str, path: str) -> str:
        """Generate a description for the parameter."""
        param_lower = param_name.lower()
        path_lower = path.lower()

        # Common descriptions
        descriptions = {
            "id": "Unique identifier",
            "pk": "Primary key",
            "uuid": "Unique identifier (UUID format)",
            "slug": "URL-friendly identifier",
            "name": "Display name",
            "title": "Title or heading",
            "email": "Email address",
            "username": "Username",
            "date": "Date in YYYY-MM-DD format",
            "time": "Timestamp",
            "count": "Number of items",
            "limit": "Maximum number of items to return",
            "offset": "Number of items to skip",
            "page": "Page number for pagination",
            "size": "Number of items per page",
        }

        if param_lower == "param":
            path_parts = path_lower.split("/")
            resource_name = None

            for part in path_parts:
                if part and part not in [
                    "api",
                    "v1",
                    "v2",
                    "v3",
                    "admin",
                    "auth",
                    "static",
                    "media",
                ]:
                    resource_name = part
                    break

            if resource_name:
                return f"Unique identifier for the {resource_name}"
            else:
                return "Unique identifier parameter"

        if param_lower in descriptions:
            return descriptions[param_lower]

        for key, desc in descriptions.items():
            if key in param_lower:
                return desc

        if "id" in param_lower:
            return f"Unique identifier for {param_lower.replace('_id', '')}"
        elif "name" in param_lower:
            return f"Name of the {param_lower.replace('_name', '')}"

        return f"Parameter: {param_name}"

    def _extract_view_info(self, callback) -> Dict[str, Any]:
        """Extract information from view callback."""
        info = {
            "name": "",
            "app_name": "",
            "methods": [APIMethod.GET],
            "auth_required": False,
            "auth_type": AuthType.NONE,
            "view_class": None,
            "serializer_class": None,
            "permissions": [],
            "description": None,
        }

        try:
            if hasattr(callback, "__name__"):
                info["name"] = callback.__name__

            if hasattr(callback, "__module__"):
                module_parts = callback.__module__.split(".")
                app_name = self._extract_app_name_from_module(callback, module_parts)
                if app_name:
                    info["app_name"] = app_name

            from .method_detector import get_allowed_methods

            detected_methods = get_allowed_methods(callback)
            methods = []
            for method_name in detected_methods:
                if hasattr(APIMethod, method_name):
                    methods.append(APIMethod(method_name))
            if methods:
                info["methods"] = methods
            else:
                for method_name in ["get", "post", "put", "patch", "delete"]:
                    if hasattr(callback, method_name):
                        if hasattr(APIMethod, method_name.upper()):
                            methods.append(getattr(APIMethod, method_name.upper()))
                if methods:
                    info["methods"] = methods

            if hasattr(callback, "authentication_classes"):
                auth_classes = callback.authentication_classes
                if auth_classes:
                    info["auth_required"] = True
                    info["auth_type"] = self._detect_auth_type(auth_classes)

            if hasattr(callback, "permission_classes"):
                info["permissions"] = [
                    perm.__name__ for perm in callback.permission_classes
                ]

            if hasattr(callback, "__class__"):
                info["view_class"] = callback.__class__.__name__

            if hasattr(callback, "serializer_class"):
                info["serializer_class"] = callback.serializer_class.__name__

            if hasattr(callback, "__doc__") and callback.__doc__:
                info["description"] = callback.__doc__.strip()

        except Exception as e:
            print(f"Error extracting view info: {e}")

        return info

    def _extract_app_name_from_module(self, callback, module_parts) -> str:
        """Extract the actual Django app name from the module path."""
        try:
            if hasattr(callback, "cls"):
                view_class = callback.cls
                if hasattr(view_class, "__module__"):
                    view_module = view_class.__module__
                    view_parts = view_module.split(".")
                    if len(view_parts) >= 2:
                        potential_app = view_parts[1]
                        if self._is_valid_django_app(potential_app):
                            return potential_app

            for part in module_parts:
                if self._is_valid_django_app(part):
                    return part

            if len(module_parts) >= 2:
                return module_parts[1]

        except Exception as e:
            print(f"Error extracting app name: {e}")

        return ""

    def _is_valid_django_app(self, app_name: str) -> bool:
        """Check if a string is a valid Django app name."""
        try:
            app_config = apps.get_app_config(app_name)
            return app_config is not None
        except Exception:
            return False

    def _detect_auth_type(self, auth_classes) -> AuthType:
        """Detect authentication type from authentication classes."""
        auth_class_names = [auth.__name__.lower() for auth in auth_classes]

        if any("jwt" in name for name in auth_class_names):
            return AuthType.TOKEN  # JWT is a type of token
        elif any("token" in name for name in auth_class_names):
            return AuthType.TOKEN
        elif any("session" in name for name in auth_class_names):
            return AuthType.SESSION
        elif any("basic" in name for name in auth_class_names):
            return AuthType.BASIC
        elif any("oauth" in name for name in auth_class_names):
            return AuthType.OAUTH
        else:
            return AuthType.API_KEY  # Use API_KEY instead of CUSTOM

    def extract_from_app(self, app_name: str) -> List[APIEndpoint]:
        """Extract endpoints from a specific Django app."""
        try:
            app_config = apps.get_app_config(app_name)
            if not app_config:
                return []

            urls_module = f"{app_name}.urls"
            try:
                urls = importlib.import_module(urls_module)

                if hasattr(urls, "urlpatterns"):
                    self.discovered_endpoints = []
                    for pattern in urls.urlpatterns:
                        if isinstance(pattern, URLPattern):
                            if hasattr(pattern, "callback"):
                                pattern._app_name_override = app_name
                            self._extract_from_pattern(pattern, f"/{app_name}/")
                        elif isinstance(pattern, URLResolver):
                            self._extract_from_resolver(pattern, f"/{app_name}/")
                    return self.discovered_endpoints
                else:
                    return []

            except ImportError:
                return []

        except Exception as e:
            print(f"Error extracting from app {app_name}: {e}")
            return []
