import json
from urllib.parse import urljoin


class APIFormatter:
    def __init__(self, allowed_hosts=None):
        """
        allowed_hosts: list of host strings from Django settings
        """
        self.allowed_hosts = allowed_hosts or []

    def _get_base_url(self, selected_host=None):
        if not self.allowed_hosts:
            return ""
        if selected_host:
            return f"http://{selected_host}"
        return f"http://{self.allowed_hosts[0]}"

    def format_plain(self, endpoints, with_host=False, selected_host=None):
        """
        Returns a simple list of endpoints.
        If with_host=True, includes full domain.
        """
        base_url = self._get_base_url(selected_host) if with_host else ""
        lines = []
        for ep in endpoints:
            url = urljoin(base_url, ep["path"]) if base_url else ep["path"]
            methods = ", ".join(ep.get("methods", []))
            lines.append(f"{url} [{methods}]")
        return "\n".join(lines)

    def format_json(self, endpoints, with_host=False, selected_host=None):
        """
        Returns JSON string of endpoints.
        """
        base_url = self._get_base_url(selected_host) if with_host else ""
        formatted = []
        for ep in endpoints:
            data = ep.copy()
            if base_url:
                data["full_url"] = urljoin(base_url, ep["path"])
            formatted.append(data)
        return json.dumps(formatted, indent=2)

    def format_curl(
        self, endpoints, selected_host=None, with_payload=False, with_auth=False
    ):
        """
        Returns curl commands for endpoints.

        Args:
            endpoints: List of endpoint dictionaries or APIEndpoint objects
            selected_host: Host to use for the base URL
            with_payload: Whether to include sample payloads for POST/PUT/PATCH
            with_auth: Whether to include authentication headers
        """
        base_url = self._get_base_url(selected_host)
        lines = []

        # Import data factory for realistic payloads
        try:
            from .data_factory import data_factory
        except ImportError:
            data_factory = None

        for ep in endpoints:
            if not base_url:
                raise ValueError("Allowed host is required for cURL formatting.")

            # Handle both dict and APIEndpoint objects
            if isinstance(ep, dict):
                path = ep.get("path", "")
                methods = ep.get("methods", ["GET"])
                auth_required = ep.get("auth_required", False)
                auth_type = ep.get("auth_type")
            else:
                path = ep.path
                methods = [m.value if hasattr(m, "value") else m for m in ep.methods]
                auth_required = ep.auth_required
                auth_type = ep.auth_type

            full_url = urljoin(base_url, path)

            for method in methods:
                method = method.upper()
                curl_cmd = f'curl -X {method} "{full_url}"'

                # Add headers
                if method in ["POST", "PUT", "PATCH"]:
                    curl_cmd += ' -H "Content-Type: application/json"'

                # Add authentication headers if requested
                if with_auth and auth_required:
                    if auth_type:
                        if "jwt" in str(auth_type).lower():
                            curl_cmd += ' -H "Authorization: Bearer YOUR_JWT_TOKEN"'
                        elif "token" in str(auth_type).lower():
                            curl_cmd += ' -H "Authorization: Token YOUR_TOKEN"'
                        elif "basic" in str(auth_type).lower():
                            curl_cmd += (
                                ' -H "Authorization: Basic base64_encoded_credentials"'
                            )
                        else:
                            curl_cmd += ' -H "Authorization: Bearer YOUR_TOKEN"'
                    else:
                        curl_cmd += ' -H "Authorization: Bearer YOUR_TOKEN"'

                # Add realistic payload if requested and available
                if with_payload and method in ["POST", "PUT", "PATCH"] and data_factory:
                    try:
                        # Convert endpoint dict to APIEndpoint object if needed
                        if isinstance(ep, dict):
                            from .models import APIEndpoint

                            endpoint_obj = APIEndpoint(
                                path=ep.get("path", ""),
                                name=ep.get("name", ""),
                                app_name=ep.get("app_name", ""),
                                methods=ep.get("methods", []),
                                auth_required=ep.get("auth_required", False),
                                auth_type=ep.get("auth_type", None),
                                url_params=ep.get("url_params", []),
                                view_class=ep.get("view_class", ""),
                                serializer_class=ep.get("serializer_class", ""),
                                permissions=ep.get("permissions", []),
                                description=ep.get("description", ""),
                            )
                        else:
                            endpoint_obj = ep

                        payload = data_factory.generate_sample_data(
                            endpoint_obj, method
                        )
                        if payload:
                            import json

                            payload_json = json.dumps(payload, indent=2)
                            # Escape for shell compatibility
                            payload_json = payload_json.replace("'", "'\"'\"'").replace(
                                "\n", "\\n"
                            )
                            curl_cmd += f" -d '{payload_json}'"
                        else:
                            # Fallback to generic payload
                            curl_cmd += ' -d \'{"key": "value"}\''
                    except Exception:
                        # Fallback to generic payload on error
                        curl_cmd += ' -d \'{"key": "value"}\''
                elif with_payload and method in ["POST", "PUT", "PATCH"]:
                    # Fallback when data factory is not available
                    curl_cmd += ' -d \'{"key": "value"}\''

                lines.append(curl_cmd)

        return "\n".join(lines)

    def format_as_html(self, endpoints, with_host=False, selected_host=None):
        """
        Returns HTML table for endpoints.
        """
        base_url = self._get_base_url(selected_host) if with_host else ""
        rows = []
        for ep in endpoints:
            url = urljoin(base_url, ep["path"]) if base_url else ep["path"]
            methods = ", ".join(ep.get("methods", []))
            rows.append(
                f"<tr><td>{url}</td><td>{methods}</td><td>{ep.get('name', '')}</td></tr>"
            )

        html = f"""
        <html>
        <head>
            <title>API Endpoints</title>
            <style>
                table {{
                    border-collapse: collapse;
                    width: 100%;
                }}
                th, td {{
                    border: 1px solid #ddd;
                    padding: 8px;
                }}
                th {{
                    background-color: #f2f2f2;
                    text-align: left;
                }}
            </style>
        </head>
        <body>
            <h2>API Endpoints</h2>
            <table>
                <tr><th>URL</th><th>Methods</th><th>Name</th></tr>
                {''.join(rows)}
            </table>
        </body>
        </html>
        """
        return html

    def format_openapi(
        self, endpoints, title="Django API", version="1.0.1", base_url=""
    ):
        """
        Returns OpenAPI 3.0 specification in JSON format.

        Args:
            endpoints: List of endpoint dictionaries or APIEndpoint objects
            title: API title
            version: API version
            base_url: Base URL for the API
        """
        openapi_spec = {
            "openapi": "3.0.0",
            "info": {
                "title": title,
                "version": version,
                "description": "Auto-generated API documentation from Django project",
            },
            "servers": [
                {
                    "url": base_url or "http://localhost:8000",
                    "description": "Development server",
                }
            ],
            "paths": {},
            "components": {
                "securitySchemes": {
                    "bearerAuth": {
                        "type": "http",
                        "scheme": "bearer",
                        "bearerFormat": "JWT",
                    },
                    "tokenAuth": {"type": "http", "scheme": "bearer"},
                }
            },
        }

        for ep in endpoints:
            # Handle both dict and APIEndpoint objects
            if isinstance(ep, dict):
                path = ep.get("path", "")
                methods = ep.get("methods", ["GET"])
                name = ep.get("name", "")
                auth_required = ep.get("auth_required", False)
                auth_type = ep.get("auth_type")
                url_params = ep.get("url_params", [])
                description = ep.get("description", "")
            else:
                path = ep.path
                methods = [m.value if hasattr(m, "value") else m for m in ep.methods]
                name = ep.name
                auth_required = ep.auth_required
                auth_type = ep.auth_type
                url_params = ep.url_params
                description = description = ep.description or ""

            # Normalize path for OpenAPI
            openapi_path = path
            for param in url_params:
                param_name = param.get("name", "")
                if param_name:
                    openapi_path = openapi_path.replace(
                        f"{{{param_name}}}", f"{{{param_name}}}"
                    )

            if openapi_path not in openapi_spec["paths"]:
                openapi_spec["paths"][openapi_path] = {}

            for method in methods:
                method_lower = method.lower()
                if method_lower in ["get", "post", "put", "patch", "delete"]:
                    operation = {
                        "summary": name or f"{method.upper()} {path}",
                        "description": description
                        or f"{method.upper()} operation for {path}",
                        "tags": [
                            (
                                ep.get("app_name", "default")
                                if isinstance(ep, dict)
                                else ep.app_name or "default"
                            )
                        ],
                    }

                    # Add parameters if URL has parameters
                    if url_params:
                        operation["parameters"] = []
                        for param in url_params:
                            param_spec = {
                                "name": param.get("name", ""),
                                "in": "path",
                                "required": True,
                                "schema": {
                                    "type": param.get("type", "string"),
                                    "format": param.get("format", "string"),
                                },
                                "description": param.get(
                                    "description", f"Parameter: {param.get('name', '')}"
                                ),
                            }
                            operation["parameters"].append(param_spec)

                    # Add security if authentication is required
                    if auth_required:
                        if auth_type and "jwt" in str(auth_type).lower():
                            operation["security"] = [{"bearerAuth": []}]
                        else:
                            operation["security"] = [{"bearerAuth": []}]

                    # Add request body for POST/PUT/PATCH
                    if method_lower in ["post", "put", "patch"]:
                        operation["requestBody"] = {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "key": {
                                                "type": "string",
                                                "description": "Example property",
                                            }
                                        },
                                    }
                                }
                            },
                        }

                    # Add responses
                    operation["responses"] = {
                        "200": {
                            "description": "Successful operation",
                            "content": {
                                "application/json": {"schema": {"type": "object"}}
                            },
                        },
                        "400": {"description": "Bad request"},
                        "401": {"description": "Unauthorized"},
                        "404": {"description": "Not found"},
                    }

                    openapi_spec["paths"][openapi_path][method_lower] = operation

        return json.dumps(openapi_spec, indent=2)

    def format_markdown(self, endpoints, title="Django API Documentation"):
        """
        Returns Markdown documentation for the API endpoints.

        Args:
            endpoints: List of endpoint dictionaries or APIEndpoint objects
            title: Documentation title
        """
        lines = [f"# {title}\n"]

        # Group endpoints by app
        app_endpoints = {}
        for ep in endpoints:
            if isinstance(ep, dict):
                app_name = ep.get("app_name", "Unknown")
                path = ep.get("path", "")
                methods = ep.get("methods", ["GET"])
                name = ep.get("name", "")
                auth_required = ep.get("auth_required", False)
                url_params = ep.get("url_params", [])
                description = ep.get("description", "")
            else:
                app_name = ep.app_name or "Unknown"
                path = ep.path
                methods = [m.value if hasattr(m, "value") else m for m in ep.methods]
                name = ep.name
                auth_required = ep.auth_required
                url_params = ep.url_params
                description = ep.description or ""

            if app_name not in app_endpoints:
                app_endpoints[app_name] = []
            app_endpoints[app_name].append(
                {
                    "path": path,
                    "methods": methods,
                    "name": name,
                    "auth_required": auth_required,
                    "url_params": url_params,
                    "description": description,
                }
            )

        # Generate documentation for each app
        for app_name, endpoints_list in sorted(app_endpoints.items()):
            lines.append(f"## {app_name}\n")

            for ep in endpoints_list:
                # Endpoint header
                methods_str = ", ".join(ep["methods"])
                auth_badge = "🔒" if ep["auth_required"] else "🔓"
                lines.append(f"### {ep['path']} [{methods_str}] {auth_badge}\n")

                # Description
                if ep["name"]:
                    lines.append(f"**Name:** {ep['name']}\n")

                if ep["description"]:
                    lines.append(f"**Description:** {ep['description']}\n")

                # URL parameters
                if ep["url_params"]:
                    lines.append("**URL Parameters:**\n")
                    for param in ep["url_params"]:
                        param_type = param.get("type", "string")
                        param_desc = param.get("description", "")
                        lines.append(
                            f"- `{param['name']}` ({param_type}) - {param_desc}\n"
                        )

                # Authentication
                if ep["auth_required"]:
                    lines.append("**Authentication:** Required\n")

                lines.append("---\n")

        return "\n".join(lines)


def format_as_text(endpoints, show_curl=False):
    """
    Format endpoints as plain text output.
    This is the main function used by the CLI.
    """
    if not endpoints:
        return "No endpoints found."

    lines = []
    for ep in endpoints:
        if isinstance(ep, dict):
            path = ep.get("path", "")
            methods = ep.get("methods", ["GET"])
            name = ep.get("name", "")
            full_url = ep.get("full_url", path)
        else:
            # Handle APIEndpoint objects
            path = ep.path
            methods = [m.value if hasattr(m, "value") else m for m in ep.methods]
            name = ep.name
            full_url = ep.full_url or path

        methods_str = ", ".join(methods)
        line = f"{full_url} [{methods_str}]"
        if name:
            line += f" - {name}"
        lines.append(line)

    return "\n".join(lines)


def format_as_html(endpoints, show_curl=False):
    """
    Format endpoints as HTML output.
    This is the main function used by the CLI for browser mode.
    """
    if not endpoints:
        return "<html><body><h2>No endpoints found.</h2></body></html>"

    rows = []
    for ep in endpoints:
        if isinstance(ep, dict):
            path = ep.get("path", "")
            methods = ep.get("methods", ["GET"])
            name = ep.get("name", "")
            full_url = ep.get("full_url", path)
            app_name = ep.get("app_name", "")
        else:
            # Handle APIEndpoint objects
            path = ep.path
            methods = [m.value if hasattr(m, "value") else m for m in ep.methods]
            name = ep.name
            full_url = ep.full_url or path
            app_name = ep.app_name

        # Create styled method badges
        method_badges = []
        for method in methods:
            method_lower = method.lower()
            method_badges.append(
                f'<span class="methods method-{method_lower}">{method}</span>'
            )

        methods_html = " ".join(method_badges)
        rows.append(
            f"""
            <tr>
                <td><code>{full_url}</code></td>
                <td>{methods_html}</td>
                <td>{name}</td>
                <td>{app_name}</td>
            </tr>
        """
        )

    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Django API Explorer</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #f5f5f5;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                overflow: hidden;
            }}
            h1 {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                margin: 0;
                padding: 20px;
                text-align: center;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 0;
            }}
            th, td {{
                padding: 12px 15px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }}
            th {{
                background-color: #f8f9fa;
                font-weight: 600;
                color: #495057;
            }}
            tr:hover {{
                background-color: #f8f9fa;
            }}
            .methods {{
                display: inline-block;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 12px;
                font-weight: 600;
                text-transform: uppercase;
            }}
            .methods {{
                background-color: #e9ecef;
                color: #495057;
            }}
            .method-get {{ background-color: #d4edda; color: #155724; }}
            .method-post {{ background-color: #d1ecf1; color: #0c5460; }}
            .method-put {{ background-color: #fff3cd; color: #856404; }}
            .method-patch {{ background-color: #fff3cd; color: #856404; }}
            .method-delete {{ background-color: #f8d7da; color: #721c24; }}
            code {{
                background-color: #f8f9fa;
                padding: 2px 4px;
                border-radius: 3px;
                font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
                font-size: 14px;
            }}
            .stats {{
                padding: 15px 20px;
                background-color: #e9ecef;
                border-bottom: 1px solid #ddd;
                font-size: 14px;
                color: #6c757d;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Django API Explorer</h1>
            <div class="stats">
                Found {len(endpoints)} API endpoints
            </div>
            <table>
                <thead>
                    <tr>
                        <th>Endpoint</th>
                        <th>Methods</th>
                        <th>Name</th>
                        <th>App</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(rows)}
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """

    return html
