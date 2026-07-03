from __future__ import annotations

from typing import TYPE_CHECKING
from enum import Enum

from PyQt6.QtWidgets import (
    QLineEdit,
    QWidget,
)

from .clock import Clock
from .const import Const as C
from . import functions as f
from .tune_key import TuneKey
from .tunes import TunesWindow
from .inform import InformTime
from .tunes import TunesSettings

if TYPE_CHECKING:
    from .main import Timer_3


class TimeField(Enum):
    """Режим ввода времени."""

    HM = 1
    MS = 2


class Timer3Controller:
    def __init__(self, window: Timer_3) -> None:
        self.window = window
        self.clock: Clock | None = None
        self.tunes_window: TunesWindow | None = None
        self.settings = TunesSettings()
        self.inform_time = InformTime(self.settings)

    def on_btn_start_click(self) -> None:
        seconds_left = self.get_seconds_left()
        if self.clock is not None or seconds_left <= 0:
            f.beep()
            return

        self.clock = Clock(seconds_left, self.settings)
        if self.clock is None:
            f.beep()
            return

        self.clock.connect("draw_time", self.draw_time)
        self.clock.connect("inform_voice", self.inform_time.inform_voice)
        self.clock.connect("inform_done", self.inform_time.inform_done)
        self.clock.start()
        self.window.btnStart.setDisabled(True)
        f.beep()

    def on_btn_tunes_click(self) -> None:
        if self.tunes_window is None:
            self.tunes_window = TunesWindow(self.settings)

        if self.tunes_window is None:
            return

        self.tunes_window.refresh_ui()
        self.tunes_window.show()

    def draw_time(self, seconds_left: int) -> None:
        hour, minutes, sec = f.hour_minutes_sec(seconds_left)

        match self.active_time_field():
            case TimeField.MS:
                self.draw_min_sec(minutes, sec)
            case TimeField.HM:
                self.draw_hour_min(hour, minutes, sec)
            case None:
                pass

    def draw_hour_min(self, hour: int, minutes: int, sec: int) -> None:
        self.window.lineEdit_HM_H.setText(f"{hour:02}")
        self.window.lineEdit_HM_M.setText(f"{minutes:02}")
        self.window.lblSec.setText(f": {sec:02}")

    def draw_min_sec(self, minutes: int, sec: int) -> None:
        self.window.lineEdit_MS_M.setText(f"{minutes:02}")
        self.window.lineEdit_MS_S.setText(f"{sec:02}")

    def get_seconds_left(self) -> int:
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
            print("TimeField.HM")
            return TimeField.HM

        if any(widget is field for field in ms_fields):
            print("TimeField.MS")
            return TimeField.MS

        f.inform_fatal_error_and_quit(
            C.TITLE_INTERNAL_ERROR,
            f"{C.TEXT_ERROR_PARAM}\n{widget.objectName()=}",
        )

        raise RuntimeError(f"Неизвестное поле ввода времени: {widget.objectName()}")

    def _active_time_field(self) -> TimeField | None:
        if self.window.lineEdit_MS_M.text() or self.window.lineEdit_MS_S.text():
            return TimeField.MS
        if self.window.lineEdit_HM_H.text() or self.window.lineEdit_HM_M.text():
            return TimeField.HM
        return None

    def on_line_edit_edited(self, widget: QLineEdit, focus: QWidget) -> None:
        match self.active_time_field(widget):
            case TimeField.HM:
                self.activate_inactivate_widgets(
                    self.window.lineEdit_HM_H,
                    self.window.lineEdit_HM_M,
                    self.window.lineEdit_MS_M,
                    self.window.lineEdit_MS_S,
                )
                self.window.lineEdit_MS_M.setText("")
                self.window.lineEdit_MS_S.setText("")
            case TimeField.MS:
                self.activate_inactivate_widgets(
                    self.window.lineEdit_MS_M,
                    self.window.lineEdit_MS_S,
                    self.window.lineEdit_HM_H,
                    self.window.lineEdit_HM_M,
                )
                self.window.lineEdit_HM_H.setText("")
                self.window.lineEdit_HM_M.setText("")
            case None:
                f.inform_fatal_error_and_quit(
                    C.TITLE_INTERNAL_ERROR,
                    C.TEXT_ERROR_UNKNOWN,
                )

        self.set_tunes_and_finish(widget, focus)

    def set_tunes_and_finish(self, widget: QLineEdit, focus: QWidget) -> None:
        self.put_int_tune(TuneKey.HM_H, self.window.lineEdit_HM_H.text())
        self.put_int_tune(TuneKey.HM_M, self.window.lineEdit_HM_M.text())
        self.put_int_tune(TuneKey.MS_M, self.window.lineEdit_MS_M.text())
        self.put_int_tune(TuneKey.MS_S, self.window.lineEdit_MS_S.text())

        if len(widget.text()) == 2:
            focus.setFocus()

    def put_int_tune(self, key: TuneKey, value: str) -> None:
        self.settings.set_value(key, value if value else 0)

    @staticmethod
    def activate_inactivate_widgets(
        active_1: QLineEdit,
        active_2: QLineEdit,
        inactive_1: QLineEdit,
        inactive_2: QLineEdit,
    ) -> None:
        inactive_1.clear()
        inactive_2.clear()
        inactive_1.setStyleSheet(C.INACTIVE_FIELD_BG_COLOR)
        inactive_2.setStyleSheet(C.INACTIVE_FIELD_BG_COLOR)
        active_1.setStyleSheet(C.ACTIVE_FIELD_BG_COLOR)
        active_2.setStyleSheet(C.ACTIVE_FIELD_BG_COLOR)
