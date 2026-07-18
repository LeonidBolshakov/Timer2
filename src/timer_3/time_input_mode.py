"""Режимы ввода времени обычного таймера."""

from enum import Enum, auto


class TimeInputMode(Enum):
    """Формат активной пары полей обычного таймера."""
    HM = auto()
    MS = auto()
