from __future__ import annotations

from itertools import pairwise
from typing import TYPE_CHECKING
from enum import Enum, auto

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget

if TYPE_CHECKING:
    from .main import Timer_3


class FocusSchema(Enum):
    ORDINARY_EMPTY = auto()
    ORDINARY_HM = auto()
    ORDINARY_MS = auto()
    CYCLE = auto()


_SCHEMAS: dict[FocusSchema, tuple[str, ...]] = {
    FocusSchema.ORDINARY_EMPTY: (
        "HM_H",
        "HM_M",
        "MS_M",
        "MS_S",
    ),
    FocusSchema.ORDINARY_HM: (
        "HM_H",
        "HM_M",
        "Start",
        "Quit",
        "Tunes",
    ),
    FocusSchema.ORDINARY_MS: (
        "MS_M",
        "MS_S",
        "Start",
        "Quit",
        "Tunes",
    ),
    FocusSchema.CYCLE: (
        "Intervals",
        "Endlessly",
        "Repetitions",
        "Start",
        "Quit",
        "Tunes",
    ),
}


class FocusTransition:
    def __init__(self, window: Timer_3) -> None:
        self.window = window

        self._widgets_by_code: dict[str, QWidget] = {
            "HM_H": window.lineEdit_HM_H,
            "HM_M": window.lineEdit_HM_M,
            "MS_M": window.lineEdit_MS_M,
            "MS_S": window.lineEdit_MS_S,
            "Start": window.btnStart,
            "Quit": window.btnQuit,
            "Tunes": window.btnTunes,
            "Intervals": window.lineEditCycleIntervals,
            "Endlessly": window.checkboxEndlessly,
            "Repetitions": window.spinBoxCycleRepetitions,
        }

    def set_focus_sequence(self, schema: FocusSchema) -> None:
        self._schema_processing(
            schema=_SCHEMAS[schema],
        )

    def _schema_processing(self, schema: tuple[str, ...]) -> None:
        unknown_codes = set(schema) - self._widgets_by_code.keys()
        for cod in self._widgets_by_code:
            if cod not in schema:
                self._widgets_by_code[cod].setFocusPolicy(Qt.FocusPolicy.ClickFocus)

        if unknown_codes:
            raise KeyError(
                "Внутренняя ошибка. В словаре widgets_by_code отсутствуют: "
                f"{sorted(unknown_codes)}"
            )

        for widget in self._widgets_by_code.values():
            widget.setFocusPolicy(Qt.FocusPolicy.ClickFocus)

        for cod in schema:
            self._widgets_by_code[cod].setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        for current, following in pairwise(schema):
            QWidget.setTabOrder(
                self._widgets_by_code[current],
                self._widgets_by_code[following],
            )

    def start_focus_for_ordinary(
        self,
        time_fields_are_empty: bool,
    ) -> None:
        if time_fields_are_empty:
            self.set_focus_sequence(FocusSchema.ORDINARY_EMPTY)
            self.window.lineEdit_MS_M.setFocus()
        else:
            self.set_focus_sequence(FocusSchema.ORDINARY_MS)
            self.window.btnStart.setFocus()

    def start_focus_for_cycle(self) -> None:
        self.set_focus_sequence(FocusSchema.CYCLE)
        if self.window.lineEditCycleIntervals.text().strip() == "":
            self.window.lineEditCycleIntervals.setFocus()
        else:
            self.window.btnStart.setFocus()

    def set_mouse_only_focus(self) -> None:
        for widget in self.window.findChildren(QWidget):
            if widget.focusPolicy() != Qt.FocusPolicy.NoFocus:
                widget.setFocusPolicy(Qt.FocusPolicy.ClickFocus)


def print_tab_order(start_widget: QWidget) -> None:
    current = start_widget
    visited: set[int] = set()
    number = 1

    print(
        f"{'№':>3}  "
        f"{'objectName':<32} "
        f"{'class':<20} "
        f"{'focusPolicy':<15} "
        f"{'enabled':<8} "
        f"{'visible':<8}"
    )

    while id(current) not in visited:
        visited.add(id(current))

        focus_policy = current.focusPolicy()

        if focus_policy != Qt.FocusPolicy.NoFocus:
            print(
                f"{number:>3}  "
                f"{current.objectName() or '<без имени>':<32} "
                f"{type(current).__name__:<20} "
                f"{focus_policy.name:<15} "
                f"{str(current.isEnabled()):<8} "
                f"{str(current.isVisible()):<8}"
            )
            number += 1

        next_in_focus = current.nextInFocusChain()
        if next_in_focus is None:
            raise RuntimeError("Отсутствует ссылка на следующий фокус")
        current = next_in_focus
