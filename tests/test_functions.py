from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from timer_3 import functions as f


class FatalError(RuntimeError):
    pass


@pytest.fixture
def fatal_error(monkeypatch: pytest.MonkeyPatch) -> list[tuple[str, str]]:
    calls: list[tuple[str, str]] = []

    def raise_fatal(title: str, text: str) -> None:
        calls.append((title, text))
        raise FatalError

    monkeypatch.setattr(f, "inform_fatal_error_and_quit", raise_fatal)
    return calls


@pytest.mark.parametrize(
    ("seconds", "expected"),
    [(0, (0, 0, 0)), (59, (0, 0, 59)), (3661, (1, 1, 1))],
)
def test_hour_minutes_sec(seconds: int, expected: tuple[int, int, int]) -> None:
    assert f.hour_minutes_sec(seconds) == expected


@pytest.mark.parametrize(
    ("number", "expected_index"),
    [(1, 1), (2, 2), (5, 0), (11, 0), (14, 0), (21, 1), (24, 2)],
)
def test_get_word_form(number: int, expected_index: int) -> None:
    forms = ["many", "one", "few"]

    assert f.get_word_form(number, forms) == forms[expected_index]


def test_time_to_text_combines_only_non_zero_parts(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        f,
        "num_to_text",
        lambda number, _gender, forms: f"{number} {forms[0]} " if number else "",
    )

    assert f.time_to_text(3661) == "1 часов 1 минут 1 секунд "


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("1 2 3", [1, 2, 3]),
        ("1,2;3\\4.5", [1, 2, 3, 4, 5]),
        ("", []),
        ("1 text", []),
        ("0 2", []),
        ("60", []),
    ],
)
def test_cycle_intervals_list(text: str, expected: list[int]) -> None:
    assert f.cycle_intervals_list(text) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [(7, 7), (" 12 ", 12), ("", 0)],
)
def test_to_int_accepts_supported_values(value: int | str, expected: int) -> None:
    assert f._to_int(value, min_value=0, max_value=20) == expected


@pytest.mark.parametrize("value", [True, 1.5, 21])
def test_to_int_rejects_invalid_values(
    value: object,
    fatal_error: list[tuple[str, str]],
) -> None:
    with pytest.raises(FatalError):
        f._to_int(value, min_value=0, max_value=20)  # type: ignore[arg-type]

    assert fatal_error


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (True, True),
        (False, False),
        (1, True),
        (0, False),
        ("YES", True),
        (" unchecked ", False),
    ],
)
def test_to_bool_accepts_supported_values(
    value: bool | int | str,
    expected: bool,
) -> None:
    assert f._to_bool(value) is expected


@pytest.mark.parametrize("value", [2, "maybe", []])
def test_to_bool_rejects_invalid_values(
    value: object,
    fatal_error: list[tuple[str, str]],
) -> None:
    with pytest.raises(FatalError):
        f._to_bool(value)  # type: ignore[arg-type]

    assert fatal_error


def test_resource_path_keeps_absolute_path() -> None:
    absolute = Path("C:/music/end.mp3")

    assert f.resource_path(absolute) == absolute


def test_resource_path_uses_pyinstaller_directory(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(f.sys, "frozen", True, raising=False)
    monkeypatch.setattr(f.sys, "_MEIPASS", "C:/bundle", raising=False)

    assert f.resource_path("sound.mp3") == Path("C:/bundle/sound.mp3")


def test_check_music_finished_emits_only_after_playback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    emitted: list[bool] = []
    monkeypatch.setattr(
        f,
        "signals",
        SimpleNamespace(
            melody_finished=SimpleNamespace(emit=lambda: emitted.append(True))
        ),
    )
    monkeypatch.setattr(f.pygame.mixer.music, "get_busy", lambda: True)

    f.check_music_finished()
    assert emitted == []

    monkeypatch.setattr(f.pygame.mixer.music, "get_busy", lambda: False)
    f.check_music_finished()
    assert emitted == [True]


def test_beep_internal_error_schedules_three_beeps(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[int, object]] = []
    monkeypatch.setattr(
        f.QTimer,
        "singleShot",
        lambda delay, callback: calls.append((delay, callback)),
    )

    f.beep_internal_error()

    assert [delay for delay, _ in calls] == [
        0,
        f.INTERNAL_ERROR_BEEP_2_DELAY_MS,
        f.INTERNAL_ERROR_BEEP_3_DELAY_MS,
    ]
    assert all(callback == f.QApplication.beep for _, callback in calls)


def test_num_reads_empty_and_filled_line_edits() -> None:
    assert f.num(SimpleNamespace(text=lambda: "")) == 0
    assert f.num(SimpleNamespace(text=lambda: "17")) == 17


def test_cycle_interval_display_helpers() -> None:
    assert f.to_cycle_interval([1, 2, 3]) == "1  2  3"
    assert f.cycle_intervals_to_display([1, 2, 3]) == "1, 2, 3"
    assert f._to_str("value") == "value"
    assert f._to_str([1, 2]) == "[1, 2]"
