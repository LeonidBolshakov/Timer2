from __future__ import annotations

from types import SimpleNamespace

import pytest
from PyQt6.QtCore import Qt

from timer_3 import focus_transition as focus_module
from timer_3.focus_transition import FocusSchema, FocusTransition
from timer_3.time_input_mode import TimeInputMode


class FakeQWidget:
    tab_orders: list[tuple[object, object]] = []

    @staticmethod
    def setTabOrder(current: object, following: object) -> None:
        FakeQWidget.tab_orders.append((current, following))


class Widget(FakeQWidget):
    def __init__(
        self,
        text: str = "",
        policy: Qt.FocusPolicy = Qt.FocusPolicy.StrongFocus,
    ) -> None:
        self._text = text
        self._policy = policy
        self.focused = False

    def setFocusPolicy(self, policy: Qt.FocusPolicy) -> None:
        self._policy = policy

    def focusPolicy(self) -> Qt.FocusPolicy:
        return self._policy

    def setFocus(self) -> None:
        self.focused = True

    def text(self) -> str:
        return self._text


def make_window() -> SimpleNamespace:
    widgets = {
        "lineEdit_HM_H": Widget(),
        "lineEdit_HM_M": Widget(),
        "lineEdit_MS_M": Widget(),
        "lineEdit_MS_S": Widget(),
        "btnStart": Widget(),
        "btnQuit": Widget(),
        "btnTunes": Widget(),
        "lineEditCycleIntervals": Widget(),
        "checkboxEndlessly": Widget(),
        "spinBoxCycleRepetitions": Widget(),
    }
    window = SimpleNamespace(**widgets)
    window.findChildren = lambda _widget_type: list(widgets.values())
    return window


@pytest.fixture
def transition(monkeypatch: pytest.MonkeyPatch) -> FocusTransition:
    FakeQWidget.tab_orders.clear()
    monkeypatch.setattr(focus_module, "QWidget", FakeQWidget)
    return FocusTransition(make_window())


def test_set_focus_sequence_resets_and_assigns_requested_order(
    transition: FocusTransition,
) -> None:
    transition.set_focus_sequence(FocusSchema.ORDINARY_MS)

    assert transition.window.lineEdit_MS_M.focusPolicy() == Qt.FocusPolicy.StrongFocus
    assert transition.window.lineEdit_MS_S.focusPolicy() == Qt.FocusPolicy.StrongFocus
    assert transition.window.btnTunes.focusPolicy() == Qt.FocusPolicy.TabFocus
    assert transition.window.lineEdit_HM_H.focusPolicy() == Qt.FocusPolicy.ClickFocus
    assert FakeQWidget.tab_orders == [
        (transition.window.lineEdit_MS_M, transition.window.lineEdit_MS_S),
        (transition.window.lineEdit_MS_S, transition.window.btnStart),
        (transition.window.btnStart, transition.window.btnQuit),
        (transition.window.btnQuit, transition.window.btnTunes),
    ]


def test_unknown_focus_code_is_rejected(transition: FocusTransition) -> None:
    with pytest.raises(KeyError, match="UNKNOWN"):
        transition._schema_processing(("MS_M", "UNKNOWN"))


@pytest.mark.parametrize(
    ("state", "expected_schema", "focus_target"),
    [
        (None, FocusSchema.ORDINARY_EMPTY, "lineEdit_MS_M"),
        (TimeInputMode.MS, FocusSchema.ORDINARY_MS, "btnStart"),
        (TimeInputMode.HM, FocusSchema.ORDINARY_HM, "btnStart"),
    ],
)
def test_start_focus_for_ordinary_selects_schema_and_widget(
    transition: FocusTransition,
    state: TimeInputMode | None,
    expected_schema: FocusSchema,
    focus_target: str,
) -> None:
    schemas: list[FocusSchema] = []
    transition.set_focus_sequence = schemas.append

    transition.start_focus_for_ordinary(state)

    assert schemas == [expected_schema]
    assert getattr(transition.window, focus_target).focused is True


def test_start_focus_for_ordinary_rejects_unknown_state(
    transition: FocusTransition,
) -> None:
    with pytest.raises(RuntimeError, match="недопустимый параметр"):
        transition.start_focus_for_ordinary(object())  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("text", "focus_target"),
    [
        ("", "lineEditCycleIntervals"),
        ("  ", "lineEditCycleIntervals"),
        ("5 10", "btnStart"),
    ],
)
def test_start_focus_for_cycle_chooses_first_useful_widget(
    transition: FocusTransition,
    text: str,
    focus_target: str,
) -> None:
    schemas: list[FocusSchema] = []
    transition.set_focus_sequence = schemas.append
    transition.window.lineEditCycleIntervals._text = text

    transition.start_focus_for_cycle()

    assert schemas == [FocusSchema.CYCLE]
    assert getattr(transition.window, focus_target).focused is True


def test_reset_tab_focus_preserves_no_focus_widgets(
    transition: FocusTransition,
) -> None:
    transition.window.btnQuit._policy = Qt.FocusPolicy.NoFocus

    transition._reset_tab_focus()

    assert transition.window.btnQuit.focusPolicy() == Qt.FocusPolicy.NoFocus
    assert transition.window.btnStart.focusPolicy() == Qt.FocusPolicy.ClickFocus
