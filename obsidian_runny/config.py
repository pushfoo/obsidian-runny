import logging


class LogLevel(str):
    """Convert to upper case and validate as a known name.

    Raises:
        `ValueError` if it the name does not convert to a known
        upper-case value (i.e. `"info"` to `"INFO"`).
    """

    def __new__(cls, level_raw: str):
        level_upper = level_raw.upper()
        _mapping = logging.getLevelNamesMapping()
        level_int = _mapping.get(level_upper, None)
        if level_int is None:
            known_levels = ", ".join((
                repr(level) for level in _mapping.keys()
            ))
            raise ValueError(
                f"Invalid log level: {level_raw!r}."
                f" Expected one of: {known_levels}"
            )
        instance = super().__new__(cls, level_upper)
        setattr(instance, '_level_int', level_int)
        return instance
