"""
Core functionality for Django API Explorer.

This package contains the main logic for discovering, analyzing, and formatting Django API endpoints.
"""

# Lazy imports to avoid DRF import issues during module loading
__all__ = [
    "format_as_text",
    "APIFormatter",
    "load_django_settings",
    "get_allowed_hosts",
    "get_installed_apps",
    "URLPatternExtractor",
    "get_allowed_methods",
    "detect_methods_from_url_pattern",
    "detect_methods_for_viewset_pattern",
    "detect_methods_for_pattern",
    "get_viewset_method_summary",
    "debug_method_detection",
    "DataFactory",
    "APIEndpoint",
    "APIMethod",
    "AuthType"
]

def __getattr__(name):
    """Lazy import function to avoid import issues."""
    if name == "format_as_text":
        from .formatter import format_as_text
        return format_as_text
    elif name == "APIFormatter":
        from .formatter import APIFormatter
        return APIFormatter
    elif name == "load_django_settings":
        from .settings_loader import load_django_settings
        return load_django_settings
    elif name == "get_allowed_hosts":
        from .settings_loader import get_allowed_hosts
        return get_allowed_hosts
    elif name == "get_installed_apps":
        from .settings_loader import get_installed_apps
        return get_installed_apps
    elif name == "URLPatternExtractor":
        from .url_extractor import URLPatternExtractor
        return URLPatternExtractor
    elif name == "get_allowed_methods":
        from .method_detector import get_allowed_methods
        return get_allowed_methods
    elif name == "detect_methods_from_url_pattern":
        from .method_detector import detect_methods_from_url_pattern
        return detect_methods_from_url_pattern
    elif name == "detect_methods_for_viewset_pattern":
        from .comprehensive_method_detector import detect_methods_for_viewset_pattern
        return detect_methods_for_viewset_pattern
    elif name == "detect_methods_for_pattern":
        from .comprehensive_method_detector import detect_methods_for_pattern
        return detect_methods_for_pattern
    elif name == "get_viewset_method_summary":
        from .comprehensive_method_detector import get_viewset_method_summary
        return get_viewset_method_summary
    elif name == "debug_method_detection":
        from .comprehensive_method_detector import debug_method_detection
        return debug_method_detection
    elif name == "DataFactory":
        from .data_factory import DataFactory
        return DataFactory
    elif name == "APIEndpoint":
        from .models import APIEndpoint
        return APIEndpoint
    elif name == "APIMethod":
        from .models import APIMethod
        return APIMethod
    elif name == "AuthType":
        from .models import AuthType
        return AuthType
    else:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
