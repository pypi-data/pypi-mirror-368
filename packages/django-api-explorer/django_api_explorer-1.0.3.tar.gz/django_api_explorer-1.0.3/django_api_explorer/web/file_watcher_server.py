import http.server
import json
import os
import queue
import socketserver
import tempfile
import threading
import time
import webbrowser
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class DjangoFileWatcher(FileSystemEventHandler):
    """Watch for changes in Django project files."""

    def __init__(self, project_root, callback):
        self.project_root = Path(project_root)
        self.callback = callback
        self.last_change = 0
        self.change_queue = queue.Queue()

        # Files to watch
        self.watch_patterns = [
            "**/*.py",  # Python files
            "**/urls.py",  # URL configurations
            "**/views.py",  # View files
            "**/models.py",  # Model files
            "**/serializers.py",  # DRF serializers
            "**/settings.py",  # Settings files
        ]

        # Files to ignore
        self.ignore_patterns = [
            "**/__pycache__/**",
            "**/*.pyc",
            "**/.git/**",
            "**/node_modules/**",
            "**/.venv/**",
            "**/venv/**",
            "**/env/**",
            "**/.pytest_cache/**",
            "**/migrations/**",
        ]

    def should_watch_file(self, file_path):
        """Check if a file should be watched."""
        file_path = Path(file_path)
        rel_path = file_path.relative_to(self.project_root)

        # Check ignore patterns
        for pattern in self.ignore_patterns:
            if rel_path.match(pattern):
                return False

        # Check watch patterns
        for pattern in self.watch_patterns:
            if rel_path.match(pattern):
                return True

        return False

    def on_modified(self, event):
        """Handle file modification events."""
        if event.is_directory:
            return

        if self.should_watch_file(event.src_path):
            current_time = time.time()
            # Debounce changes (ignore changes within 1 second)
            if current_time - self.last_change > 1:
                self.last_change = current_time
                print(f"🔄 File changed: {event.src_path}")
                self.change_queue.put(event.src_path)
                # Trigger callback in a separate thread to avoid blocking
                threading.Thread(target=self.callback, daemon=True).start()


class FileWatcherServer:
    def __init__(
        self, project_root, settings_module, app=None, port=8001, auto_open=True
    ):
        """
        Initialize the file watcher server.

        Args:
            project_root: Path to Django project root
            settings_module: Django settings module
            app: Specific app to watch (optional)
            port: Port for the web server
            auto_open: Whether to auto-open browser
        """
        self.project_root = Path(project_root)
        self.settings_module = settings_module
        self.app = app
        self.port = port
        self.auto_open = auto_open
        self._temp_dir = tempfile.mkdtemp()
        self.endpoints = []
        self.observer = None
        self.server_thread = None
        self.is_running = False

        # Copy template to temp directory
        template_path = Path(__file__).parent / "templates" / "enhanced_index.html"
        self._html_path = os.path.join(self._temp_dir, "index.html")

        if template_path.exists():
            with open(template_path, "r", encoding="utf-8") as f:
                html_content = f.read()

            # Add auto-reload JavaScript
            html_content = self._add_auto_reload_script(html_content)

            with open(self._html_path, "w", encoding="utf-8") as f:
                f.write(html_content)

    def _add_auto_reload_script(self, html_content):
        """Add auto-reload JavaScript to the HTML template."""
        auto_reload_script = """
        <script>
            // Auto-reload functionality
            let lastReloadTime = Date.now();
            let reloadCheckInterval;

            // Start checking for updates
            function startAutoReload() {
                reloadCheckInterval = setInterval(checkForUpdates, 2000);
            }

            // Check for updates
            function checkForUpdates() {
                fetch('/api/check-updates?t=' + Date.now())
                    .then(response => response.json())
                    .then(data => {
                        if (data.has_updates && data.last_update > lastReloadTime) {
                            console.log('🔄 Updates detected, reloading...');
                            lastReloadTime = Date.now();
                            location.reload();
                        }
                    })
                    .catch(error => {
                        console.log('Auto-reload check failed:', error);
                    });
            }

            // Start auto-reload when page loads
            document.addEventListener('DOMContentLoaded', function() {
                startAutoReload();
                console.log('🔄 Auto-reload enabled - watching for file changes...');
            });

            // Clean up on page unload
            window.addEventListener('beforeunload', function() {
                if (reloadCheckInterval) {
                    clearInterval(reloadCheckInterval);
                }
            });
        </script>
        """

        # Insert the script before the closing </body> tag
        if "</body>" in html_content:
            return html_content.replace("</body>", auto_reload_script + "</body>")
        else:
            return html_content + auto_reload_script

    def _extract_endpoints(self):
        """Extract endpoints from Django project."""
        try:
            # Set up Django environment
            os.environ.setdefault("DJANGO_SETTINGS_MODULE", self.settings_module)

            import django

            django.setup()

            # Import the extractor
            from django_api_explorer.core.url_extractor import URLPatternExtractor

            # Extract endpoints
            extractor = URLPatternExtractor(str(self.project_root))
            if self.app:
                self.endpoints = extractor.extract_from_app(self.app)
                print(
                    f"📊 Extracted {len(self.endpoints)} endpoints from app: {self.app}"
                )
            else:
                self.endpoints = extractor.extract_all_endpoints()
                print(f"📊 Extracted {len(self.endpoints)} endpoints from all apps")

            return True
        except Exception as e:
            print(f"❌ Error extracting endpoints: {e}")
            return False

    def _on_file_change(self):
        """Callback when files change."""
        print("🔄 File change detected, re-extracting endpoints...")
        if self._extract_endpoints():
            print("✅ Endpoints updated successfully")
        else:
            print("❌ Failed to update endpoints")

    def _start_file_watcher(self):
        """Start the file watcher."""
        self.observer = Observer()
        event_handler = DjangoFileWatcher(self.project_root, self._on_file_change)

        # Watch the project directory
        self.observer.schedule(event_handler, str(self.project_root), recursive=True)
        self.observer.start()
        print(f"👀 Watching for changes in: {self.project_root}")

    def _create_handler(self):
        """Create the HTTP request handler."""
        server_instance = self
        static_dir = Path(__file__).parent / "static"

        class FileWatcherHandler(http.server.SimpleHTTPRequestHandler):
            def do_GET(self):
                if self.path == "/api/endpoints":
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.send_header(
                        "Cache-Control", "no-cache, no-store, must-revalidate"
                    )
                    self.end_headers()

                    # Convert endpoints to JSON-serializable format
                    json_endpoints = []
                    for ep in server_instance.endpoints:
                        if hasattr(ep, "to_dict"):
                            ep_dict = ep.to_dict()
                        else:
                            ep_dict = ep

                        # Ensure methods is always a list
                        if isinstance(ep_dict.get("methods"), str):
                            ep_dict["methods"] = [ep_dict["methods"]]
                        elif not isinstance(ep_dict.get("methods"), list):
                            ep_dict["methods"] = ["GET"]

                        # Ensure full_url is set with fallback host
                        if not ep_dict.get("full_url") and ep_dict.get("path"):
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
                        "last_update": int(time.time() * 1000),  # Current timestamp
                    }

                    self.wfile.write(json.dumps(response_data, indent=2).encode())

                elif self.path.startswith("/api/check-updates"):
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.send_header(
                        "Cache-Control", "no-cache, no-store, must-revalidate"
                    )
                    self.end_headers()

                    # Check if there have been any file changes
                    has_updates = (
                        hasattr(server_instance, "_last_file_change")
                        and server_instance._last_file_change > 0
                    )

                    response_data = {
                        "has_updates": has_updates,
                        "last_update": getattr(server_instance, "_last_file_change", 0),
                    }

                    self.wfile.write(json.dumps(response_data).encode())

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

        return FileWatcherHandler

    def _start_server(self):
        """Start the HTTP server."""
        handler = self._create_handler()
        os.chdir(self._temp_dir)

        with socketserver.TCPServer(("", self.port), handler) as httpd:
            print(
                f"🌐 File Watcher API Explorer running at http://localhost:{self.port}"
            )
            if self.auto_open:
                webbrowser.open(f"http://localhost:{self.port}")
            httpd.serve_forever()

    def start(self):
        """Start the file watcher server."""
        self.is_running = True

        # Initial endpoint extraction
        print("🔍 Initial endpoint extraction...")
        if not self._extract_endpoints():
            print("❌ Failed to extract initial endpoints")
            return

        # Start file watcher
        self._start_file_watcher()

        # Start server in a separate thread
        self.server_thread = threading.Thread(target=self._start_server, daemon=True)
        self.server_thread.start()

        try:
            # Keep the main thread alive
            while self.is_running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutting down file watcher server...")
            self.stop()

    def stop(self):
        """Stop the file watcher server."""
        self.is_running = False
        if self.observer:
            self.observer.stop()
            self.observer.join()
        print("✅ File watcher server stopped")


def run_file_watcher_server(
    project_root, settings_module, app=None, port=8001, auto_open=True
):
    """Run the file watcher server."""
    server = FileWatcherServer(project_root, settings_module, app, port, auto_open)
    server.start()
