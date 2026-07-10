from PyQt6.QtCore import QTimer

from . import functions as f


class CycleBeeper:
    def __init__(self) -> None:
        self._intervals: list[int] = []
        self._index = 0
        self._timer = QTimer()
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._on_timeout)

    def start(self, intervals: list[int]) -> None:
        if not intervals:
            return

        self._intervals = intervals
        self._index = 0
        self._start_next_timer()

    def stop(self) -> None:
        self._timer.stop()

    def _start_next_timer(self) -> None:
        interval_sec = self._intervals[self._index]
        self._timer.start(interval_sec * 1000)

    def _on_timeout(self) -> None:
        f.beep()

        self._index += 1
        if self._index >= len(self._intervals):
            self._index = 0

        self._start_next_timer()
