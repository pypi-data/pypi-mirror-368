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

    def format_curl(self, endpoints, selected_host=None, with_payload=False):
        """
        Returns curl commands for endpoints.
        """
        base_url = self._get_base_url(selected_host)
        lines = []
        for ep in endpoints:
            if not base_url:
                raise ValueError("Allowed host is required for cURL formatting.")
            full_url = urljoin(base_url, ep["path"])
            methods = ep.get("methods", ["GET"])
            for method in methods:
                method = method.upper()
                if with_payload and method in ["POST", "PUT", "PATCH"]:
                    payload = '{"key": "value"}'
                    curl_cmd = f'curl -X {method} "{full_url}" -H "Content-Type: application/json" -d \'{payload}\''
                else:
                    curl_cmd = f'curl -X {method} "{full_url}"'
                lines.append(curl_cmd)
        return "\n".join(lines)

    def format_html(self, endpoints, with_host=False, selected_host=None):
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

        methods_str = ", ".join(methods)
        rows.append(
            f"""
            <tr>
                <td><code>{full_url}</code></td>
                <td><span class="methods">{methods_str}</span></td>
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
            .methods:contains("GET") {{ background-color: #d4edda; color: #155724; }}
            .methods:contains("POST") {{ background-color: #d1ecf1; color: #0c5460; }}
            .methods:contains("PUT") {{ background-color: #fff3cd; color: #856404; }}
            .methods:contains("DELETE") {{ background-color: #f8d7da; color: #721c24; }}
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
