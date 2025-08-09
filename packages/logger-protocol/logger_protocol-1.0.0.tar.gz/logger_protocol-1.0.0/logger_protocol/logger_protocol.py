from typing import Any, Protocol


class LoggerProtocol(Protocol):
    def debug(self, *args: Any, **kwargs: Any) -> None:
        """Log a debug message"""

    def info(self, *args: Any, **kwargs: Any) -> None:
        """Log an info message"""

    def warning(self, *args: Any, **kwargs: Any) -> None:
        """Log a warning message"""

    def error(self, *args: Any, **kwargs: Any) -> None:
        """Log an error message"""

    def critical(self, *args: Any, **kwargs: Any) -> None:
        """Log a critical message"""
