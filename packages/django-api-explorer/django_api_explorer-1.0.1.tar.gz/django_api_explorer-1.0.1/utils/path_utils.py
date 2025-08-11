import os


def join_url(host: str, path: str) -> str:
    """Join host and path to form a full URL."""
    if not host.startswith("http://") and not host.startswith("https://"):
        host = f"http://{host}"
    return f"{host.rstrip('/')}/{path.lstrip('/')}"


def is_url_pattern_excluded(path: str) -> bool:
    """
    Exclude admin, static, media, and debug paths.
    """
    excluded_prefixes = ["/admin", "/static", "/media", "/__debug__"]
    return any(path.startswith(prefix) for prefix in excluded_prefixes)


def get_project_root() -> str:
    """Return absolute path to the current project root."""
    return os.getcwd()
