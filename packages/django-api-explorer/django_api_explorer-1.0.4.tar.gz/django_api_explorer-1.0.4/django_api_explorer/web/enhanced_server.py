import http.server
import json
import os
import socketserver
import tempfile
import threading
import webbrowser
from pathlib import Path


class EnhancedHTMLServer:
    def __init__(self, endpoints, port=8001, auto_open=True):
        """
        endpoints: List of APIEndpoint objects or dictionaries
        port: port number for the local server
        auto_open: if True, automatically open in browser
        """
        self.endpoints = endpoints
        self.port = port
        self.auto_open = auto_open
        self._temp_dir = tempfile.mkdtemp()

        # Copy template to temp directory
        template_path = Path(__file__).parent / "templates" / "enhanced_index.html"
        self._html_path = os.path.join(self._temp_dir, "index.html")

        if template_path.exists():
            with open(template_path, "r", encoding="utf-8") as f:
                html_content = f.read()

            with open(self._html_path, "w", encoding="utf-8") as f:
                f.write(html_content)

    def _start_server(self):
        handler = self._create_handler()
        os.chdir(self._temp_dir)

        with socketserver.TCPServer(("", self.port), handler) as httpd:
            print(f"🌐 Enhanced API Explorer running at http://localhost:{self.port}")
            if self.auto_open:
                webbrowser.open(f"http://localhost:{self.port}")
            httpd.serve_forever()

    def _create_handler(self):
        endpoints = self.endpoints
        static_dir = Path(__file__).parent / "static"

        class APIExplorerHandler(http.server.SimpleHTTPRequestHandler):
            def do_GET(self):
                if self.path == "/api/endpoints":
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()

                    # Convert endpoints to JSON-serializable format
                    json_endpoints = []
                    for ep in endpoints:
                        if hasattr(ep, "to_dict"):
                            # APIEndpoint object
                            ep_dict = ep.to_dict()
                        else:
                            # Dictionary
                            ep_dict = ep

                        # Ensure methods is always a list
                        if isinstance(ep_dict.get("methods"), str):
                            ep_dict["methods"] = [ep_dict["methods"]]
                        elif not isinstance(ep_dict.get("methods"), list):
                            ep_dict["methods"] = ["GET"]

                        # Ensure full_url is set with fallback host
                        if not ep_dict.get("full_url") and ep_dict.get("path"):
                            # Use default localhost if no host is configured
                            ep_dict["full_url"] = (
                                f"http://127.0.0.1:8000{ep_dict['path']}"
                            )

                        json_endpoints.append(ep_dict)

                    # Get unique apps and sort them
                    apps = sorted(
                        list(
                            set(
                                ep.get("app_name", "")
                                for ep in json_endpoints
                                if ep.get("app_name")
                            )
                        )
                    )

                    response_data = {
                        "endpoints": json_endpoints,
                        "total": len(json_endpoints),
                        "apps": apps,
                    }

                    self.wfile.write(json.dumps(response_data, indent=2).encode())
                elif self.path.startswith("/static/"):
                    # Serve static files
                    static_path = self.path[8:]  # Remove '/static/' prefix
                    file_path = static_dir / static_path

                    if file_path.exists() and file_path.is_file():
                        self.send_response(200)

                        # Set appropriate content type
                        if file_path.suffix == ".css":
                            self.send_header("Content-type", "text/css")
                        elif file_path.suffix == ".js":
                            self.send_header("Content-type", "application/javascript")
                        else:
                            self.send_header("Content-type", "application/octet-stream")

                        self.end_headers()

                        with open(file_path, "rb") as f:
                            self.wfile.write(f.read())
                    else:
                        self.send_error(404, "File not found")
                else:
                    # Serve the main HTML file
                    super().do_GET()

            def log_message(self, format, *args):
                # Suppress logging for cleaner output
                pass

        return APIExplorerHandler

    def start(self):
        """
        Start the server in a background thread so it doesn't block.
        """
        thread = threading.Thread(target=self._start_server, daemon=True)
        thread.start()


def run_enhanced_server(endpoints, port=8001, auto_open=True):
    """
    Start an enhanced local server to serve the new HTML interface.

    Args:
        endpoints: List of APIEndpoint objects or dictionaries
        port: Port number for the server (default: 8001)
        auto_open: Whether to automatically open in browser (default: True)
    """
    server = EnhancedHTMLServer(endpoints, port=port, auto_open=auto_open)
    server.start()

    print(f"🌐 Enhanced API Explorer started at http://localhost:{port}")
    print("Press Ctrl+C to stop the server")

    try:
        # Keep the main thread alive
        while True:
            import time

            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
