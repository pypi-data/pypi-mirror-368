# Logger Protocol
Python protocol for the standard lib Logger and Logger-like classes.

```python
import logging

from logger_protocol import LoggerProtocol, SilentLogger


class MyClass:
    _logger: LoggerProtocol

    def __init__(self, verbose: bool = True):
        self._logger = logging.getLogger(__name__) if verbose else SilentLogger
```