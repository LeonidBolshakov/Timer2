import io
import sys
from enum import Enum
from contextlib import suppress

sys.stdout = io.StringIO()
import pygame  # type: ignore

sys.stdout = sys.__stdout__

from PyQt6 import uic  # type: ignore
from PyQt6.QtCore import QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator
from PyQt6.QtWidgets import (
    QApplication,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QWidget,
)

from .clock import Clock
from .const import Const as C
from . import functions as f
from .inform import InformTime
from .tune_key import TuneKey
from .tunes import TunesSettings, TunesWindow


class TimeField(Enum):
    """Режим ввода времени."""

    HM = 1
    MS = 2


class Timer_3(QMainWindow):
    """Главное окно приложения."""

    btnQuit: QPushButton
    btnStart: QPushButton
    btnTunes: QPushButton
    lblSec: QLabel
    lineEdit_HM_H: QLineEdit
    lineEdit_HM_M: QLineEdit
    lineEdit_MS_M: QLineEdit
    lineEdit_MS_S: QLineEdit

    def __init__(self) -> None:
        super().__init__(None)
        uic.loadUi(str(f.resource_path(C.TIMER_3_UI)), self)

        self.settings = TunesSettings()
        self.clock: Clock | None = None
        self.inform_time = InformTime(self.settings)
        self.tunes_window: TunesWindow | None = None

        self.validator_hour = QRegularExpressionValidator()
        self.validator_min_sec = QRegularExpressionValidator()

        self.set_validators()
        self.connect_signals()
        self.set_bolds()
        self.init_vars()

    def set_validators(self) -> None:
        self.validator_hour = QRegularExpressionValidator(
            QRegularExpression(C.RE_PATTERN_0_24)
        )
        self.validator_min_sec = QRegularExpressionValidator(
            QRegularExpression(C.RE_PATTERN_0_60)
        )

        self.lineEdit_HM_H.setValidator(self.validator_hour)
        self.lineEdit_HM_M.setValidator(self.validator_min_sec)
        self.lineEdit_MS_M.setValidator(self.validator_min_sec)
        self.lineEdit_MS_S.setValidator(self.validator_min_sec)

    def connect_signals(self) -> None:
        self.btnQuit.clicked.connect(f.go_quit)
        self.btnStart.clicked.connect(self.on_btn_start_click)
        self.btnTunes.clicked.connect(self.on_btn_tunes_click)

        self.lineEdit_HM_H.textEdited.connect(
            lambda: self.on_line_edit_edited(self.lineEdit_HM_H, self.lineEdit_HM_M)
        )
        self.lineEdit_HM_M.textEdited.connect(
            lambda: self.on_line_edit_edited(self.lineEdit_HM_M, self.btnStart)
        )
        self.lineEdit_MS_M.textEdited.connect(
            lambda: self.on_line_edit_edited(self.lineEdit_MS_M, self.lineEdit_MS_S)
        )
        self.lineEdit_MS_S.textEdited.connect(
            lambda: self.on_line_edit_edited(self.lineEdit_MS_S, self.btnStart)
        )

    def set_bolds(self) -> None:
        return
        for line_edit in (
            self.lineEdit_HM_H,
            self.lineEdit_HM_M,
            self.lineEdit_MS_M,
            self.lineEdit_MS_S,
        ):
            font = line_edit.font()
            font.setBold(True)
            line_edit.setFont(font)

    def init_vars(self) -> None:
        self.lblSec.setText("")
        if self.settings.model.restore_time:
            self.initialize_time_fields()

    def initialize_time_fields(self) -> None:
        model = self.settings.model

        if model.hm_h != 0 or model.hm_m != 0:
            self.lineEdit_HM_H.setText(str(model.hm_h))
            self.lineEdit_HM_M.setText(str(model.hm_m))

        if model.ms_m != 0 or model.ms_s != 0:
            self.lineEdit_MS_M.setText(str(model.ms_m))
            self.lineEdit_MS_S.setText(str(model.ms_s))

    def on_btn_start_click(self) -> None:
        seconds_left = self.get_seconds_left()
        if self.clock is not None or seconds_left <= 0:
            return

        self.clock = Clock(seconds_left, self.settings)
        if self.clock is None:
            return

        self.clock.connect("draw_time", self.draw_time)
        self.clock.connect("inform_voice", self.inform_time.inform_voice)
        self.clock.connect("inform_done", self.inform_time.inform_done)
        self.clock.start()
        self.btnStart.setDisabled(True)
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
        self.lineEdit_HM_H.setText(f"{hour:02}")
        self.lineEdit_HM_M.setText(f"{minutes:02}")
        self.lblSec.setText(f": {sec:02}")

    def draw_min_sec(self, minutes: int, sec: int) -> None:
        self.lineEdit_MS_M.setText(f"{minutes:02}")
        self.lineEdit_MS_S.setText(f"{sec:02}")

    def get_seconds_left(self) -> int:
        match self.active_time_field():
            case TimeField.MS:
                return f.num(self.lineEdit_MS_M) * C.SECONDS_IN_MINUTE + f.num(
                    self.lineEdit_MS_S
                )
            case TimeField.HM:
                return (
                    f.num(self.lineEdit_HM_H) * C.SECONDS_IN_HOUR
                    + f.num(self.lineEdit_HM_M) * C.SECONDS_IN_MINUTE
                )
            case None:
                return 0

    def active_time_field(self, widget: QLineEdit|None = None) -> TimeField | None:
        match widget:
            case None:
                return self._active_time_field()
            case self.lineEdit_HM_H | self.lineEdit_HM_M:
                return TimeField.HM
            case self.lineEdit_MS_M | self.lineEdit_MS_S:
                return TimeField.MS
            case _:
                f.inform_fatal_error_and_quit(
                    C.TITLE_INTERNAL_ERROR,
                    f"{C.TEXT_ERROR_PARAM}\n{widget.objectName()=}",
                )

    def _active_time_field(self) -> TimeField | None:
        if self.lineEdit_MS_M.text() or self.lineEdit_MS_S.text():
            return TimeField.MS
        if self.lineEdit_HM_H.text() or self.lineEdit_HM_M.text():
            return TimeField.HM
        return None

    def on_line_edit_edited(self, widget: QLineEdit, focus: QWidget) -> None:
        match self.active_time_field(widget):
            case TimeField.HM:
                self.activate_inactivate_widgets(
                    self.lineEdit_HM_H,
                    self.lineEdit_HM_M,
                    self.lineEdit_MS_M,
                    self.lineEdit_MS_S,
                )
                self.lineEdit_MS_M.setText("")
                self.lineEdit_MS_S.setText("")
            case TimeField.MS:
                self.activate_inactivate_widgets(
                    self.lineEdit_MS_M,
                    self.lineEdit_MS_S,
                    self.lineEdit_HM_H,
                    self.lineEdit_HM_M,
                )
                self.lineEdit_HM_H.setText("")
                self.lineEdit_HM_M.setText("")
            case None:
                f.inform_fatal_error_and_quit(
                    C.TITLE_INTERNAL_ERROR,
                    C.TEXT_ERROR_UNKNOWN,
                )

        self.set_tunes_and_finish(widget, focus)

    def set_tunes_and_finish(self, widget: QLineEdit, focus: QWidget) -> None:
        self.put_int_tune(TuneKey.HM_H, self.lineEdit_HM_H.text())
        self.put_int_tune(TuneKey.HM_M, self.lineEdit_HM_M.text())
        self.put_int_tune(TuneKey.MS_M, self.lineEdit_MS_M.text())
        self.put_int_tune(TuneKey.MS_S, self.lineEdit_MS_S.text())

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

    def start(self) -> int:
        self.show()
        # noinspection PyArgumentList
        return QApplication.exec()


def main() -> None:
    def on_app_exit() -> None:
        with suppress(pygame.error):
            pygame.mixer.quit()

    app = QApplication(sys.argv)
    app.aboutToQuit.connect(on_app_exit)

    timer_3_app = Timer_3()
    sys.exit(timer_3_app.start())


if __name__ == "__main__":
    main()
