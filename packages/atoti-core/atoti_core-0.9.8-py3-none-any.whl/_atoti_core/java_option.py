def java_option(key: str, value: str | None = None, /, *, prefix: str = "D") -> str:
    return f"-{prefix}{key}{'' if value is None else f'={value}'}"
