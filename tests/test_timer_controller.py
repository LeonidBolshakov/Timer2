from __future__ import annotations

from types import SimpleNamespace

import pytest

from timer_3 import timer_controller as controller_module
from timer_3.time_input_mode import TimeInputMode
from timer_3.timer_controller import Timer3Controller


class TimerFinished(RuntimeError):
    pass


class Field:
    def __init__(self, text: str = "") -> None:
        self._text = text

    def text(self) -> str:
        return self._text

    def setText(self, text: str) -> None:
        self._text = text


class FakeClock:
    def __init__(self, seconds_left: int = 0) -> None:
        self.seconds_left = seconds_left
        self.restarts: list[int] = []
        self.connections: dict[str, object] = {}

    def restart(self, seconds: int) -> None:
        self.seconds_left = seconds
        self.restarts.append(seconds)

    def connect(self, name: str, callback: object) -> None:
        self.connections[name] = callback


def make_controller(
    *,
    intervals: list[int] | None = None,
    repetitions: int = 3,
    endlessly: bool = False,
) -> Timer3Controller:
    controller = Timer3Controller.__new__(Timer3Controller)
    controller.window = SimpleNamespace(
        lineEdit_HM_H=Field(),
        lineEdit_HM_M=Field(),
        lineEdit_MS_M=Field(),
        lineEdit_MS_S=Field(),
        lblSec=Field(),
        lineEditCurrentInterval=Field(),
        lineEditIntervalDuration=Field(),
        lineEditLeft=Field(),
    )
    controller.context = SimpleNamespace(
        model=SimpleNamespace(
            cycle_intervals=intervals or [],
            cycle_repetitions=repetitions,
            endlessly=endlessly,
            voice_interval=10,
            beep_interval=3,
            beep_period_in_final=11,
        )
    )
    controller._clock = FakeClock()
    controller.inform_time = SimpleNamespace(
        informed=[],
        inform_voice=lambda seconds: controller.inform_time.informed.append(seconds),
        end_of_ordynary_timer=lambda: None,
    )
    controller._current_interval_index = 0
    controller._cycle_intervals_iter = iter([])
    controller._seconds_interval = 0
    controller._repetitions_count = repetitions
    return controller


def test_ordinary_tick_draws_zero_before_final_notifications() -> None:
    controller = make_controller()
    events: list[tuple[object, ...]] = []
    controller.active_time_field = lambda: TimeInputMode.MS
    controller._draw_min_sec = lambda minutes, seconds: events.append(
        ("draw", minutes, seconds)
    )
    controller.check_inform_voice_and_final_beep = lambda: events.append(("inform",))

    controller.for_ordinary_a_second_passed(0)

    assert events == [("draw", 0, 0), ("inform",)]


def test_ordinary_tick_draws_hours_minutes_and_seconds() -> None:
    controller = make_controller()
    controller.active_time_field = lambda: TimeInputMode.HM
    controller.check_inform_voice_and_final_beep = lambda: None

    controller.for_ordinary_a_second_passed(3661)

    assert controller.window.lineEdit_HM_H.text() == "01"
    assert controller.window.lineEdit_HM_M.text() == "01"
    assert controller.window.lblSec.text() == ": 01"


def test_prepare_ordinary_timer_uses_ordinary_end_callback() -> None:
    controller = make_controller()
    captured: list[object] = []
    controller._get_seconds_left = lambda: 90
    controller.prepare_timer = lambda *args: captured.extend(args)

    controller._prepare_start_tab_ordinary()

    assert captured[0] == 90
    assert captured[1] == controller.for_ordinary_a_second_passed
    assert captured[2] == controller.inform_time.end_of_ordynary_timer


def test_last_repetition_quits_without_starting_an_extra_cycle(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    controller = make_controller(intervals=[10], repetitions=1)
    controller._cycle_intervals_iter = iter([])

    def finish() -> None:
        raise TimerFinished

    monkeypatch.setattr(controller_module.f, "go_quit", finish)

    with pytest.raises(TimerFinished):
        controller.cycle_end_interval()

    assert controller._repetitions_count == 0
    assert controller._clock.restarts == []


def test_cycle_moves_to_next_interval_without_decrementing_repetitions(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    controller = make_controller(intervals=[10, 20], repetitions=2)
    controller._cycle_intervals_iter = iter([20])
    monkeypatch.setattr(controller_module.f, "beep", lambda: None)

    controller.cycle_end_interval()

    assert controller._repetitions_count == 2
    assert controller._current_interval_index == 1
    assert controller._clock.restarts == [20]
    assert controller.window.lineEditCurrentInterval.text() == "2"
    assert controller.window.lineEditIntervalDuration.text() == "20"
    assert controller.window.lineEditLeft.text() == "20"


def test_completed_cycle_starts_next_repetition(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    controller = make_controller(intervals=[10, 20], repetitions=2)
    controller._cycle_intervals_iter = iter([])
    monkeypatch.setattr(controller_module.f, "beep", lambda: None)
    monkeypatch.setattr(
        controller_module.f,
        "go_quit",
        lambda: pytest.fail("timer must continue"),
    )

    controller.cycle_end_interval()

    assert controller._repetitions_count == 1
    assert controller._current_interval_index == 0
    assert controller._clock.restarts == [10]
    assert controller.window.lineEditCurrentInterval.text() == "1"


def test_endless_cycle_wraps_without_changing_repetition_counter(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    controller = make_controller(intervals=[7], repetitions=3, endlessly=True)
    controller._cycle_intervals_iter = iter([])
    monkeypatch.setattr(controller_module.f, "beep", lambda: None)
    monkeypatch.setattr(
        controller_module.f,
        "go_quit",
        lambda: pytest.fail("endless timer must not quit"),
    )

    controller.cycle_end_interval()

    assert controller._repetitions_count == 3
    assert controller._clock.restarts == [7]


@pytest.mark.parametrize(
    ("seconds_left", "voice_calls", "beep_count"),
    [(10, [10], 0), (9, [], 1), (12, [], 0)],
)
def test_voice_and_final_beep_boundaries(
    monkeypatch: pytest.MonkeyPatch,
    seconds_left: int,
    voice_calls: list[int],
    beep_count: int,
) -> None:
    controller = make_controller()
    controller._clock.seconds_left = seconds_left
    beeps: list[bool] = []
    monkeypatch.setattr(controller_module.f, "beep", lambda: beeps.append(True))

    controller.check_inform_voice_and_final_beep()

    assert controller.inform_time.informed == voice_calls
    assert len(beeps) == beep_count


@pytest.mark.parametrize(
    ("mode", "values", "expected"),
    [
        (TimeInputMode.MS, ("", "", "02", "05"), 125),
        (TimeInputMode.HM, ("01", "02", "", ""), 3720),
        (None, ("", "", "", ""), 0),
    ],
)
def test_get_seconds_left(
    mode: TimeInputMode | None,
    values: tuple[str, str, str, str],
    expected: int,
) -> None:
    controller = make_controller()
    (
        controller.window.lineEdit_HM_H._text,
        controller.window.lineEdit_HM_M._text,
        controller.window.lineEdit_MS_M._text,
        controller.window.lineEdit_MS_S._text,
    ) = values
    controller.active_time_field = lambda: mode

    assert controller._get_seconds_left() == expected


def test_prepare_interval_initializes_first_repetition() -> None:
    controller = make_controller(intervals=[8, 13], repetitions=4)
    prepared: list[tuple[object, ...]] = []
    controller.prepare_timer = lambda *args: prepared.append(args)

    controller._prepare_start_tab_interval()

    assert controller._repetitions_count == 4
    assert controller._seconds_interval == 8
    assert prepared[0][0] == 8
    assert prepared[0][1] == controller.cycle_second_signal
    assert prepared[0][2] == controller.cycle_end_interval
    assert controller.window.lineEditCurrentInterval.text() == "1"
    assert controller.window.lineEditLeft.text() == "8"
