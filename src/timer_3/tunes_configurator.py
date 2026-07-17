from __future__ import annotations

from typing import TYPE_CHECKING
from PyQt6.QtGui import QIntValidator

from .tunes_controller import TunesController
from . import settings_schema as shema

if TYPE_CHECKING:
    from .tunes import TunesWindow


class TunesConfigurator:
    def __init__(self, window: TunesWindow, controller: TunesController) -> None:
        self.window = window
        self.controller = controller

        self.voice_interval_validator = QIntValidator(
            shema.VOICE_INTERVAL_MIN, shema.VOICE_INTERVAL_MAX, self.window
        )
        self.beep_interval_validator = QIntValidator(
            shema.BEEP_INTERVAL_MIN, shema.BEEP_INTERVAL_MAX, self.window
        )
        self.beep_period_in_final_validator = QIntValidator(
            shema.BEEP_PERIOD_IN_FINAL_MIN, shema.BEEP_PERIOD_IN_FINAL_MIN, self.window
        )

        self._set_validators()
        self.controller.refresh_tune_ui()
        self._connect_signals()

    def _connect_signals(self) -> None:
        self.window.btnBoxOk.accepted.connect(self.window.hide)
        self.window.toolBtnFileTunes.clicked.connect(
            self.controller.on_tool_btn_file_tunes
        )
        self.window.toolBtnMelody.clicked.connect(self.controller.on_tool_btn_melody)
        self.window.checkBoxRestore.stateChanged.connect(
            self.controller.on_restore_changed
        )
        self.window.lnEdFileTunes.editingFinished.connect(
            self.controller.on_file_tunes_edited
        )
        self.window.lnEdVoiceInterval.editingFinished.connect(
            self.controller.on_voice_interval_edited
        )
        self.window.lnEdBeepInterval.editingFinished.connect(
            self.controller.on_beep_interval_edited
        )
        self.window.lnEdBeepPeriodInFinal.editingFinished.connect(
            self.controller.on_beep_period_in_final_edited
        )

    def _set_validators(self) -> None:
        self.window.lnEdVoiceInterval.setValidator(self.voice_interval_validator)
        self.window.lnEdBeepInterval.setValidator(self.beep_interval_validator)
        self.window.lnEdBeepPeriodInFinal.setValidator(
            self.beep_period_in_final_validator
        )
