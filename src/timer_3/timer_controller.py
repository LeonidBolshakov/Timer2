from __future__ import annotations

from typing import TYPE_CHECKING
from enum import Enum

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QLineEdit,
    QWidget,
)

from .clock import Clock
from .const import Const as C
from . import functions as f
from .param_keys import ParamKeys
from .tunes import TunesWindow
from .inform import InformTime
from .tunes import TunesSettings

if TYPE_CHECKING:
    from .main import Timer_3


class TimeField(Enum):
    """Режим ввода времени."""

    HM = 1
    MS = 2


# -----------------
# ----- Обработчики событий виджетов окна "Timer"
# ------------------


class Timer3Controller:
    def __init__(self, window: Timer_3) -> None:
        self.window = window
        self.active_tab_in_QTabWidget = 0
        self.tunes_window: TunesWindow | None = None
        self.settings = TunesSettings()
        self.clock = Clock(1, self.settings)
        cycle_intervals = self.settings.model.cycle_intervals
        self.text_cycleintervals_old = f.cycle_intervals_to_display(cycle_intervals)
        self.inform_time = InformTime(self.settings)

    def on_btn_start_click(self) -> None:
        active_tab_in_QTabWidget = self.settings.model.active_tab_in_QTabWidget
        seconds_left = self._get_seconds_left()

        clock = Clock(seconds_left, self.settings)
        if clock is None:
            f.beep_internal_error()
        self.clock = clock

        if active_tab_in_QTabWidget == 0:
            self._start_tab_ordinary()
            return

        if active_tab_in_QTabWidget == 1:
            self._start_tab_interval()
            return

        f.beep_internal_error()

    def on_btn_tunes_click(self) -> None:
        if self.tunes_window is None:
            self.tunes_window = TunesWindow(self.settings)

        if self.tunes_window is None:
            return

        self.tunes_window.refresh_ui()
        self.tunes_window.show_ui()

    def on_line_edit_edited(self, widget: QLineEdit, focus: QWidget) -> None:
        match self.active_time_field(widget):
            case TimeField.HM:
                self._activate_widgets(
                    self.window.lineEdit_HM_H,
                    self.window.lineEdit_HM_M,
                )
                self._inaktivate_widgets(
                    self.window.lineEdit_MS_M,
                    self.window.lineEdit_MS_S,
                )
            case TimeField.MS:
                self._activate_widgets(
                    self.window.lineEdit_MS_M,
                    self.window.lineEdit_MS_S,
                )
                self._inaktivate_widgets(
                    self.window.lineEdit_HM_H,
                    self.window.lineEdit_HM_M,
                )
            case None:
                f.inform_fatal_error_and_quit(
                    C.TITLE_INTERNAL_ERROR,
                    C.TEXT_ERROR_UNKNOWN,
                )

        self._commit_time_state_and_advance_focus(widget, focus)

    def on_lineEditCycleIntervals_edited(self) -> None:
        text = self.window.lineEditCycleIntervals.text()
        intervals = f.cycle_intervals_list(text)

        if not intervals:
            f.beep()
            self.window.lineEditCycleIntervals.setText(self.text_cycleintervals_old)
            return

        self.settings.set_value(ParamKeys.CYCLE_INTERVALS, intervals)
        self.text_cycleintervals_old = text

    def on_endlessly_changed(self, state: int) -> None:
        self.settings.set_value(
            ParamKeys.CYCLE_ENDLESSLY,
            state == Qt.CheckState.Checked.value,
        )

    def on_cycle_repetitions_changed(self, value: int) -> None:
        self.settings.set_value(ParamKeys.CYCLE_REPETITIONS, value)

    def on_QTabWidget_changed(self, index: int) -> None:
        self.settings.set_value(ParamKeys.ACTIVE_TAB_IN_QTABWIDGET, index)

    # -----------------
    # ----- Работа с полями времени в окне "Timer" (Обычный таймер)
    # ------------------

    def a_second_passed(self, seconds_left: int) -> None:
        self.check_inform_voice_and_final_beep()

        hour, minutes, sec = f.hour_minutes_sec(seconds_left)

        match self.active_time_field():
            case TimeField.MS:
                self._draw_min_sec(minutes, sec)
            case TimeField.HM:
                self._draw_hour_min(hour, minutes, sec)
            case None:
                pass

    def active_time_field(self, widget: QLineEdit | None = None) -> TimeField | None:
        if widget is None:
            return self._active_time_field()

        hm_fields = (
            self.window.lineEdit_HM_H,
            self.window.lineEdit_HM_M,
        )

        ms_fields = (
            self.window.lineEdit_MS_M,
            self.window.lineEdit_MS_S,
        )

        if any(widget is field for field in hm_fields):
            return TimeField.HM

        if any(widget is field for field in ms_fields):
            return TimeField.MS

        f.inform_fatal_error_and_quit(
            C.TITLE_INTERNAL_ERROR,
            f"{C.TEXT_ERROR_PARAM}\n{widget.objectName()=}",
        )

    # -----------------
    # ----- Helpers (Обычный таймер)
    # ------------------

    def _draw_hour_min(self, hour: int, minutes: int, sec: int) -> None:
        self.window.lineEdit_HM_H.setText(f"{hour:02}")
        self.window.lineEdit_HM_M.setText(f"{minutes:02}")
        self.window.lblSec.setText(f": {sec:02}")

    def _draw_min_sec(self, minutes: int, sec: int) -> None:
        self.window.lineEdit_MS_M.setText(f"{minutes:02}")
        self.window.lineEdit_MS_S.setText(f"{sec:02}")

    def _active_time_field(self) -> TimeField | None:
        if self.window.lineEdit_MS_M.text() or self.window.lineEdit_MS_S.text():
            return TimeField.MS
        if self.window.lineEdit_HM_H.text() or self.window.lineEdit_HM_M.text():
            return TimeField.HM
        return None

    def _commit_time_state_and_advance_focus(
        self, widget: QLineEdit, next_focus: QWidget
    ) -> None:
        self._put_int_state(ParamKeys.HM_H, self.window.lineEdit_HM_H.text())
        self._put_int_state(ParamKeys.HM_M, self.window.lineEdit_HM_M.text())
        self._put_int_state(ParamKeys.MS_M, self.window.lineEdit_MS_M.text())
        self._put_int_state(ParamKeys.MS_S, self.window.lineEdit_MS_S.text())

        if len(widget.text()) == 2:
            next_focus.setFocus()

    def _put_int_state(self, key: ParamKeys, value: str) -> None:
        self.settings.set_value(key, value if value else 0)

    @staticmethod
    def _activate_widgets(
        active_1: QLineEdit,
        active_2: QLineEdit,
    ) -> None:
        active_1.setStyleSheet(C.ACTIVE_FIELD_BG_COLOR)
        active_2.setStyleSheet(C.ACTIVE_FIELD_BG_COLOR)

    @staticmethod
    def _inaktivate_widgets(
        inactive_1: QLineEdit,
        inactive_2: QLineEdit,
    ) -> None:
        inactive_1.clear()
        inactive_2.clear()
        inactive_1.setStyleSheet(C.INACTIVE_FIELD_BG_COLOR)
        inactive_2.setStyleSheet(C.INACTIVE_FIELD_BG_COLOR)

    def _get_seconds_left(self) -> int:
        match self.active_time_field():
            case TimeField.MS:
                return f.num(self.window.lineEdit_MS_M) * C.SECONDS_IN_MINUTE + f.num(
                    self.window.lineEdit_MS_S
                )
            case TimeField.HM:
                return (
                    f.num(self.window.lineEdit_HM_H) * C.SECONDS_IN_HOUR
                    + f.num(self.window.lineEdit_HM_M) * C.SECONDS_IN_MINUTE
                )
            case None:
                return 0

    def _start_tab_ordinary(self) -> None:
        self.clock.connect("a_second_passed", self.a_second_passed)
        self.clock.connect("end_of_timer", self.inform_time.end_of_timer)
        self.clock.start()
        self.window.btnStart.setDisabled(True)
        f.beep()

    def check_inform_voice_and_final_beep(self) -> None:
        if self.clock.seconds_left % self.settings.model.voice_interval == 0:
            self.inform_time.inform_voice(self.clock.seconds_left)

        if (
            self.clock.seconds_left < self.settings.model.beep_period_in_final
            and self.clock.seconds_left % self.settings.model.beep_interval == 0
        ):
            f.beep()

    # -----------------
    # ----- Helpers (Иетервальный таймер)
    # ------------------

    def _start_tab_interval(self) -> None:
        pass
