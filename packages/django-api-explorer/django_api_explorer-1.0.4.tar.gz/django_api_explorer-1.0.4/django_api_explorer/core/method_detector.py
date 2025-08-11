from django.views import View

# Global flag to track DRF availability
DRF_AVAILABLE = None

def _check_drf_availability():
    """Check if Django REST Framework is available."""
    global DRF_AVAILABLE
    if DRF_AVAILABLE is None:
        try:
            import rest_framework
            DRF_AVAILABLE = True
        except ImportError:
            DRF_AVAILABLE = False
    return DRF_AVAILABLE

def _get_drf_classes():
    """Get DRF classes if available."""
    if not _check_drf_availability():
        # Return dummy classes if DRF is not available
        class GenericAPIView:
            pass
        class APIView:
            pass
        class ViewSet:
            pass
        return GenericAPIView, APIView, ViewSet
    
    # Import DRF classes only when needed
    from rest_framework.generics import GenericAPIView
    from rest_framework.views import APIView
    from rest_framework.viewsets import ViewSet
    return GenericAPIView, APIView, ViewSet


def get_allowed_methods(callback):
    """
    Detect allowed HTTP methods for a given view callback.
    Returns a list like ["GET", "POST"].
    """
    methods = set()

    # Handle DRF ViewSet actions
    if hasattr(callback, "cls") and hasattr(callback.cls, "get_extra_actions"):
        view_class = callback.cls
        methods.update(_get_viewset_methods(view_class))
        return sorted(methods)

    # Handle class-based views
    if hasattr(callback, "view_class"):
        view_class = callback.view_class
        methods.update(_get_class_based_view_methods(view_class))
        return sorted(methods)

    # Handle function-based views
    view_func = getattr(callback, "__func__", callback)

    # Check if it's a DRF view function
    if hasattr(view_func, "view_class"):
        view_class = view_func.view_class
        methods.update(_get_class_based_view_methods(view_class))

    # Check for @require_http_methods decorator
    if hasattr(view_func, "methods"):
        methods.update(view_func.methods)

    # Check for DRF action decorators
    if hasattr(view_func, "action"):
        if view_func.action in ["list", "retrieve"]:
            methods.add("GET")
        elif view_func.action in ["create"]:
            methods.add("POST")
        elif view_func.action in ["update", "partial_update"]:
            methods.add("PUT")
            methods.add("PATCH")
        elif view_func.action in ["destroy"]:
            methods.add("DELETE")

    # Check for DRF action decorator with methods
    if hasattr(view_func, "methods"):
        methods.update(view_func.methods)

    # Check for DRF action decorator with detail parameter
    if hasattr(view_func, "detail"):
        detail = view_func.detail
        if detail is False:  # List action
            methods.add("GET")
        elif detail is True:  # Detail action
            methods.add("GET")

    # Fallback: assume GET if nothing else is specified
    if not methods:
        methods.add("GET")

    return sorted(methods)


def _get_viewset_methods(view_class):
    """Extract methods from DRF ViewSet."""
    methods = set()
    
    # Only proceed if DRF is available
    if not _check_drf_availability():
        return methods

    # Standard ViewSet methods
    if hasattr(view_class, "list"):
        methods.add("GET")
    if hasattr(view_class, "create"):
        methods.add("POST")
    if hasattr(view_class, "retrieve"):
        methods.add("GET")
    if hasattr(view_class, "update"):
        methods.add("PUT")
    if hasattr(view_class, "partial_update"):
        methods.add("PATCH")
    if hasattr(view_class, "destroy"):
        methods.add("DELETE")

    # Check for custom actions
    if hasattr(view_class, "get_extra_actions"):
        extra_actions = view_class.get_extra_actions()
        for action_func in extra_actions:
            # Try to determine method from action name or decorators
            if hasattr(action_func, "methods"):
                methods.update(action_func.methods)
            elif hasattr(action_func, "action"):
                # Check if it's a DRF action with specific methods
                if hasattr(action_func, "methods"):
                    methods.update(action_func.methods)
                else:
                    # Default to GET for custom actions
                    methods.add("GET")
            else:
                # Default to GET for custom actions
                methods.add("GET")

    return methods


def _get_class_based_view_methods(view_class):
    """Extract methods from class-based views."""
    methods = set()

    # Check if it's a DRF ViewSet (only if DRF is available)
    if _check_drf_availability():
        GenericAPIView, APIView, ViewSet = _get_drf_classes()
        if isinstance(view_class, ViewSet) or issubclass(view_class, ViewSet):
            methods.update(_get_viewset_methods(view_class))
            return methods

    # Check if it's a DRF APIView or GenericAPIView (only if DRF is available)
    if _check_drf_availability():
        GenericAPIView, APIView, ViewSet = _get_drf_classes()
        if isinstance(view_class, (APIView, GenericAPIView)) or issubclass(
            view_class, (APIView, GenericAPIView)
        ):
            # Check for standard HTTP methods
            for method_name in ["get", "post", "put", "patch", "delete", "head", "options"]:
                if hasattr(view_class, method_name):
                    methods.add(method_name.upper())

            # Check for DRF action methods
            if hasattr(view_class, "list"):
                methods.add("GET")
            if hasattr(view_class, "create"):
                methods.add("POST")
            if hasattr(view_class, "retrieve"):
                methods.add("GET")
            if hasattr(view_class, "update"):
                methods.add("PUT")
            if hasattr(view_class, "partial_update"):
                methods.add("PATCH")
            if hasattr(view_class, "destroy"):
                methods.add("DELETE")

    # Check for standard Django class-based views
    elif isinstance(view_class, View) or issubclass(view_class, View):
        for method_name in ["get", "post", "put", "patch", "delete", "head", "options"]:
            if hasattr(view_class, method_name):
                methods.add(method_name.upper())

    # Generic check for any class-based view
    else:
        for method_name in ["get", "post", "put", "patch", "delete", "head", "options"]:
            if hasattr(view_class, method_name):
                methods.add(method_name.upper())

    return methods


def detect_methods_from_url_pattern(pattern):
    """
    Detect HTTP methods from URL pattern configuration.
    This is useful for patterns that have explicit method restrictions.
    """
    methods = set()

    # Check if pattern has method restrictions
    if hasattr(pattern, "callback"):
        callback = pattern.callback
        methods.update(get_allowed_methods(callback))

    # Check for DRF router patterns
    if hasattr(pattern, "url_patterns"):
        for sub_pattern in pattern.url_patterns:
            methods.update(detect_methods_from_url_pattern(sub_pattern))

    return methods
