def normalize_jdbc_url(url: str, /) -> str:
    prefix = "jdbc:"
    return url if url.startswith(prefix) else f"{prefix}{url}"
