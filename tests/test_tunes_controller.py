from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest
from PyQt6.QtCore import Qt

from timer_3 import tunes_controller as tunes_module
from timer_3.param_keys import ParamKeys
from timer_3.tunes_controller import TunesController


class Field:
    def __init__(self, text: str = "") -> None:
        self._text = text
        self.check_state: Qt.CheckState | None = None

    def text(self) -> str:
        return self._text

    def setText(self, text: str) -> None:
        self._text = text

    def setCheckState(self, state: Qt.CheckState) -> None:
        self.check_state = state


class SignalBlocker:
    def __init__(self, _widget: object) -> None:
        pass

    def __enter__(self) -> SignalBlocker:
        return self

    def __exit__(self, *_args: object) -> None:
        pass


class Settings:
    def __init__(self, tmp_path: Path) -> None:
        self.settings_file = tmp_path / "active.json"
        self.model = SimpleNamespace(
            file_melody="music/end.mp3",
            voice_interval=10,
            beep_interval=3,
            beep_period_in_final=11,
            restore_time=True,
        )
        self.set_calls: list[tuple[ParamKeys, object]] = []
        self.switch_calls: list[Path] = []
        self.storage = SimpleNamespace(pop_warnings=lambda: [])

    def set_value(self, key: ParamKeys, value: object) -> None:
        self.set_calls.append((key, value))

    def switch_settings_file(self, path: Path) -> None:
        self.switch_calls.append(path)


def make_controller(tmp_path: Path) -> TunesController:
    settings = Settings(tmp_path)
    window = SimpleNamespace(
        settings=settings,
        lnEdFileTunes=Field(),
        lnEdFileMelody=Field(),
        lnEdVoiceInterval=Field(),
        lnEdBeepInterval=Field(),
        lnEdBeepPeriodInFinal=Field(),
        checkBoxRestore=Field(),
    )
    return TunesController(window)


@pytest.fixture(autouse=True)
def fake_signal_blocker(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(tunes_module, "QSignalBlocker", SignalBlocker)


def test_refresh_tune_ui_draws_all_model_values(tmp_path: Path) -> None:
    controller = make_controller(tmp_path)

    controller.refresh_tune_ui()

    assert controller.window.lnEdFileTunes.text() == str(tmp_path / "active.json")
    assert controller.window.lnEdFileMelody.text() == "music/end.mp3"
    assert controller.window.lnEdVoiceInterval.text() == "10"
    assert controller.window.lnEdBeepInterval.text() == "3"
    assert controller.window.lnEdBeepPeriodInFinal.text() == "11"
    assert controller.window.checkBoxRestore.check_state == Qt.CheckState.Checked


def test_refresh_tune_ui_draws_unchecked_restore(tmp_path: Path) -> None:
    controller = make_controller(tmp_path)
    controller.settings.model.restore_time = False

    controller.refresh_tune_ui()

    assert controller.window.checkBoxRestore.check_state == Qt.CheckState.Unchecked


@pytest.mark.parametrize(
    ("method_name", "key", "field_name"),
    [
        ("on_voice_interval_edited", ParamKeys.VOICE_INTERVAL, "lnEdVoiceInterval"),
        ("on_beep_interval_edited", ParamKeys.BEEP_INTERVAL, "lnEdBeepInterval"),
        (
            "on_beep_period_in_final_edited",
            ParamKeys.BEEP_PERIOD_IN_FINAL,
            "lnEdBeepPeriodInFinal",
        ),
    ],
)
def test_numeric_handlers_delegate_to_common_setter(
    tmp_path: Path,
    method_name: str,
    key: ParamKeys,
    field_name: str,
) -> None:
    controller = make_controller(tmp_path)
    calls: list[tuple[ParamKeys, object]] = []
    controller._set_int_from_line_edit = lambda arg_key, field: calls.append(
        (arg_key, field)
    )

    getattr(controller, method_name)()

    assert calls == [(key, getattr(controller.window, field_name))]


@pytest.mark.parametrize(
    ("state", "expected"),
    [
        (Qt.CheckState.Checked.value, True),
        (Qt.CheckState.Unchecked.value, False),
    ],
)
def test_restore_handler_updates_setting(
    tmp_path: Path,
    state: int,
    expected: bool,
) -> None:
    controller = make_controller(tmp_path)
    warnings: list[bool] = []
    controller._show_storage_warnings = lambda: warnings.append(True)

    controller.on_restore_changed(state)

    assert controller.settings.set_calls == [(ParamKeys.RESTORE_TIME, expected)]
    assert warnings == [True]


@pytest.mark.parametrize("selected", ["", "C:/music/new.mp3"])
def test_melody_file_selection_handles_cancel_and_success(
    tmp_path: Path,
    selected: str,
) -> None:
    controller = make_controller(tmp_path)
    refreshes: list[bool] = []
    controller._select_file = lambda **_kwargs: selected
    controller._show_storage_warnings = lambda: None
    controller.refresh_tune_ui = lambda: refreshes.append(True)

    controller.on_tool_btn_melody()

    expected_calls = [(ParamKeys.FILE_MELODY, selected)] if selected else []
    assert controller.settings.set_calls == expected_calls
    assert refreshes == ([True] if selected else [])


@pytest.mark.parametrize("selected", ["", "C:/settings/work.json"])
def test_settings_file_dialog_handles_cancel_and_success(
    tmp_path: Path,
    selected: str,
) -> None:
    controller = make_controller(tmp_path)
    switched: list[Path] = []
    controller._select_file = lambda **_kwargs: selected
    controller._switch_settings_file = switched.append

    controller.on_tool_btn_file_tunes()

    assert switched == ([Path(selected)] if selected else [])


def test_empty_edited_settings_path_restores_ui(tmp_path: Path) -> None:
    controller = make_controller(tmp_path)
    controller.window.lnEdFileTunes.setText("  ")
    refreshes: list[bool] = []
    controller.refresh_tune_ui = lambda: refreshes.append(True)

    controller.on_file_tunes_edited()

    assert refreshes == [True]
    assert controller.settings.switch_calls == []


def test_relative_edited_settings_path_is_normalized_and_switched(
    tmp_path: Path,
) -> None:
    controller = make_controller(tmp_path)
    controller.window.lnEdFileTunes.setText("profiles/work")
    switched: list[Path] = []
    controller._switch_settings_file = switched.append

    controller.on_file_tunes_edited()

    assert switched == [(tmp_path / "profiles/work.json").resolve()]


def test_common_numeric_setter_refreshes_after_success(tmp_path: Path) -> None:
    controller = make_controller(tmp_path)
    field = Field("17")
    events: list[str] = []
    controller._show_storage_warnings = lambda: events.append("warnings")
    controller.refresh_tune_ui = lambda: events.append("refresh")

    controller._set_int_from_line_edit(ParamKeys.VOICE_INTERVAL, field)

    assert controller.settings.set_calls == [(ParamKeys.VOICE_INTERVAL, "17")]
    assert events == ["warnings", "refresh"]


def test_common_numeric_setter_warns_and_refreshes_after_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    controller = make_controller(tmp_path)
    controller.settings.set_value = lambda *_args: (_ for _ in ()).throw(
        ValueError("outside range")
    )
    warnings: list[tuple[object, ...]] = []
    monkeypatch.setattr(
        tunes_module,
        "QMessageBox",
        SimpleNamespace(warning=lambda *args: warnings.append(args)),
    )
    events: list[str] = []
    controller._show_storage_warnings = lambda: events.append("storage")
    controller.refresh_tune_ui = lambda: events.append("refresh")

    controller._set_int_from_line_edit(ParamKeys.VOICE_INTERVAL, Field("999"))

    assert "outside range" in str(warnings[0][2])
    assert events == ["storage", "refresh"]


def test_switch_settings_file_refreshes_and_shows_warnings(tmp_path: Path) -> None:
    controller = make_controller(tmp_path)
    events: list[str] = []
    controller._show_storage_warnings = lambda: events.append("warnings")
    controller.refresh_tune_ui = lambda: events.append("refresh")
    path = tmp_path / "new.json"

    controller._switch_settings_file(path)

    assert controller.settings.switch_calls == [path]
    assert events == ["warnings", "refresh"]


@pytest.mark.parametrize(
    ("text", "expected_name"),
    [("profile", "profile.json"), ("profile.JSON", "profile.JSON")],
)
def test_normalize_json_path_adds_only_missing_suffix(
    tmp_path: Path,
    text: str,
    expected_name: str,
) -> None:
    controller = make_controller(tmp_path)

    result = controller._normalize_json_path(text)

    assert result == (tmp_path / expected_name).resolve()


def test_select_file_uses_parent_of_current_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    controller = make_controller(tmp_path)
    calls: list[tuple[object, ...]] = []

    def get_open_file_name(*args: object) -> tuple[str, str]:
        calls.append(args)
        return "selected.json", ""

    monkeypatch.setattr(
        tunes_module,
        "QFileDialog",
        SimpleNamespace(getOpenFileName=get_open_file_name),
    )

    result = controller._select_file(
        str(tmp_path / "current.json"),
        "title",
        "*.json",
    )

    assert result == "selected.json"
    assert calls[0][2] == str(tmp_path)


@pytest.mark.parametrize("warnings", [[], ["first", "second"]])
def test_show_storage_warnings(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    warnings: list[str],
) -> None:
    controller = make_controller(tmp_path)
    controller.settings.storage.pop_warnings = lambda: warnings
    calls: list[tuple[object, ...]] = []
    monkeypatch.setattr(
        tunes_module,
        "QMessageBox",
        SimpleNamespace(warning=lambda *args: calls.append(args)),
    )

    controller._show_storage_warnings()

    assert len(calls) == (1 if warnings else 0)
    if warnings:
        assert calls[0][2] == "first\n\nsecond"
