"""Message classes for bus communication."""

from dataclasses import dataclass
from typing import Any


@dataclass
class ExecuteFunctionRequest:
    """Message sent to request function execution."""
    exec_msg: Any


@dataclass
class LogMessage:
    """Message for log forwarding."""
    level: str
    message: str