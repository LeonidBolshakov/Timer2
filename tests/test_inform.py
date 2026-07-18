from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from timer_3 import inform as inform_module
from timer_3.inform import InformTime


class FatalError(RuntimeError):
    pass


class TimerFinished(RuntimeError):
    pass


def make_inform(file_melody: str = "sound.mp3") -> InformTime:
    settings = SimpleNamespace(model=SimpleNamespace(file_melody=file_melody))
    return InformTime(settings)


def test_end_of_ordinary_timer_requires_melody(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    inform = make_inform("")
    calls: list[tuple[str, str]] = []

    def fatal(title: str, text: str) -> None:
        calls.append((title, text))
        raise FatalError

    monkeypatch.setattr(inform_module.f, "inform_fatal_error_and_quit", fatal)

    with pytest.raises(FatalError):
        inform.end_of_ordynary_timer()

    assert calls
    assert "мелод" in calls[0][1].lower()


def test_end_of_ordinary_timer_plays_melody_then_quits(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    inform = make_inform()
    calls: list[object] = []
    music = SimpleNamespace(
        load=lambda path: calls.append(("load", path)),
        play=lambda: calls.append("play"),
    )
    monkeypatch.setattr(inform_module.pygame, "init", lambda: calls.append("init"))
    monkeypatch.setattr(
        inform_module.pygame,
        "mixer",
        SimpleNamespace(init=lambda: calls.append("mixer.init"), music=music),
    )
    monkeypatch.setattr(
        inform_module.f,
        "resource_path",
        lambda path: Path("C:/bundle") / path,
    )
    monkeypatch.setattr(
        InformTime,
        "control_end_of_melody",
        staticmethod(lambda: calls.append("control")),
    )
    monkeypatch.setattr(
        inform_module.f,
        "go_quit",
        lambda: (_ for _ in ()).throw(TimerFinished()),
    )

    with pytest.raises(TimerFinished):
        inform.end_of_ordynary_timer()

    assert calls == [
        "init",
        "mixer.init",
        ("load", Path("C:/bundle/sound.mp3")),
        "play",
        "control",
    ]


def test_playback_error_is_reported_as_fatal(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    inform = make_inform()
    fatal_calls: list[tuple[str, str]] = []
    monkeypatch.setattr(inform_module.f, "resource_path", lambda path: Path(path))
    monkeypatch.setattr(
        inform_module.pygame,
        "init",
        lambda: (_ for _ in ()).throw(RuntimeError("audio unavailable")),
    )

    def fatal(title: str, text: str) -> None:
        fatal_calls.append((title, text))
        raise FatalError

    monkeypatch.setattr(inform_module.f, "inform_fatal_error_and_quit", fatal)

    with pytest.raises(FatalError):
        inform.end_of_ordynary_timer()

    assert "audio unavailable" in fatal_calls[0][1]


def test_voice_once_speaks_and_releases_lock(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    inform = make_inform()
    calls: list[object] = []
    engine = SimpleNamespace(
        say=lambda text: calls.append(("say", text)),
        runAndWait=lambda: calls.append("run"),
        stop=lambda: calls.append("stop"),
    )
    monkeypatch.setattr(inform_module.f, "time_to_text", lambda seconds: f"{seconds}s")
    monkeypatch.setattr(inform_module.pyttsx3, "init", lambda: engine)

    inform._voice_once(12)

    assert calls == [("say", "12s"), "run", "stop"]
    assert inform.voice_lock.acquire(blocking=False) is True
    inform.voice_lock.release()


def test_voice_once_skips_when_previous_message_is_active(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    inform = make_inform()
    inform.voice_lock.acquire()
    monkeypatch.setattr(
        inform_module.pyttsx3,
        "init",
        lambda: pytest.fail("engine must not be created"),
    )

    inform._voice_once(5)

    assert inform.voice_lock.locked() is True
    inform.voice_lock.release()
