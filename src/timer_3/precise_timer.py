from collections.abc import Callable

from PyQt6.QtCore import QElapsedTimer, QTimer


class PreciseTimer:
    """Точный таймер. Похож на QTimer, но компенсирует накопленный дрейф."""

    def __init__(self, interval_ms: int, callback: Callable[[], None]) -> None:
        self.interval = interval_ms
        self.callback = callback
        self.elapsed = QElapsedTimer()
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.setInterval(self.interval)
        self.timer.timeout.connect(self._on_timeout)
        self.tick_count = 0

    def start(self) -> None:
        self.elapsed.start()
        self.timer.start(0)

    def _on_timeout(self) -> None:
        self.tick_count += 1
        now = self.elapsed.elapsed()
        expected_time = self.tick_count * self.interval
        drift = now - expected_time

        self.callback()

        next_delay = max(0, self.interval - drift)
        self.timer.start(next_delay)
