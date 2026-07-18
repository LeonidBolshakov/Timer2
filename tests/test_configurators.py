from __future__ import annotations

from types import SimpleNamespace

import pytest
from PyQt6.QtCore import Qt

from timer_3 import timer_configurator as timer_config_module
from timer_3 import tunes_configurator as tunes_config_module
from timer_3.param_keys import ParamKeys
from timer_3.timer_configurator import Timer3UiConfigurator
from timer_3.tunes_configurator import TunesConfigurator


class Signal:
    def __init__(self) -> None:
        self.callbacks: list[object] = []

    def connect(self, callback: object) -> None:
        self.callbacks.append(callback)

    def emit(self, *args: object) -> None:
        for callback in self.callbacks:
            callback(*args)  # type: ignore[operator]


class Widget:
    def __init__(self, text: str = "") -> None:
        self._text = text
        self.validator: object | None = None
        self.check_state: Qt.CheckState | None = None
        self.value: int | None = None
        self.clicked = Signal()
        self.textEdited = Signal()
        self.stateChanged = Signal()
        self.valueChanged = Signal()
        self.currentChanged = Signal()
        self.editingFinished = Signal()
        self.accepted = Signal()

    def setValidator(self, validator: object) -> None:
        self.validator = validator

    def setText(self, text: str) -> None:
        self._text = text

    def text(self) -> str:
        return self._text

    def setCheckState(self, state: Qt.CheckState) -> None:
        self.check_state = state

    def setValue(self, value: int) -> None:
        self.value = value

    def setCurrentIndex(self, value: int) -> None:
        self.value = value


class SignalBlocker:
    def __init__(self, _widget: object) -> None:
        pass

    def __enter__(self) -> SignalBlocker:
        return self

    def __exit__(self, *_args: object) -> None:
        pass


class Regex:
    def __init__(self, pattern: str) -> None:
        self.pattern = pattern


class RegexValidator:
    def __init__(self, regex: Regex) -> None:
        self.regex = regex


class IntValidator:
    def __init__(self, minimum: int, maximum: int, parent: object) -> None:
        self.minimum = minimum
        self.maximum = maximum
        self.parent = parent


def make_timer_window() -> SimpleNamespace:
    window = SimpleNamespace(
        btnQuit=Widget(),
        btnStart=Widget(),
        btnTunes=Widget(),
        lineEdit_HM_H=Widget(),
        lineEdit_HM_M=Widget(),
        lineEdit_MS_M=Widget(),
        lineEdit_MS_S=Widget(),
        lineEditCycleIntervals=Widget(),
        checkboxEndlessly=Widget(),
        spinBoxCycleRepetitions=Widget(),
        tabWidgetSetTime=Widget(),
        lblSec=Widget("old"),
    )
    window._style = "base"
    window.styleSheet = lambda: window._style
    window.setStyleSheet = lambda style: setattr(window, "_style", style)
    return window


def make_timer_controller(model: SimpleNamespace) -> SimpleNamespace:
    context = SimpleNamespace(set_calls=[])
    context.model = model
    context.set_value = lambda key, value, save=True: context.set_calls.append(
        (key, value, save)
    )
    controller = SimpleNamespace(
        context=context,
        edited=[],
        focus_tabs=[],
        on_btn_start_click=lambda: None,
        on_btn_tunes_click=lambda: None,
        on_line_edit_cycle_intervals_edited=lambda: None,
        on_endlessly_changed=lambda _state: None,
        on_cycle_repetitions_changed=lambda _value: None,
        on_qtab_widget_changed=lambda _index: None,
    )
    controller.on_line_edit_edited = lambda widget: controller.edited.append(widget)
    controller.init_focus_for_tab = lambda index: controller.focus_tabs.append(index)
    return controller


@pytest.fixture(autouse=True)
def fake_qt_helpers(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(timer_config_module, "QSignalBlocker", SignalBlocker)
    monkeypatch.setattr(timer_config_module, "QRegularExpression", Regex)
    monkeypatch.setattr(
        timer_config_module,
        "QRegularExpressionValidator",
        RegexValidator,
    )
    monkeypatch.setattr(tunes_config_module, "QIntValidator", IntValidator)


def test_timer_configurator_restores_fields_and_connects_signals() -> None:
    model = SimpleNamespace(
        restore_time=True,
        hm_h=1,
        hm_m=2,
        ms_m=3,
        ms_s=4,
        cycle_intervals=[5, 10],
        endlessly=True,
        cycle_repetitions=6,
        active_tab_in_QTabWidget=1,
    )
    window = make_timer_window()
    controller = make_timer_controller(model)

    configurator = Timer3UiConfigurator(window, controller)

    assert configurator.validator_hour.regex.pattern
    assert window.lineEdit_HM_H.validator is configurator.validator_hour
    assert window.lineEdit_MS_S.validator is configurator.validator_min_sec
    assert window.lineEdit_HM_H.text() == "1"
    assert window.lineEdit_HM_M.text() == "2"
    assert window.lineEdit_MS_M.text() == "3"
    assert window.lineEdit_MS_S.text() == "4"
    assert window.lineEditCycleIntervals.text() == "5  10"
    assert window.checkboxEndlessly.check_state == Qt.CheckState.Checked
    assert window.spinBoxCycleRepetitions.value == 6
    assert window.tabWidgetSetTime.value == 1
    assert controller.focus_tabs == [1]
    assert "QPushButton:focus" in window._style

    window.lineEdit_MS_S.textEdited.emit()
    assert controller.edited == [window.lineEdit_MS_S]


def test_timer_configurator_resets_model_when_restore_is_disabled() -> None:
    model = SimpleNamespace(
        restore_time=False,
        hm_h=1,
        hm_m=2,
        ms_m=3,
        ms_s=4,
        cycle_intervals=[5],
        endlessly=True,
        cycle_repetitions=8,
        active_tab_in_QTabWidget=0,
    )
    window = make_timer_window()
    controller = make_timer_controller(model)

    Timer3UiConfigurator(window, controller)

    assert controller.context.set_calls == [
        (ParamKeys.HM_H, 0, False),
        (ParamKeys.HM_M, 0, False),
        (ParamKeys.MS_M, 0, False),
        (ParamKeys.MS_S, 0, False),
        (ParamKeys.CYCLE_INTERVALS, [], False),
        (ParamKeys.CYCLE_ENDLESSLY, False, False),
        (ParamKeys.CYCLE_REPETITIONS, 1, True),
    ]
    assert window.lblSec.text() == ""
    assert controller.focus_tabs == [0]


def test_init_ordinary_fields_leaves_zero_groups_empty() -> None:
    model = SimpleNamespace(hm_h=0, hm_m=0, ms_m=0, ms_s=0)
    window = make_timer_window()
    controller = make_timer_controller(model)
    configurator = Timer3UiConfigurator.__new__(Timer3UiConfigurator)
    configurator.window = window
    configurator.context = controller.context

    configurator.init_ordinary_fields()

    assert window.lineEdit_HM_H.text() == ""
    assert window.lineEdit_MS_M.text() == ""


def test_init_tab_cycle_uses_display_separator() -> None:
    model = SimpleNamespace(
        cycle_intervals=[2, 4],
        endlessly=False,
        cycle_repetitions=3,
    )
    window = make_timer_window()
    configurator = Timer3UiConfigurator.__new__(Timer3UiConfigurator)
    configurator.window = window
    configurator.context = SimpleNamespace(model=model)

    configurator.init_tabCycle()

    assert window.lineEditCycleIntervals.text() == "2, 4"
    assert window.checkboxEndlessly.check_state == Qt.CheckState.Unchecked
    assert window.spinBoxCycleRepetitions.value == 3


def make_tunes_window() -> SimpleNamespace:
    window = SimpleNamespace(
        btnBoxOk=Widget(),
        toolBtnFileTunes=Widget(),
        toolBtnMelody=Widget(),
        checkBoxRestore=Widget(),
        lnEdFileTunes=Widget(),
        lnEdVoiceInterval=Widget(),
        lnEdBeepInterval=Widget(),
        lnEdBeepPeriodInFinal=Widget(),
    )
    window.hidden = False
    window.hide = lambda: setattr(window, "hidden", True)
    return window


def test_tunes_configurator_sets_ranges_validators_and_connections() -> None:
    window = make_tunes_window()
    calls: list[str] = []
    controller = SimpleNamespace(
        refresh_tune_ui=lambda: calls.append("refresh"),
        on_tool_btn_file_tunes=lambda: calls.append("file"),
        on_tool_btn_melody=lambda: calls.append("melody"),
        on_restore_changed=lambda _state: calls.append("restore"),
        on_file_tunes_edited=lambda: calls.append("file-edited"),
        on_voice_interval_edited=lambda: calls.append("voice"),
        on_beep_interval_edited=lambda: calls.append("beep"),
        on_beep_period_in_final_edited=lambda: calls.append("final"),
    )

    configurator = TunesConfigurator(window, controller)

    assert configurator.voice_interval_validator.minimum == 1
    assert configurator.voice_interval_validator.maximum == 120
    assert configurator.beep_interval_validator.minimum == 1
    assert configurator.beep_interval_validator.maximum == 30
    assert configurator.beep_period_in_final_validator.maximum == 20
    assert window.lnEdVoiceInterval.validator is configurator.voice_interval_validator
    assert window.lnEdBeepInterval.validator is configurator.beep_interval_validator
    assert calls == ["refresh"]

    window.btnBoxOk.accepted.emit()
    window.toolBtnFileTunes.clicked.emit()
    window.toolBtnMelody.clicked.emit()
    window.checkBoxRestore.stateChanged.emit(2)
    window.lnEdFileTunes.editingFinished.emit()
    window.lnEdVoiceInterval.editingFinished.emit()
    window.lnEdBeepInterval.editingFinished.emit()
    window.lnEdBeepPeriodInFinal.editingFinished.emit()

    assert window.hidden is True
    assert calls == [
        "refresh",
        "file",
        "melody",
        "restore",
        "file-edited",
        "voice",
        "beep",
        "final",
    ]
