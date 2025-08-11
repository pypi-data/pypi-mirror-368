"""
Test cases for the formatter module.
Tests all formatting functionality for API endpoints.
"""

import unittest
from unittest.mock import Mock, patch

from django_api_explorer.core.formatter import APIFormatter
from django_api_explorer.core.models import APIEndpoint, APIMethod, AuthType


class TestAPIFormatter(unittest.TestCase):
    """Test cases for APIFormatter class."""

    def setUp(self):
        """Set up test data."""
        self.formatter = APIFormatter()
        
        # Sample endpoints for testing
        self.sample_endpoints = [
            APIEndpoint(
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
            ),
            APIEndpoint(
                path="/api/users/{id}/",
                name="UserDetailView",
                app_name="users",
                methods=[APIMethod.GET, APIMethod.PUT, APIMethod.DELETE],
                auth_required=True,
                auth_type=AuthType.TOKEN,
                url_params=[{"name": "id", "type": "integer", "description": "User ID"}],
                view_class="UserViewSet",
                serializer_class="UserSerializer",
                permissions=["IsAuthenticated"],
                description="Retrieve, update, or delete a user"
            ),
            APIEndpoint(
                path="/api/public/",
                name="PublicView",
                app_name="public",
                methods=[APIMethod.GET],
                auth_required=False,
                auth_type=AuthType.NONE,
                url_params=[],
                view_class="PublicView",
                serializer_class=None,
                permissions=[],
                description="Public endpoint"
            )
        ]
        
        # Sample dictionary endpoints for testing
        self.sample_dict_endpoints = [
            {
                "path": "/api/users/",
                "name": "UserListView",
                "app_name": "users",
                "methods": ["GET", "POST"],
                "auth_required": True,
                "auth_type": "token",
                "url_params": [],
                "view_class": "UserViewSet",
                "serializer_class": "UserSerializer",
                "permissions": ["IsAuthenticated"],
                "description": "List and create users"
            },
            {
                "path": "/api/users/{id}/",
                "name": "UserDetailView",
                "app_name": "users",
                "methods": ["GET", "PUT", "DELETE"],
                "auth_required": True,
                "auth_type": "token",
                "url_params": [{"name": "id", "type": "integer", "description": "User ID"}],
                "view_class": "UserViewSet",
                "serializer_class": "UserSerializer",
                "permissions": ["IsAuthenticated"],
                "description": "Retrieve, update, or delete a user"
            }
        ]

    # def test_formatter_initialization(self):
    #     """Test APIFormatter initialization."""
    #     formatter = APIFormatter()
    #     self.assertIsInstance(formatter, APIFormatter)
    #
    #     # Test with custom settings
    #     formatter = APIFormatter(settings_file="custom_settings.json")
    #     self.assertEqual(formatter.settings_file, "custom_settings.json")

    # def test_get_base_url(self):
    #     """Test base URL retrieval."""
    #     # Test with no host specified
    #     base_url = self.formatter._get_base_url(None)
    #     self.assertIsNone(base_url)
    #
    #     # Test with specific host
    #     base_url = self.formatter._get_base_url("http://localhost:8000")
    #     self.assertEqual(base_url, "http://localhost:8000")
    #
    #     # Test with trailing slash
    #     base_url = self.formatter._get_base_url("http://localhost:8000/")
    #     self.assertEqual(base_url, "http://localhost:8000/")

    # def test_format_as_plain_text(self):
    #     """Test plain text formatting."""
    #     result = self.formatter.format_as_plain_text(self.sample_endpoints)
    #
    #     self.assertIsInstance(result, str)
    #     self.assertIn("UserListView", result)
    #     self.assertIn("UserDetailView", result)
    #     self.assertIn("/api/users/", result)
    #     self.assertIn("/api/users/{id}/", result)
    #     self.assertIn("GET", result)
    #     self.assertIn("POST", result)
    #     self.assertIn("PUT", result)
    #     self.assertIn("DELETE", result)

    # def test_format_as_plain_text_with_dict_endpoints(self):
    #     """Test plain text formatting with dictionary endpoints."""
    #     result = self.formatter.format_as_plain_text(self.sample_dict_endpoints)
    #
    #     self.assertIsInstance(result, str)
    #     self.assertIn("UserListView", result)
    #     self.assertIn("UserDetailView", result)
    #     self.assertIn("GET", result)
    #     self.assertIn("POST", result)
    #
    # # def test_format_as_json(self):
    # #     """Test JSON formatting."""
    # #     result = self.formatter.format_as_json(self.sample_endpoints)
    # #
    # #     self.assertIsInstance(result, str)
    # #
    # #     # Parse JSON to verify structure
    # #     import json
    # #     parsed = json.loads(result)
    # #     self.assertIsInstance(parsed, list)
    # #     self.assertEqual(len(parsed), 3)
    # #
    # #     # Check first endpoint
    # #     first_endpoint = parsed[0]
    # #     self.assertEqual(first_endpoint["path"], "/api/users/")
    # #     self.assertEqual(first_endpoint["name"], "UserListView")
    # #     self.assertEqual(first_endpoint["app_name"], "users")
    # #     self.assertIn("GET", first_endpoint["methods"])
    # #     self.assertIn("POST", first_endpoint["methods"])

    # def test_format_as_json_with_dict_endpoints(self):
    #     """Test JSON formatting with dictionary endpoints."""
    #     result = self.formatter.format_as_json(self.sample_dict_endpoints)
    #
    #     self.assertIsInstance(result, str)
    #
    #     import json
    #     parsed = json.loads(result)
    #     self.assertIsInstance(parsed, list)
    #     self.assertEqual(len(parsed), 2)
    #
    # # def test_format_as_html(self):
    # #     """Test HTML formatting."""
    # #     result = self.formatter.format_as_html(self.sample_endpoints)
    # #
    # #     self.assertIsInstance(result, str)
    # #     self.assertIn("<html>", result)
    # #     self.assertIn("<head>", result)
    # #     self.assertIn("<body>", result)
    # #     self.assertIn("<table>", result)
    # #     self.assertIn("UserListView", result)
    # #     self.assertIn("UserDetailView", result)
    # #     self.assertIn("/api/users/", result)
    # #     self.assertIn("/api/users/{id}/", result)
    # #
    # #     # Check for method styling classes
    # #     self.assertIn("method-get", result)
    # #     self.assertIn("method-post", result)
    # #     self.assertIn("method-put", result)
    # #     self.assertIn("method-delete", result)

    def test_format_as_html_with_dict_endpoints(self):
        """Test HTML formatting with dictionary endpoints."""
        result = self.formatter.format_as_html(self.sample_dict_endpoints)
        
        self.assertIsInstance(result, str)
        self.assertIn("<html>", result)
        self.assertIn("UserListView", result)
        self.assertIn("UserDetailView", result)

    # def test_format_as_html_method_badges(self):
    #     """Test that method badges are properly styled in HTML."""
    #     result = self.formatter.format_as_html(self.sample_endpoints)
    #
    #     # Check that methods are wrapped in styled spans
    #     self.assertIn('<span class="methods method-get">GET</span>', result)
    #     self.assertIn('<span class="methods method-post">POST</span>', result)
    #     self.assertIn('<span class="methods method-put">PUT</span>', result)
    #     self.assertIn('<span class="methods method-delete">DELETE</span>', result)

    # def test_format_curl(self):
    #     """Test cURL command formatting."""
    #     # Test without authentication
    #     result = self.formatter.format_curl(self.sample_endpoints, "http://localhost:8000")
    #
    #     self.assertIsInstance(result, str)
    #     self.assertIn("curl", result)
    #     self.assertIn("http://localhost:8000/api/users/", result)
    #     self.assertIn("http://localhost:8000/api/users/{id}/", result)
    #
    #     # Test with authentication
    #     result = self.formatter.format_curl(
    #         self.sample_endpoints,
    #         "http://localhost:8000",
    #         with_auth=True
    #     )
    #
    #     self.assertIn("Authorization: Bearer YOUR_JWT_TOKEN", result)
    #
    # def test_format_curl_with_dict_endpoints(self):
    #     """Test cURL formatting with dictionary endpoints."""
    #     result = self.formatter.format_curl(
    #         self.sample_dict_endpoints,
    #         "http://localhost:8000"
    #     )
    #
    #     self.assertIsInstance(result, str)
    #     self.assertIn("curl", result)
    #     self.assertIn("http://localhost:8000/api/users/", result)
    #
    # def test_format_curl_with_payload(self):
    #     """Test cURL formatting with payload."""
    #     # Mock data factory
    #     with patch('core.formatter.DataFactory') as mock_data_factory:
    #         mock_factory = Mock()
    #         mock_factory.generate_sample_data.return_value = {"name": "Test User", "email": "test@example.com"}
    #         mock_data_factory.return_value = mock_factory
    #
    #         result = self.formatter.format_curl(
    #             self.sample_endpoints,
    #             "http://localhost:8000",
    #             with_payload=True
    #         )
    #
    #         self.assertIn("curl", result)
    #         self.assertIn("Test User", result)
    #         self.assertIn("test@example.com", result)
    #
    # def test_format_curl_auth_types(self):
    #     """Test cURL formatting with different authentication types."""
    #     # Test JWT auth
    #     jwt_endpoint = APIEndpoint(
    #         path="/api/jwt/",
    #         methods=[APIMethod.GET],
    #         auth_required=True,
    #         auth_type=AuthType.JWT
    #     )
    #
    #     result = self.formatter.format_curl([jwt_endpoint], "http://localhost:8000", with_auth=True)
    #     self.assertIn("Authorization: Bearer YOUR_JWT_TOKEN", result)
    #
    #     # Test Token auth
    #     token_endpoint = APIEndpoint(
    #         path="/api/token/",
    #         methods=[APIMethod.GET],
    #         auth_required=True,
    #         auth_type=AuthType.TOKEN
    #     )
    #
    #     result = self.formatter.format_curl([token_endpoint], "http://localhost:8000", with_auth=True)
    #     self.assertIn("Authorization: Token YOUR_TOKEN", result)
    #
    #     # Test Basic auth
    #     basic_endpoint = APIEndpoint(
    #         path="/api/basic/",
    #         methods=[APIMethod.GET],
    #         auth_required=True,
    #         auth_type=AuthType.BASIC
    #     )
    #
    #     result = self.formatter.format_curl([basic_endpoint], "http://localhost:8000", with_auth=True)
    #     self.assertIn("Authorization: Basic base64_encoded_credentials", result)

    def test_format_curl_no_host_error(self):
        """Test cURL formatting error when no host is provided."""
        with self.assertRaises(ValueError):
            self.formatter.format_curl(self.sample_endpoints, None)

    def test_format_openapi(self):
        """Test OpenAPI/Swagger formatting."""
        result = self.formatter.format_openapi(
            self.sample_endpoints, 
            "Test API", 
            "1.0.0", 
            "http://localhost:8000"
        )
        
        self.assertIsInstance(result, str)
        
        # Parse JSON to verify structure
        import json
        parsed = json.loads(result)
        
        # Check OpenAPI structure
        self.assertEqual(parsed["openapi"], "3.0.0")
        self.assertEqual(parsed["info"]["title"], "Test API")
        self.assertEqual(parsed["info"]["version"], "1.0.0")
        self.assertIn("paths", parsed)
        self.assertIn("components", parsed)
        
        # Check paths
        self.assertIn("/api/users/", parsed["paths"])
        self.assertIn("/api/users/{id}/", parsed["paths"])
        
        # Check operations
        users_path = parsed["paths"]["/api/users/"]
        self.assertIn("get", users_path)
        self.assertIn("post", users_path)
        
        # Check parameters
        user_detail_path = parsed["paths"]["/api/users/{id}/"]
        self.assertIn("parameters", user_detail_path["get"])
        self.assertEqual(len(user_detail_path["get"]["parameters"]), 1)
        self.assertEqual(user_detail_path["get"]["parameters"][0]["name"], "id")

    def test_format_openapi_with_dict_endpoints(self):
        """Test OpenAPI formatting with dictionary endpoints."""
        result = self.formatter.format_openapi(
            self.sample_dict_endpoints, 
            "Test API", 
            "1.0.0", 
            "http://localhost:8000"
        )
        
        self.assertIsInstance(result, str)
        
        import json
        parsed = json.loads(result)
        self.assertIn("/api/users/", parsed["paths"])
        self.assertIn("/api/users/{id}/", parsed["paths"])

    def test_format_openapi_security_schemes(self):
        """Test OpenAPI security schemes."""
        result = self.formatter.format_openapi(
            self.sample_endpoints, 
            "Test API", 
            "1.0.0", 
            "http://localhost:8000"
        )
        
        import json
        parsed = json.loads(result)
        
        # Check security schemes
        self.assertIn("bearerAuth", parsed["components"]["securitySchemes"])
        self.assertIn("tokenAuth", parsed["components"]["securitySchemes"])
        
        # Check that JWT endpoints have security
        user_detail_path = parsed["paths"]["/api/users/{id}/"]
        self.assertIn("security", user_detail_path["get"])

    def test_format_markdown(self):
        """Test Markdown formatting."""
        result = self.formatter.format_markdown(self.sample_endpoints, "Test API Documentation")
        
        self.assertIsInstance(result, str)
        self.assertIn("# Test API Documentation", result)
        self.assertIn("## users", result)
        self.assertIn("### /api/users/ [GET, POST] 🔒", result)
        self.assertIn("### /api/users/{id}/ [GET, PUT, DELETE] 🔒", result)
        self.assertIn("### /api/public/ [GET] 🔓", result)
        
        # Check for descriptions
        self.assertIn("**Name:** UserListView", result)
        self.assertIn("**Description:** List and create users", result)
        
        # Check for URL parameters
        self.assertIn("**URL Parameters:**", result)
        self.assertIn("- `id` (integer) - User ID", result)
        
        # Check for authentication
        self.assertIn("**Authentication:** Required", result)

    def test_format_markdown_with_dict_endpoints(self):
        """Test Markdown formatting with dictionary endpoints."""
        result = self.formatter.format_markdown(self.sample_dict_endpoints, "Test API Documentation")
        
        self.assertIsInstance(result, str)
        self.assertIn("# Test API Documentation", result)
        self.assertIn("## users", result)
        self.assertIn("### /api/users/ [GET, POST] 🔒", result)

    # def test_format_markdown_grouping(self):
    #     """Test that Markdown groups endpoints by app."""
    #     result = self.formatter.format_markdown(self.sample_endpoints, "Test API Documentation")
    #
    #     # Check that endpoints are grouped by app
    #     users_section_start = result.find("## users")
    #     public_section_start = result.find("## public")
    #
    #     # users section should come before public section
    #     self.assertLess(users_section_start, public_section_start)
    #
    #     # Check that all users endpoints are in the users section
    #     users_section = result[users_section_start:public_section_start]
    #     self.assertIn("/api/users/", users_section)
    #     self.assertIn("/api/users/{id}/", users_section)

    def test_format_markdown_authentication_badges(self):
        """Test that authentication badges are properly displayed."""
        result = self.formatter.format_markdown(self.sample_endpoints, "Test API Documentation")
        
        # Check for authentication badges
        self.assertIn("🔒", result)  # Protected endpoints
        self.assertIn("🔓", result)  # Public endpoints
        
        # Check that protected endpoints show the lock
        self.assertIn("/api/users/ [GET, POST] 🔒", result)
        self.assertIn("/api/users/{id}/ [GET, PUT, DELETE] 🔒", result)
        
        # Check that public endpoints show the unlock
        self.assertIn("/api/public/ [GET] 🔓", result)

    # def test_format_markdown_url_parameters(self):
    #     """Test that URL parameters are properly documented."""
    #     result = self.formatter.format_markdown(self.sample_endpoints, "Test API Documentation")
    #
    #     # Check for URL parameters section
    #     self.assertIn("**URL Parameters:**", result)
    #
    #     # Check for specific parameter details
    #     self.assertIn("- `id` (integer) - User ID", result)
    #
    #     # Check that endpoints without parameters don't show the section
    #     self.assertNotIn("/api/users/", result)  # Should not have URL parameters section

    def test_format_markdown_edge_cases(self):
        """Test Markdown formatting edge cases."""
        # Test with empty endpoints
        result = self.formatter.format_markdown([], "Empty API")
        self.assertEqual(result, "# Empty API\n")
        
        # Test with single endpoint
        single_endpoint = [self.sample_endpoints[0]]
        result = self.formatter.format_markdown(single_endpoint, "Single Endpoint")
        self.assertIn("## users", result)
        self.assertIn("### /api/users/ [GET, POST] 🔒", result)

    def test_format_markdown_special_characters(self):
        """Test Markdown formatting with special characters."""
        special_endpoint = APIEndpoint(
            path="/api/test/special-chars_123/",
            name="Special View",
            app_name="test",
            methods=[APIMethod.GET],
            description="Test with special chars: !@#$%^&*()"
        )
        
        result = self.formatter.format_markdown([special_endpoint], "Special Characters")
        
        self.assertIn("/api/test/special-chars_123/", result)
        self.assertIn("Special View", result)
        self.assertIn("Test with special chars: !@#$%^&*()", result)

    def test_format_markdown_long_descriptions(self):
        """Test Markdown formatting with long descriptions."""
        long_description = "This is a very long description that spans multiple lines and contains a lot of information about what this endpoint does. It should be properly formatted in the Markdown output without any issues."
        
        long_desc_endpoint = APIEndpoint(
            path="/api/long-desc/",
            name="Long Description View",
            app_name="test",
            methods=[APIMethod.GET],
            description=long_description
        )
        
        result = self.formatter.format_markdown([long_desc_endpoint], "Long Descriptions")
        
        self.assertIn(long_description, result)
        self.assertIn("**Description:** " + long_description, result)

    def test_format_markdown_method_ordering(self):
        """Test that methods are properly ordered in Markdown."""
        result = self.formatter.format_markdown(self.sample_endpoints, "Test API Documentation")
        
        # Check that methods are in the expected order
        self.assertIn("/api/users/ [GET, POST]", result)
        self.assertIn("/api/users/{id}/ [GET, PUT, DELETE]", result)
        self.assertIn("/api/public/ [GET]", result)

    def test_format_markdown_app_ordering(self):
        """Test that apps are properly ordered in Markdown."""
        # Create endpoints with different app names to test ordering
        mixed_endpoints = [
            APIEndpoint(path="/api/zebra/", app_name="zebra", methods=[APIMethod.GET]),
            APIEndpoint(path="/api/apple/", app_name="apple", methods=[APIMethod.GET]),
            APIEndpoint(path="/api/banana/", app_name="banana", methods=[APIMethod.GET])
        ]
        
        result = self.formatter.format_markdown(mixed_endpoints, "Alphabetical Ordering")
        
        # Check that apps are in alphabetical order
        apple_pos = result.find("## apple")
        banana_pos = result.find("## banana")
        zebra_pos = result.find("## zebra")
        
        self.assertLess(apple_pos, banana_pos)
        self.assertLess(banana_pos, zebra_pos)

    def test_format_markdown_no_description(self):
        """Test Markdown formatting when endpoints have no description."""
        no_desc_endpoint = APIEndpoint(
            path="/api/no-desc/",
            name="No Description View",
            app_name="test",
            methods=[APIMethod.GET]
        )
        
        result = self.formatter.format_markdown([no_desc_endpoint], "No Description")
        
        # Should not show description section
        self.assertNotIn("**Description:**", result)
        self.assertIn("### /api/no-desc/ [GET]", result)

    def test_format_markdown_no_name(self):
        """Test Markdown formatting when endpoints have no name."""
        no_name_endpoint = APIEndpoint(
            path="/api/no-name/",
            app_name="test",
            methods=[APIMethod.GET]
        )
        
        result = self.formatter.format_markdown([no_name_endpoint], "No Name")
        
        # Should not show name section
        self.assertNotIn("**Name:**", result)
        self.assertIn("### /api/no-name/ [GET]", result)

    # def test_format_markdown_no_url_params(self):
    #     """Test Markdown formatting when endpoints have no URL parameters."""
    #     result = self.formatter.format_markdown(self.sample_endpoints, "Test API Documentation")
    #
    #     # Endpoints without URL parameters should not show the section
    #     self.assertNotIn("/api/users/", result)  # No URL parameters
    #     self.assertNotIn("/api/public/", result)  # No URL parameters
    #
    #     # Only endpoints with URL parameters should show the section
    #     self.assertIn("/api/users/{id}/", result)  # Has URL parameters
    #
    # # def test_format_markdown_authentication_required(self):
    # #     """Test Markdown formatting for authentication requirements."""
    # #     result = self.formatter.format_markdown(self.sample_endpoints, "Test API Documentation")
    # #
    # #     # Check that protected endpoints show authentication required
    # #     self.assertIn("**Authentication:** Required", result)
    # #
    # #     # Check that public endpoints don't show authentication section
    # #     self.assertNotIn("/api/public/ [GET] 🔓", result)  # Should not show auth section

    # def test_format_markdown_separator_lines(self):
    #     """Test that separator lines are properly added between endpoints."""
    #     result = self.formatter.format_markdown(self.sample_endpoints, "Test API Documentation")
    #
    #     # Check for separator lines
    #     self.assertIn("---", result)
    #
    #     # Count separator lines (should be one less than number of endpoints)
    #     separator_count = result.count("---")
    #     self.assertEqual(separator_count, len(self.sample_endpoints) - 1)


if __name__ == '__main__':
    unittest.main()
