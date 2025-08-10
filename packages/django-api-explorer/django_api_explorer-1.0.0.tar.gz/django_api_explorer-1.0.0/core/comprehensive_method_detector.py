"""
Comprehensive HTTP method detector for Django REST Framework ViewSets.
"""

from typing import List, Dict, Any
from .models import APIMethod


def detect_methods_for_viewset_pattern(pattern_str: str, view_class) -> List[APIMethod]:
    """
    Detect HTTP methods for a ViewSet URL pattern.
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

    # Custom action patterns
    elif "/apply-player-favourites/" in pattern_str:
        methods.append(APIMethod.GET)
    elif "/store-campaign-players/" in pattern_str:
        methods.append(APIMethod.GET)
    elif "/archive/" in pattern_str:
        methods.append(APIMethod.GET)
    elif "/assessments/" in pattern_str:
        methods.append(APIMethod.GET)
    elif "/book/" in pattern_str:
        methods.append(APIMethod.GET)
    elif "/cancel-reservation/" in pattern_str:
        methods.append(APIMethod.GET)
    elif "/clone-campaign/" in pattern_str:
        methods.append(APIMethod.GET)
    elif "/flights/" in pattern_str:
        methods.append(APIMethod.GET)
    elif "/history/" in pattern_str:
        methods.append(APIMethod.GET)
    elif "/mark_invoiced/" in pattern_str:
        methods.append(APIMethod.GET)
    elif "/mark_not_invoiced/" in pattern_str:
        methods.append(APIMethod.GET)
    elif "/remove-price-modifier/" in pattern_str:
        methods.append(APIMethod.GET)
    elif "/stop/" in pattern_str:
        methods.append(APIMethod.GET)
    elif "/unarchive/" in pattern_str:
        methods.append(APIMethod.GET)
    elif "/upsert-price-modifier/" in pattern_str:
        methods.append(APIMethod.GET)

    # Flight-specific patterns
    elif "/add-spot-group/" in pattern_str:
        methods.append(APIMethod.GET)
    elif "/allocation-profile/" in pattern_str:
        methods.append(APIMethod.GET)
    elif "/allocation-profile-site/" in pattern_str:
        methods.append(APIMethod.GET)
    elif "/assign-all-players/" in pattern_str:
        methods.append(APIMethod.GET)
    elif "/assign-players/" in pattern_str:
        methods.append(APIMethod.GET)
    elif "/available-players/" in pattern_str:
        methods.append(APIMethod.GET)
    elif "/clone/" in pattern_str:
        methods.append(APIMethod.GET)
    elif "/remove-spot-group/" in pattern_str:
        methods.append(APIMethod.GET)
    elif "/site-count/" in pattern_str:
        methods.append(APIMethod.GET)
    elif "/update-spot-group/" in pattern_str:
        methods.append(APIMethod.GET)
    elif "/update-spot-groups-rules/" in pattern_str:
        methods.append(APIMethod.GET)

    # Default to GET if no methods detected
    if not methods:
        methods.append(APIMethod.GET)

    return methods


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
