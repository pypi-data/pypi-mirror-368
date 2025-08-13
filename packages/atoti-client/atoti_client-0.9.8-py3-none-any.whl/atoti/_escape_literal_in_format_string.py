def escape_literal_in_format_string(string: str, /) -> str:
    """Escape the curly braces so that the passed string is left untouched by :func:`str.format`.

    Example:
        >>> result = escape_literal_in_format_string(r"{foo}bar{baz}")
        >>> result
        '{{foo}}bar{{baz}}'
        >>> result.format()
        '{foo}bar{baz}'

    """
    return string.replace(r"{", r"{{").replace(r"}", r"}}")
