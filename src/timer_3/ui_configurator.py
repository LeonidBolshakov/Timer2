from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt6.QtCore import QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator

from . import functions as f
from .const import Const as C
from .tunes import TunesSettings
from .timer_controller import Timer3Controller

if TYPE_CHECKING:
    from .main import Timer_3


class Timer3UiConfigurator:
    def __init__(self, window: Timer_3, controller: Timer3Controller) -> None:
        self.window = window
        self.controller = controller
        self.settings = TunesSettings()
        self.set_validators()
        self.connect_signals()
        self.init_vars()

    def set_validators(self) -> None:
        validator_hour = QRegularExpressionValidator(
            QRegularExpression(C.RE_PATTERN_0_24)
        )
        validator_min_sec = QRegularExpressionValidator(
            QRegularExpression(C.RE_PATTERN_0_60)
        )

        self.window.lineEdit_HM_H.setValidator(validator_hour)
        self.window.lineEdit_HM_M.setValidator(validator_min_sec)
        self.window.lineEdit_MS_M.setValidator(validator_min_sec)
        self.window.lineEdit_MS_S.setValidator(validator_min_sec)

    def connect_signals(self) -> None:
        self.window.btnQuit.clicked.connect(f.go_quit)
        self.window.btnStart.clicked.connect(self.controller.on_btn_start_click)
        self.window.btnTunes.clicked.connect(self.controller.on_btn_tunes_click)

        self.window.lineEdit_HM_H.textEdited.connect(
            lambda: self.controller.on_line_edit_edited(
                self.window.lineEdit_HM_H, self.window.lineEdit_HM_M
            )
        )
        self.window.lineEdit_HM_M.textEdited.connect(
            lambda: self.controller.on_line_edit_edited(
                self.window.lineEdit_HM_M, self.window.btnStart
            )
        )
        self.window.lineEdit_MS_M.textEdited.connect(
            lambda: self.controller.on_line_edit_edited(
                self.window.lineEdit_MS_M, self.window.lineEdit_MS_S
            )
        )
        self.window.lineEdit_MS_S.textEdited.connect(
            lambda: self.controller.on_line_edit_edited(
                self.window.lineEdit_MS_S, self.window.btnStart
            )
        )
        self.init_vars()

    def init_vars(self) -> None:
        self.window.lblSec.setText("")
        if self.settings.model.restore_time:
            self.initialize_time_fields()

    def initialize_time_fields(self) -> None:
        model = self.settings.model

        if model.hm_h != 0 or model.hm_m != 0:
            self.window.lineEdit_HM_H.setText(str(model.hm_h))
            self.window.lineEdit_HM_M.setText(str(model.hm_m))

        if model.ms_m != 0 or model.ms_s != 0:
            self.window.lineEdit_MS_M.setText(str(model.ms_m))
            self.window.lineEdit_MS_S.setText(str(model.ms_s))
        pass
