"""Схемы клавиатурного фокуса главного окна."""

from __future__ import annotations

from itertools import pairwise
from typing import TYPE_CHECKING
from enum import Enum, auto
from dataclasses import dataclass

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget

from .time_input_mode import TimeInputMode

if TYPE_CHECKING:
    from .main import Timer_3


class FocusSchema(Enum):
    """Именованные варианты Tab-порядка для режимов таймера."""
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


@dataclass(frozen=True, slots=True)
class FocusTarget:
    """Виджет и требуемая политика фокуса в активной схеме."""
    widget: QWidget
    policy: Qt.FocusPolicy


class FocusTransition:
    """Настраивает Tab-порядок и начальный фокус для текущего режима."""
    def __init__(self, window: Timer_3) -> None:
        self.window = window

        self._focus_targets_by_code: dict[str, FocusTarget] = {
            "HM_H": FocusTarget(
                window.lineEdit_HM_H,
                Qt.FocusPolicy.StrongFocus,
            ),
            "HM_M": FocusTarget(
                window.lineEdit_HM_M,
                Qt.FocusPolicy.StrongFocus,
            ),
            "MS_M": FocusTarget(
                window.lineEdit_MS_M,
                Qt.FocusPolicy.StrongFocus,
            ),
            "MS_S": FocusTarget(
                window.lineEdit_MS_S,
                Qt.FocusPolicy.StrongFocus,
            ),
            "Start": FocusTarget(
                window.btnStart,
                Qt.FocusPolicy.StrongFocus,
            ),
            "Quit": FocusTarget(
                window.btnQuit,
                Qt.FocusPolicy.StrongFocus,
            ),
            "Tunes": FocusTarget(
                window.btnTunes,
                Qt.FocusPolicy.TabFocus,
            ),
            "Intervals": FocusTarget(
                window.lineEditCycleIntervals,
                Qt.FocusPolicy.StrongFocus,
            ),
            "Endlessly": FocusTarget(
                window.checkboxEndlessly,
                Qt.FocusPolicy.StrongFocus,
            ),
            "Repetitions": FocusTarget(
                window.spinBoxCycleRepetitions,
                Qt.FocusPolicy.StrongFocus,
            ),
        }

    def set_focus_sequence(self, schema: FocusSchema) -> None:
        """Активировать одну из предопределённых схем клавиатурного фокуса."""
        self._schema_processing(
            schema=_SCHEMAS[schema],
        )

    def _schema_processing(self, schema: tuple[str, ...]) -> None:
        unknown_codes = set(schema) - self._focus_targets_by_code.keys()

        if unknown_codes:
            raise KeyError(
                "Внутренняя ошибка. В словаре focus_targets_by_code отсутствуют: \n"
                f"{sorted(unknown_codes)}"
            )

        self._reset_tab_focus()

        for code in schema:
            self._focus_targets_by_code[code].widget.setFocusPolicy(
                self._focus_targets_by_code[code].policy
            )

        for current_code, following_code in pairwise(schema):
            current = self._focus_targets_by_code[current_code].widget
            following = self._focus_targets_by_code[following_code].widget

            QWidget.setTabOrder(current, following)

    def start_focus_for_ordinary(self, state: TimeInputMode | None) -> None:
        """Выбрать схему и начальный виджет обычного таймера."""
        match state:
            case None:
                self.set_focus_sequence(FocusSchema.ORDINARY_EMPTY)
                self.window.lineEdit_MS_M.setFocus()
                return

            case TimeInputMode.MS:
                self.set_focus_sequence(FocusSchema.ORDINARY_MS)
                self.window.btnStart.setFocus()
                return

            case TimeInputMode.HM:
                self.set_focus_sequence(FocusSchema.ORDINARY_HM)
                self.window.btnStart.setFocus()
                return

        raise RuntimeError(
            f"Внутренняя ошибка."
            f"class FocusTransition -> start_focus_for_ordinary\n"
            f"недопустимый параметр - {state}"
        )

    def start_focus_for_cycle(self) -> None:
        """Выбрать схему и начальный виджет циклического таймера."""
        self.set_focus_sequence(FocusSchema.CYCLE)
        if self.window.lineEditCycleIntervals.text().strip() == "":
            self.window.lineEditCycleIntervals.setFocus()
        else:
            self.window.btnStart.setFocus()

    def _reset_tab_focus(self) -> None:
        for widget in self.window.findChildren(QWidget):
            if widget.focusPolicy() != Qt.FocusPolicy.NoFocus:
                widget.setFocusPolicy(Qt.FocusPolicy.ClickFocus)


def print_tab_order(start_widget: QWidget) -> None:
    """Напечатать цепочку фокуса для ручной диагностики Qt-интерфейса."""
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
