"""
Comprehensive HTTP method detector for Django REST Framework ViewSets.
"""

from typing import Any, Dict, List

from .models import APIMethod


def detect_methods_for_viewset_pattern(pattern_str: str, view_class) -> List[APIMethod]:
    """
    Detect HTTP methods for a ViewSet URL pattern.
    This is a generic implementation that works with any Django project.
    """
    methods = []

    # Clean the pattern string
    pattern_str = pattern_str.replace(r"\.(?P<format>[a-z0-9]+)/?$", "")

    # Standard ViewSet patterns
    if pattern_str.endswith("/$") and not pattern_str.endswith("/(?P<pk>[^/.]+)/$"):
        # List/Create endpoint
        if hasattr(view_class, "list"):
            methods.append(APIMethod.GET)
        if hasattr(view_class, "create"):
            methods.append(APIMethod.POST)

    elif pattern_str.endswith("/(?P<pk>[^/.]+)/$"):
        # Retrieve/Update/Destroy endpoint
        if hasattr(view_class, "retrieve"):
            methods.append(APIMethod.GET)
        if hasattr(view_class, "update"):
            methods.append(APIMethod.PUT)
        if hasattr(view_class, "partial_update"):
            methods.append(APIMethod.PATCH)
        if hasattr(view_class, "destroy"):
            methods.append(APIMethod.DELETE)

    # Generic custom action detection
    # Look for custom actions in the ViewSet
    if hasattr(view_class, "get_extra_actions"):
        extra_actions = view_class.get_extra_actions()
        for action_func in extra_actions:
            # Check if this pattern matches the action
            action_name = action_func.__name__
            if (
                f"/{action_name}/" in pattern_str
                or f"/{action_name.replace('_', '-')}/" in pattern_str
            ):
                # Check if the action has specific method restrictions
                if hasattr(action_func, "methods"):
                    for method in action_func.methods:
                        if hasattr(APIMethod, method.upper()):
                            methods.append(getattr(APIMethod, method.upper()))
                else:
                    # Default to GET for custom actions
                    methods.append(APIMethod.GET)

    # Default to GET if no methods detected
    if not methods:
        methods.append(APIMethod.GET)

    # Remove duplicates while preserving order
    seen = set()
    unique_methods = []
    for method in methods:
        if method not in seen:
            seen.add(method)
            unique_methods.append(method)

    return unique_methods


def detect_methods_for_pattern(pattern_str: str, view_class) -> List[APIMethod]:
    """
    Generic method detection for any URL pattern.
    This is a fallback when the specific ViewSet detection fails.
    """
    methods = []

    # Check for standard HTTP methods in the view class
    for method_name in ["get", "post", "put", "patch", "delete", "head", "options"]:
        if hasattr(view_class, method_name):
            if hasattr(APIMethod, method_name.upper()):
                methods.append(getattr(APIMethod, method_name.upper()))

    # Check for DRF-specific methods (only if not already detected above)
    if hasattr(view_class, "list") and APIMethod.GET not in methods:
        methods.append(APIMethod.GET)
    if hasattr(view_class, "create") and APIMethod.POST not in methods:
        methods.append(APIMethod.POST)
    if hasattr(view_class, "retrieve") and APIMethod.GET not in methods:
        methods.append(APIMethod.GET)
    if hasattr(view_class, "update") and APIMethod.PUT not in methods:
        methods.append(APIMethod.PUT)
    if hasattr(view_class, "partial_update") and APIMethod.PATCH not in methods:
        methods.append(APIMethod.PATCH)
    if hasattr(view_class, "destroy") and APIMethod.DELETE not in methods:
        methods.append(APIMethod.DELETE)

    # Default to GET if no methods detected
    if not methods:
        methods.append(APIMethod.GET)

    # Remove duplicates while preserving order
    seen = set()
    unique_methods = []
    for method in methods:
        if method not in seen:
            seen.add(method)
            unique_methods.append(method)

    return unique_methods


def get_viewset_method_summary(view_class) -> Dict[str, List[APIMethod]]:
    """
    Get a summary of all methods available in a ViewSet.
    """
    summary = {}

    # Standard ViewSet methods
    if hasattr(view_class, "list"):
        summary["list"] = [APIMethod.GET]
    if hasattr(view_class, "create"):
        summary["create"] = [APIMethod.POST]
    if hasattr(view_class, "retrieve"):
        summary["retrieve"] = [APIMethod.GET]
    if hasattr(view_class, "update"):
        summary["update"] = [APIMethod.PUT]
    if hasattr(view_class, "partial_update"):
        summary["partial_update"] = [APIMethod.PATCH]
    if hasattr(view_class, "destroy"):
        summary["destroy"] = [APIMethod.DELETE]

    # Custom actions
    if hasattr(view_class, "get_extra_actions"):
        extra_actions = view_class.get_extra_actions()
        for action_func in extra_actions:
            action_name = action_func.__name__
            if hasattr(action_func, "methods"):
                methods = []
                for method in action_func.methods:
                    if hasattr(APIMethod, method.upper()):
                        methods.append(getattr(APIMethod, method.upper()))
                summary[action_name] = methods
            else:
                summary[action_name] = [APIMethod.GET]

    return summary


def debug_method_detection(pattern_str: str, view_class) -> Dict[str, Any]:
    """
    Debug method detection to understand why duplicate methods might occur.
    """
    debug_info = {
        "pattern": pattern_str,
        "view_class": (
            view_class.__name__ if hasattr(view_class, "__name__") else str(view_class)
        ),
        "has_get": hasattr(view_class, "get"),
        "has_list": hasattr(view_class, "list"),
        "has_retrieve": hasattr(view_class, "retrieve"),
        "has_create": hasattr(view_class, "create"),
        "has_update": hasattr(view_class, "update"),
        "has_partial_update": hasattr(view_class, "partial_update"),
        "has_destroy": hasattr(view_class, "destroy"),
        "detected_methods": [],
    }

    # Run both detection methods
    viewset_methods = detect_methods_for_viewset_pattern(pattern_str, view_class)
    generic_methods = detect_methods_for_pattern(pattern_str, view_class)

    debug_info["viewset_methods"] = [str(m) for m in viewset_methods]
    debug_info["generic_methods"] = [str(m) for m in generic_methods]

    return debug_info
