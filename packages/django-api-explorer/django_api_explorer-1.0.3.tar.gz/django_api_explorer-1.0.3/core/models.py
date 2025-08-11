"""
Data models for API Explorer.

This module defines the data structures used throughout the API Explorer
to represent API endpoints and their metadata.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class APIMethod(Enum):
    """HTTP methods supported by API endpoints."""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class AuthType(Enum):
    """Authentication types for API endpoints."""

    NONE = "none"
    SESSION = "session"
    TOKEN = "token"
    BASIC = "basic"
    OAUTH = "oauth"
    API_KEY = "api_key"


@dataclass
class APIEndpoint:
    """Represents an API endpoint with all its metadata."""

    path: str
    name: str = ""
    app_name: str = ""
    methods: List[APIMethod] = field(default_factory=lambda: [APIMethod.GET])
    auth_required: bool = False
    auth_type: AuthType = AuthType.NONE
    url_params: List[dict] = field(default_factory=list)  # Enhanced parameter structure
    view_class: Optional[str] = None
    serializer_class: Optional[str] = None
    permissions: List[str] = field(default_factory=list)
    description: Optional[str] = None
    full_url: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert endpoint to dictionary for serialization."""
        return {
            "path": self.path,
            "name": self.name,
            "app_name": self.app_name,
            "methods": [method.value for method in self.methods],
            "auth_required": self.auth_required,
            "auth_type": self.auth_type.value,
            "url_params": self.url_params,  # Now contains detailed parameter info
            "url_param_names": [
                param.get("descriptive_name", param.get("name", ""))
                for param in self.url_params
            ],  # For backward compatibility
            "view_class": self.view_class,
            "serializer_class": self.serializer_class,
            "permissions": self.permissions,
            "description": self.description,
            "full_url": self.full_url,
        }

    def __str__(self) -> str:
        """String representation of the endpoint."""
        methods_str = ", ".join([method.value for method in self.methods])
        return f"{self.path} [{methods_str}] - {self.name}"
