from urllib.parse import urlparse


def url_2_name(url: str, level: int = 3) -> str:
    """
    Converts a URL into a name of format scheme:host:port:/limited/path.

    Args:
        url (str): The input URL.
        level (int): Maximum number of path segments to include.

    Returns:
        str: A formatted name string.
    """
    parsed = urlparse(url)
    scheme = parsed.scheme or "https"
    netloc = parsed.netloc or parsed.path.split('/')[0]
    path_parts = parsed.path.strip("/").split("/") if parsed.netloc else parsed.path.split("/")[1:]

    trimmed_path = "/" + "/".join(path_parts[:level]) if path_parts else "/"

    host = parsed.hostname or netloc
    port = parsed.port or (443 if scheme == "https" else 80)

    hostport = f"{host}:{port}"
    return f"{scheme}:{hostport}:{trimmed_path}"
