from __future__ import annotations

from collections.abc import Iterator, Callable
from typing import TYPE_CHECKING
from enum import Enum

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QLineEdit,
)

from .clock import Clock
from .const import Const as C
from . import functions as f
from .param_keys import ParamKeys
from .tunes import TunesWindow
from .inform import InformTime
from .tunes import Context
from .focus_transition import FocusTransition, FocusSchema

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
        self._current_interval_index = 0
        self._cycle_intervals_iter: Iterator[int] = iter([])
        self._seconds_interval = 0
        self._repetitions_count = 0
        self.focus_transition = FocusTransition(self.window)
        self._tunes_window: TunesWindow | None = None
        self.context = Context()
        self._clock = Clock()
        self.inform_time = InformTime(self.context)

    def on_btn_start_click(self) -> None:
        active_tab_in_QTabWidget = self.context.model.active_tab_in_QTabWidget

        if active_tab_in_QTabWidget == 0:
            self._prepare_start_tab_ordinary()

        if active_tab_in_QTabWidget == 1:
            self._prepare_start_tab_interval()

        self.window.btnStart.setDisabled(True)
        f.beep()
        self._clock.start()

    def on_btn_tunes_click(self) -> None:
        if self._tunes_window is None:
            self._tunes_window = TunesWindow(self.context)

        if self._tunes_window is None:
            return

        self._tunes_window.refresh_ui()
        self._tunes_window.show_ui()

    def on_line_edit_edited(self, widget: QLineEdit) -> None:
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
                self.focus_transition.set_focus_sequence(FocusSchema.ORDINARY_HM)
            case TimeField.MS:
                self._activate_widgets(
                    self.window.lineEdit_MS_M,
                    self.window.lineEdit_MS_S,
                )
                self._inaktivate_widgets(
                    self.window.lineEdit_HM_H,
                    self.window.lineEdit_HM_M,
                )
                self.focus_transition.set_focus_sequence(FocusSchema.ORDINARY_MS)
            case None:
                f.inform_fatal_error_and_quit(
                    C.TITLE_INTERNAL_ERROR,
                    C.TEXT_ERROR_UNKNOWN,
                )
        self._commit_time_state_and_advance_focus(widget)

    def on_lineEditCycleIntervals_edited(self) -> None:
        text = self.window.lineEditCycleIntervals.text()
        intervals = f.cycle_intervals_list(text)

        if not intervals:
            f.beep()
            self.window.lineEditCycleIntervals.undo()
            return

        self.context.set_value(ParamKeys.CYCLE_INTERVALS, intervals)

    def on_endlessly_changed(self, state: int) -> None:
        self.context.set_value(
            ParamKeys.CYCLE_ENDLESSLY,
            state == Qt.CheckState.Checked.value,
        )
        if state == Qt.CheckState.Checked.value:
            self.window.spinBoxCycleRepetitions.setDisabled(True)
        if state == Qt.CheckState.Unchecked.value:
            self.window.spinBoxCycleRepetitions.setDisabled(False)

    def on_cycle_Repetitions_changed(self, value: int) -> None:
        self.context.set_value(ParamKeys.CYCLE_Repetitions, value)

    def on_QTabWidget_changed(self, index: int) -> None:
        self.init_focus_for_tab(index)
        self.context.set_value(ParamKeys.ACTIVE_TAB_IN_QTABWIDGET, index)

    # -----------------
    # ----- Работа с полями времени в окне "Timer" (Обычный таймер)
    # ------------------

    def for_ordinary_a_second_passed(self, seconds_left: int) -> None:
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

        if widget in hm_fields:
            return TimeField.HM

        if widget in ms_fields:
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

    def _commit_time_state_and_advance_focus(self, widget: QLineEdit) -> None:
        self._put_state(ParamKeys.HM_H, self.window.lineEdit_HM_H.text())
        self._put_state(ParamKeys.HM_M, self.window.lineEdit_HM_M.text())
        self._put_state(ParamKeys.MS_M, self.window.lineEdit_MS_M.text())
        self._put_state(ParamKeys.MS_S, self.window.lineEdit_MS_S.text())

        if len(widget.text()) == 2:
            self.window.focusNextChild()

    def _put_state(self, key: ParamKeys, value: str) -> None:
        self.context.set_value(key, value if value else 0)

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

    def _prepare_start_tab_ordinary(self) -> None:
        seconds_left = self._get_seconds_left()
        self.prepare_timer(
            seconds_left,
            self.for_ordinary_a_second_passed,
            self.inform_time.end_of_timer,
        )

    def check_inform_voice_and_final_beep(self) -> None:
        if self._clock.seconds_left % self.context.model.voice_interval == 0:
            self.inform_time.inform_voice(self._clock.seconds_left)

        if (
            self._clock.seconds_left < self.context.model.beep_period_in_final
            and self._clock.seconds_left % self.context.model.beep_interval == 0
        ):
            f.beep()

    # -----------------
    # ----- Helpers (Интервальный таймер)
    # ------------------

    def _prepare_start_tab_interval(self) -> None:
        intervals = self.context.model.cycle_intervals

        self._cycle_intervals_iter = iter(intervals)
        try:
            self._seconds_interval = next(self._cycle_intervals_iter)
        except StopIteration:
            self._seconds_interval = 0
        if self.context.model.endlessly:
            self._processing_endlessly_cycle()
        else:
            self._processing_repetitions_cycle()

        self._show_current_cycle_interval()

    def _processing_endlessly_cycle(self) -> None:
        self.prepare_timer(
            self._seconds_interval, self.cycle_second_signal, self.cycle_end_interval
        )
        self.init_left_field()

    def cycle_end_interval(self) -> None:
        self._current_interval_index += 1
        try:
            self._seconds_interval = next(self._cycle_intervals_iter)
            self._clock.restart(self._seconds_interval)
        except StopIteration:
            if not self.context.model.endlessly:
                if self._repetitions_count < 0:
                    f.go_quit()

                self._repetitions_count -= 1

            self.clock_restart()
            self.init_left_field()

        f.beep()
        self._show_current_cycle_interval()
        self.init_left_field()

    def cycle_second_signal(self, seconds_left: int) -> None:
        self.window.lineEditLeft.setText(str(seconds_left))

    def prepare_timer(
        self,
        seconds_interval: int,
        a_second_passed: Callable[[int], None],
        end_of_timer: Callable[[], None],
    ) -> None:
        self._clock.seconds_left = seconds_interval
        self._clock.connect("a_second_passed", a_second_passed)
        self._clock.connect("end_of_timer", end_of_timer)

    def _show_current_cycle_interval(self) -> None:
        self.window.lineEditCurrentInterval.setText(
            str(self._current_interval_index + 1)
        )
        self.window.lineEditIntervalDuration.setText(str(self._seconds_interval))

    def _processing_repetitions_cycle(self) -> None:
        self.prepare_timer(
            self._seconds_interval,
            self.cycle_second_signal,
            self.cycle_end_interval,
        )
        self.init_left_field()

    def clock_restart(self) -> None:
        self._current_interval_index = 0
        self._cycle_intervals_iter = iter(self.context.model.cycle_intervals)
        try:
            self._seconds_interval = next(self._cycle_intervals_iter)
        except StopIteration:
            self._seconds_interval = 0
        self._clock.restart(self._seconds_interval)

    def init_focus_for_tab(self, tab_index: int) -> None:
        self.window.tabWidgetSetTime.setCurrentIndex(tab_index)

        if tab_index == 0:
            self.focus_transition.start_focus_for_ordinary(
                self.context.model.ordinary_time_is_empty
            )
            return

        if tab_index == 1:
            self.focus_transition.start_focus_for_cycle()
            return

        raise RuntimeError(C.TITLE_INTERNAL_ERROR)

    def init_left_field(self) -> None:
        self.window.lineEditLeft.setText(str(self._seconds_interval))
