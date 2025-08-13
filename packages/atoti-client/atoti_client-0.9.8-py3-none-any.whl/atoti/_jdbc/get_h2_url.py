from pathlib import Path


def get_h2_url(path: Path, /) -> str:
    return f"h2:{path.absolute() / 'content'}"
