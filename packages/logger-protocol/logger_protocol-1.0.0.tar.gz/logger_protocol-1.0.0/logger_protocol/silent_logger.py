from typing import Any

from .logger_protocol import LoggerProtocol


class SilentLogger(LoggerProtocol):
    """
    Logger with methods that no-op.
    Useful for conditionally silencing all logging.
    """

    @staticmethod
    def debug(*args: Any, **kwargs: Any) -> None: ...

    @staticmethod
    def info(*args: Any, **kwargs: Any) -> None: ...

    @staticmethod
    def warning(*args: Any, **kwargs: Any) -> None: ...

    @staticmethod
    def error(*args: Any, **kwargs: Any) -> None: ...

    @staticmethod
    def critical(*args: Any, **kwargs: Any) -> None: ...
