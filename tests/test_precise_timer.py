from __future__ import annotations

import pytest

from timer_3 import precise_timer as precise_timer_module
from timer_3.precise_timer import PreciseTimer


class FakeSignal:
    def __init__(self) -> None:
        self.callback: object | None = None

    def connect(self, callback: object) -> None:
        self.callback = callback


class FakeQTimer:
    def __init__(self) -> None:
        self.timeout = FakeSignal()
        self.single_shot = False
        self.starts: list[int] = []
        self.stop_count = 0

    def setSingleShot(self, value: bool) -> None:
        self.single_shot = value

    def start(self, delay: int) -> None:
        self.starts.append(delay)

    def stop(self) -> None:
        self.stop_count += 1


class FakeElapsedTimer:
    def __init__(self) -> None:
        self.elapsed_value = 0
        self.start_count = 0

    def start(self) -> None:
        self.start_count += 1

    def elapsed(self) -> int:
        return self.elapsed_value


@pytest.fixture
def timer(monkeypatch: pytest.MonkeyPatch) -> PreciseTimer:
    monkeypatch.setattr(precise_timer_module, "QTimer", FakeQTimer)
    monkeypatch.setattr(precise_timer_module, "QElapsedTimer", FakeElapsedTimer)
    return PreciseTimer(1000, lambda: None)


def test_constructor_configures_single_shot_timer(timer: PreciseTimer) -> None:
    assert timer.timer.single_shot is True
    assert timer.timer.timeout.callback == timer._on_timeout


def test_restart_resets_timing_state(timer: PreciseTimer) -> None:
    timer.tick_count = 8

    timer.restart()

    assert timer.tick_count == 0
    assert timer.timer.stop_count == 1
    assert timer.elapsed.start_count == 1
    assert timer.timer.starts == [1000]


@pytest.mark.parametrize(
    ("elapsed", "expected_delay"),
    [(1100, 900), (2500, 0), (900, 1100)],
)
def test_timeout_compensates_for_drift(
    timer: PreciseTimer,
    elapsed: int,
    expected_delay: int,
) -> None:
    callbacks: list[str] = []
    timer.callback = lambda: callbacks.append("callback")
    timer.elapsed.elapsed_value = elapsed

    timer._on_timeout()

    assert timer.tick_count == 1
    assert callbacks == ["callback"]
    assert timer.timer.starts == [expected_delay]
