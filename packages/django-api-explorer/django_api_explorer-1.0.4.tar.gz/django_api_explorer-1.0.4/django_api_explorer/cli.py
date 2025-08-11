#!/usr/bin/env python3
"""
Django API Explorer CLI

A command-line tool to discover and document API endpoints in Django projects.
"""
import os
import sys

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from django_api_explorer.core import format_as_text
from django_api_explorer.core import (
    get_allowed_hosts,
    get_installed_apps,
    load_django_settings,
)
from django_api_explorer.core import URLPatternExtractor
from django_api_explorer.utils.path_utils import join_url
from django_api_explorer.web.enhanced_server import run_enhanced_server

console = Console()


@click.command()
@click.option(
    "--project-root",
    "-p",
    default=os.getcwd(),
    help="Path to your Django project root (default: current directory)",
)
@click.option(
    "--settings", "-s", help="Django settings module (e.g. myproject.settings.dev)"
)
@click.option("--app", "-a", help="Scan only a specific Django app")
@click.option(
    "--curl", is_flag=True, help="Generate curl commands instead of plain URLs"
)
@click.option(
    "--browser", "-b", is_flag=True, help="Open results in browser instead of terminal"
)
@click.option(
    "--watch",
    "-w",
    is_flag=True,
    help="Watch for file changes and auto-reload (requires --browser)",
)
@click.option("--json", "-j", is_flag=True, help="Output in JSON format")
@click.option("--output", "-o", help="Save output to file")
@click.option("--host", help="Override the host (e.g., localhost:8000)")
@click.option(
    "--port", type=int, default=8001, help="Port for the web server (default: 8001)"
)
@click.version_option(version="1.0.4", prog_name="django-api-explorer")
def main(project_root, settings, app, curl, browser, watch, json, output, host, port):
    """
    🚀 Django API Explorer

    Discover and document API endpoints in Django projects.

    Examples:
        django-api-explorer                    # Scan all apps
        django-api-explorer --app users        # Scan specific app
        django-api-explorer --browser          # Open in browser
        django-api-explorer --curl             # Generate curl commands
        django-api-explorer --json -o apis.json # Export as JSON
    """
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:

            # Step 1: Set project root in sys.path
            progress.add_task("Setting up project path...", total=None)
            sys.path.insert(0, project_root)

            # Step 2: Load Django settings
            progress.add_task("Loading Django settings...", total=None)
            try:
                load_django_settings(settings)
            except Exception as e:
                console.print(f"[red]Error loading Django settings: {e}[/red]")
                console.print(
                    "\n[yellow]Make sure you're in a Django project directory or specify --settings[/yellow]"
                )
                sys.exit(1)

            # Step 3: Get allowed hosts
            progress.add_task("Detecting hosts...", total=None)
            allowed_hosts = get_allowed_hosts()

            if not host:
                if not allowed_hosts:
                    console.print(
                        "⚠️  No ALLOWED_HOSTS found in settings. Using http://127.0.0.1:8000"
                    )
                    host = "http://127.0.0.1:8000"
                elif len(allowed_hosts) == 1:
                    host = _process_host(allowed_hosts[0])
                else:
                    console.print("\n[cyan]Available Hosts:[/cyan]")
                    for i, h in enumerate(allowed_hosts, 1):
                        console.print(f"  {i}. {h}")
                    choice = click.prompt("Select host number", type=int, default=1)
                    host = _process_host(allowed_hosts[choice - 1])
            else:
                host = _process_host(host)

            # Step 4: Get app choice if not provided
            if not app:
                progress.add_task("Detecting installed apps...", total=None)
                installed_apps = [
                    app for app in get_installed_apps() if not app.startswith("django.")
                ]

                if len(installed_apps) > 1:
                    console.print("\n[cyan]Installed Apps:[/cyan]")
                    for i, app_name in enumerate(installed_apps, 1):
                        console.print(f"  {i}. {app_name}")
                    console.print(f"  {len(installed_apps) + 1}. All apps")

                    choice = click.prompt(
                        "Select app number", type=int, default=len(installed_apps) + 1
                    )
                    if choice <= len(installed_apps):
                        app = installed_apps[choice - 1]

            # Step 5: Extract APIs
            progress.add_task("Extracting API endpoints...", total=None)
            extractor = URLPatternExtractor(project_root)
            if app:
                endpoints = extractor.extract_from_app(app)
                console.print(f"[green]Scanning app: {app}[/green]")
            else:
                endpoints = extractor.extract_all_endpoints()
                console.print("[green]Scanning all apps[/green]")

            if not endpoints:
                console.print("[yellow]No API endpoints found![/yellow]")
                console.print("\nMake sure your Django project has:")
                console.print("  • URL patterns defined in urls.py")
                console.print("  • Views that can be discovered")
                sys.exit(0)

            # Step 6: Attach host to endpoints
            progress.add_task("Processing endpoints...", total=None)
            full_endpoints = []
            for ep in endpoints:
                ep_dict = ep.to_dict()
                ep_dict["full_url"] = join_url(host, ep_dict["path"])
                full_endpoints.append(ep_dict)

            # Step 7: Output
            progress.add_task("Formatting output...", total=None)

            if browser:
                if watch:
                    # Use file watcher server
                    from django_api_explorer.web.file_watcher_server import run_file_watcher_server

                    console.print("🔄 Starting file watcher mode...")
                    console.print(
                        "📝 The UI will automatically reload when you make changes to your Django files"
                    )
                    console.print("🛑 Press Ctrl+C to stop the watcher")
                    run_file_watcher_server(project_root, settings, app, port)
                else:
                    # Use regular enhanced server
                    run_enhanced_server(full_endpoints, port)
            elif json:
                import json

                output_data = json.dumps(full_endpoints, indent=2)
                if output:
                    with open(output, "w") as f:
                        f.write(output_data)
                    console.print(f"[green]JSON saved to: {output}[/green]")
                else:
                    console.print(output_data)
            else:
                # Terminal output
                if curl:
                    from django_api_explorer.core import APIFormatter

                    formatter = APIFormatter([host])
                    output_text = formatter.format_curl(full_endpoints)
                else:
                    output_text = format_as_text(full_endpoints)

                if output:
                    with open(output, "w") as f:
                        f.write(output_text)
                    console.print(f"[green]Output saved to: {output}[/green]")
                else:
                    # Display in a nice table
                    table = Table(
                        title=f"🚀 Django API Explorer - {len(full_endpoints)} endpoints found"
                    )
                    table.add_column("Endpoint", style="cyan", no_wrap=True)
                    table.add_column("Methods", style="green")
                    table.add_column("Name", style="yellow")
                    table.add_column("App", style="magenta")

                    for ep in full_endpoints:
                        methods = ", ".join(ep.get("methods", ["GET"]))
                        name = ep.get("name", "")
                        app_name = ep.get("app_name", "")
                        table.add_row(ep["full_url"], methods, name, app_name)

                    console.print(table)

                    if curl:
                        console.print("\n[cyan]cURL Commands:[/cyan]")
                        console.print(output_text)

    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")
        sys.exit(1)


def _process_host(host):
    """Process and clean up the host string."""
    if not host:
        return "http://127.0.0.1:8000"

    # Remove wildcards and clean up
    host = str(host).strip()

    # Replace wildcards with localhost
    if host == "*" or host == "['*']":
        return "http://127.0.0.1:8000"

    # Remove quotes and brackets if present
    host = host.strip("'\"[]")

    # Add protocol if missing
    if not host.startswith(("http://", "https://")):
        host = f"http://{host}"

    return host


if __name__ == "__main__":
    main()
