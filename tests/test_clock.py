from __future__ import annotations

from collections.abc import Callable

import pytest

from timer_3 import clock as clock_module
from timer_3.clock import Clock
from timer_3.const import Const as C


class FakePreciseTimer:
    def __init__(self, interval: int, callback: Callable[[], None]) -> None:
        self.interval = interval
        self.callback = callback
        self.calls: list[str] = []

    def start(self) -> None:
        self.calls.append("start")

    def stop(self) -> None:
        self.calls.append("stop")

    def restart(self) -> None:
        self.calls.append("restart")


@pytest.fixture
def clock(monkeypatch: pytest.MonkeyPatch) -> Clock:
    monkeypatch.setattr(clock_module, "PreciseTimer", FakePreciseTimer)
    return Clock()


def test_clock_constructs_precise_timer_with_expected_interval(clock: Clock) -> None:
    assert clock.timer.interval == C.TIMER_INTERVAL
    assert clock.timer.callback == clock.on_time_out


def test_timeout_emits_second_and_end_in_order(clock: Clock) -> None:
    events: list[tuple[str, int | None]] = []
    clock.seconds_left = 1
    clock.connect("a_second_passed", lambda value: events.append(("second", value)))
    clock.connect("end_of_timer", lambda: events.append(("end", None)))

    clock.on_time_out()

    assert clock.seconds_left == 0
    assert events == [("second", 0), ("end", None)]


def test_timeout_does_not_end_while_time_remains(clock: Clock) -> None:
    events: list[str] = []
    clock.seconds_left = 2
    clock.connect("a_second_passed", lambda _value: events.append("second"))
    clock.connect("end_of_timer", lambda: events.append("end"))

    clock.on_time_out()

    assert events == ["second"]


def test_start_stop_and_restart_delegate_to_precise_timer(clock: Clock) -> None:
    clock.start()
    clock.stop()
    clock.restart(42)

    assert clock.seconds_left == 42
    assert clock.timer.calls == ["start", "stop", "stop", "restart"]


def test_callback_failure_is_reported_as_fatal_error(
    clock: Clock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fatal_calls: list[tuple[str, str]] = []

    def fatal(title: str, text: str) -> None:
        fatal_calls.append((title, text))
        raise RuntimeError("fatal")

    monkeypatch.setattr(clock_module.traceback, "print_exc", lambda: None)
    monkeypatch.setattr(clock_module.f, "inform_fatal_error_and_quit", fatal)

    with pytest.raises(RuntimeError, match="fatal"):
        clock.callback("missing")

    assert fatal_calls[0][0] == C.TITLE_INTERNAL_ERROR
    assert "missing" in fatal_calls[0][1]
