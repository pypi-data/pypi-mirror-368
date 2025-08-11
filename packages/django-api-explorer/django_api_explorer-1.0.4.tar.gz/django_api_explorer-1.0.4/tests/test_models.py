"""
Test cases for the models module.
Tests all data models and their functionality.
"""

import unittest

from django_api_explorer.core.models import APIEndpoint, APIMethod, AuthType


class TestAPIMethod(unittest.TestCase):
    """Test cases for APIMethod enum."""

    def test_apimethod_values(self):
        """Test that all expected HTTP methods are present."""
        expected_methods = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'HEAD', 'OPTIONS']
        
        for method in expected_methods:
            self.assertTrue(hasattr(APIMethod, method))
            self.assertEqual(getattr(APIMethod, method).value, method)

    def test_apimethod_string_representation(self):
        """Test string representation of APIMethod."""
        get_method = APIMethod.GET
        self.assertEqual(str(get_method), "APIMethod.GET")
        self.assertEqual(get_method.value, "GET")

    def test_apimethod_comparison(self):
        """Test APIMethod comparison operations."""
        get_method = APIMethod.GET
        post_method = APIMethod.POST
        
        self.assertNotEqual(get_method, post_method)
        self.assertEqual(get_method, APIMethod.GET)
        self.assertEqual(get_method.value, "GET")


class TestAuthType(unittest.TestCase):
    """Test cases for AuthType enum."""
    #
    # def test_authtype_values(self):
    #     """Test that all expected auth types are present."""
    #     expected_types = ['NONE', 'SESSION', 'TOKEN', 'BASIC', 'OAUTH', 'API_KEY']
    #
    #     for auth_type in expected_types:
    #         self.assertTrue(hasattr(AuthType, auth_type))
    #         # Note: values are lowercase in the actual implementation
    #         expected_value = auth_type.lower().replace('_', '')
    #         self.assertEqual(getattr(AuthType, auth_type).value, expected_value)

    def test_authtype_comparison(self):
        """Test AuthType comparison operations."""
        none_auth = AuthType.NONE
        token_auth = AuthType.TOKEN
        
        self.assertNotEqual(none_auth, token_auth)
        self.assertEqual(none_auth, AuthType.NONE)
        self.assertEqual(none_auth.value, "none")

    def test_authtype_string_representation(self):
        """Test string representation of AuthType."""
        token_auth = AuthType.TOKEN
        self.assertEqual(str(token_auth), "AuthType.TOKEN")
        self.assertEqual(token_auth.value, "token")


class TestAPIEndpoint(unittest.TestCase):
    """Test cases for APIEndpoint class."""

    def setUp(self):
        """Set up test data."""
        self.sample_endpoint = APIEndpoint(
            path="/api/users/",
            name="UserListView",
            app_name="users",
            methods=[APIMethod.GET, APIMethod.POST],
            auth_required=True,
            auth_type=AuthType.TOKEN,
            url_params=[],
            view_class="UserViewSet",
            serializer_class="UserSerializer",
            permissions=["IsAuthenticated"],
            description="List and create users"
        )

    def test_apiendpoint_creation(self):
        """Test APIEndpoint creation with all parameters."""
        endpoint = APIEndpoint(
            path="/api/users/{id}/",
            name="UserDetailView",
            app_name="users",
            methods=[APIMethod.GET, APIMethod.PUT, APIMethod.DELETE],
            auth_required=True,
            auth_type=AuthType.TOKEN,
            url_params=[{"name": "id", "type": "integer"}],
            view_class="UserViewSet",
            serializer_class="UserSerializer",
            permissions=["IsAuthenticated"],
            description="Retrieve, update, or delete a user"
        )
        
        self.assertEqual(endpoint.path, "/api/users/{id}/")
        self.assertEqual(endpoint.name, "UserDetailView")
        self.assertEqual(endpoint.app_name, "users")
        self.assertEqual(len(endpoint.methods), 3)
        self.assertIn(APIMethod.GET, endpoint.methods)
        self.assertIn(APIMethod.PUT, endpoint.methods)
        self.assertIn(APIMethod.DELETE, endpoint.methods)
        self.assertTrue(endpoint.auth_required)
        self.assertEqual(endpoint.auth_type, AuthType.TOKEN)
        self.assertEqual(len(endpoint.url_params), 1)
        self.assertEqual(endpoint.url_params[0]["name"], "id")
        self.assertEqual(endpoint.url_params[0]["type"], "integer")

    def test_apiendpoint_default_values(self):
        """Test APIEndpoint creation with default values."""
        endpoint = APIEndpoint(path="/api/test/")
        
        self.assertEqual(endpoint.path, "/api/test/")
        self.assertEqual(endpoint.name, "")
        self.assertEqual(endpoint.app_name, "")
        self.assertEqual(endpoint.methods, [APIMethod.GET])
        self.assertFalse(endpoint.auth_required)
        self.assertEqual(endpoint.auth_type, AuthType.NONE)
        self.assertEqual(endpoint.url_params, [])
        self.assertIsNone(endpoint.view_class)
        self.assertIsNone(endpoint.serializer_class)
        self.assertEqual(endpoint.permissions, [])
        self.assertIsNone(endpoint.description)

    # def test_apiendpoint_methods_validation(self):
    #     """Test that methods are properly validated and stored."""
    #     endpoint = APIEndpoint(
    #         path="/api/test/",
    #         methods=["GET", "POST"]  # String methods
    #     )
    #
    #     # Should convert string methods to APIMethod objects
    #     self.assertEqual(len(endpoint.methods), 2)
    #     self.assertIn(APIMethod.GET, endpoint.methods)
    #     self.assertIn(APIMethod.POST, endpoint.methods)

    def test_apiendpoint_url_params(self):
        """Test URL parameters handling."""
        endpoint = APIEndpoint(
            path="/api/users/{id}/{slug}/",
            url_params=[
                {"name": "id", "type": "integer", "description": "User ID"},
                {"name": "slug", "type": "string", "description": "User slug"}
            ]
        )
        
        self.assertEqual(len(endpoint.url_params), 2)
        self.assertEqual(endpoint.url_params[0]["name"], "id")
        self.assertEqual(endpoint.url_params[0]["type"], "integer")
        self.assertEqual(endpoint.url_params[0]["description"], "User ID")
        self.assertEqual(endpoint.url_params[1]["name"], "slug")
        self.assertEqual(endpoint.url_params[1]["type"], "string")

    def test_apiendpoint_string_representation(self):
        """Test string representation of APIEndpoint."""
        endpoint = APIEndpoint(
            path="/api/users/",
            name="UserListView",
            methods=[APIMethod.GET, APIMethod.POST]
        )
        
        expected_str = "/api/users/ [GET, POST] - UserListView"
        self.assertEqual(str(endpoint), expected_str)

    def test_apiendpoint_repr_representation(self):
        """Test repr representation of APIEndpoint."""
        endpoint = APIEndpoint(
            path="/api/users/",
            name="UserListView",
            app_name="users"
        )
        
        repr_str = repr(endpoint)
        self.assertIn("APIEndpoint", repr_str)
        self.assertIn("/api/users/", repr_str)
        self.assertIn("UserListView", repr_str)
        self.assertIn("users", repr_str)

    def test_apiendpoint_equality(self):
        """Test APIEndpoint equality comparison."""
        endpoint1 = APIEndpoint(
            path="/api/users/",
            name="UserListView",
            app_name="users"
        )
        
        endpoint2 = APIEndpoint(
            path="/api/users/",
            name="UserListView",
            app_name="users"
        )
        
        endpoint3 = APIEndpoint(
            path="/api/posts/",
            name="PostListView",
            app_name="posts"
        )
        
        self.assertEqual(endpoint1, endpoint2)
        self.assertNotEqual(endpoint1, endpoint3)

    # def test_apiendpoint_hashable(self):
    #     """Test that APIEndpoint objects are hashable."""
    #     endpoint1 = APIEndpoint(path="/api/users/", name="UserListView")
    #     endpoint2 = APIEndpoint(path="/api/posts/", name="PostListView")
    #
    #     # Test that we can create a set (requires hashable objects)
    #     endpoint_set = {endpoint1, endpoint2}
    #     self.assertEqual(len(endpoint_set), 2)

    def test_apiendpoint_to_dict(self):
        """Test converting endpoint to dictionary."""
        endpoint = APIEndpoint(
            path="/api/users/",
            name="UserListView",
            app_name="users",
            methods=[APIMethod.GET, APIMethod.POST],
            auth_required=True,
            auth_type=AuthType.TOKEN
        )
        
        endpoint_dict = endpoint.to_dict()
        
        self.assertIsInstance(endpoint_dict, dict)
        self.assertEqual(endpoint_dict["path"], "/api/users/")
        self.assertEqual(endpoint_dict["name"], "UserListView")
        self.assertEqual(endpoint_dict["app_name"], "users")
        self.assertEqual(endpoint_dict["methods"], ["GET", "POST"])
        self.assertTrue(endpoint_dict["auth_required"])
        self.assertEqual(endpoint_dict["auth_type"], "token")
        self.assertEqual(endpoint_dict["url_params"], [])
        self.assertEqual(endpoint_dict["url_param_names"], [])

    def test_apiendpoint_to_dict_with_url_params(self):
        """Test converting endpoint with URL parameters to dictionary."""
        endpoint = APIEndpoint(
            path="/api/users/{id}/",
            url_params=[
                {"name": "id", "type": "integer", "description": "User ID"}
            ]
        )
        
        endpoint_dict = endpoint.to_dict()
        
        self.assertEqual(len(endpoint_dict["url_params"]), 1)
        self.assertEqual(endpoint_dict["url_params"][0]["name"], "id")
        self.assertEqual(endpoint_dict["url_params"][0]["type"], "integer")
        self.assertEqual(endpoint_dict["url_params"][0]["description"], "User ID")
        
        # Check url_param_names for backward compatibility
        self.assertEqual(endpoint_dict["url_param_names"], ["id"])

    def test_apiendpoint_edge_cases(self):
        """Test APIEndpoint edge cases."""
        # Test with empty path
        endpoint = APIEndpoint(path="")
        self.assertEqual(endpoint.path, "")
        
        # Test with None values
        endpoint = APIEndpoint(
            path="/api/test/",
            name=None,
            app_name=None,
            view_class=None,
            serializer_class=None,
            description=None
        )
        
        self.assertEqual(endpoint.name, None)
        self.assertEqual(endpoint.app_name, None)
        self.assertIsNone(endpoint.view_class)
        self.assertIsNone(endpoint.serializer_class)
        self.assertIsNone(endpoint.description)

    # def test_apiendpoint_invalid_methods(self):
    #     """Test handling of invalid method types."""
    #     # Test with None methods
    #     endpoint = APIEndpoint(path="/api/test/", methods=None)
    #     self.assertEqual(endpoint.methods, [APIMethod.GET])
    #
    #     # Test with empty methods list
    #     endpoint = APIEndpoint(path="/api/test/", methods=[])
    #     self.assertEqual(endpoint.methods, [APIMethod.GET])

    # def test_apiendpoint_invalid_url_params(self):
    #     """Test handling of invalid URL parameters."""
    #     # Test with None url_params
    #     endpoint = APIEndpoint(path="/api/test/", url_params=None)
    #     self.assertEqual(endpoint.url_params, [])
    #
    #     # Test with empty url_params list
    #     endpoint = APIEndpoint(path="/api/test/", url_params=[])
    #     self.assertEqual(endpoint.url_params, [])

    # def test_apiendpoint_invalid_permissions(self):
    #     """Test handling of invalid permissions."""
    #     # Test with None permissions
    #     endpoint = APIEndpoint(path="/api/test/", permissions=None)
    #     self.assertEqual(endpoint.permissions, [])
    #
    #     # Test with empty permissions list
    #     endpoint = APIEndpoint(path="/api/test/", permissions=[])
    #     self.assertEqual(endpoint.permissions, [])


if __name__ == "__main__":
    unittest.main()
