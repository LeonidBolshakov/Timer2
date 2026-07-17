from __future__ import annotations


from PyQt6 import uic
from PyQt6.QtWidgets import (
    QCheckBox,
    QDialogButtonBox,
    QLineEdit,
    QToolButton,
    QWidget,
)

from .const import Const as C
from . import functions as f
from .context import Context
from .tunes_configurator import TunesConfigurator
from .tunes_controller import TunesController


class TunesWindow(QWidget):
    """Окно настроек: владеет UI, контроллером и конфигуратором."""

    btnBoxOk: QDialogButtonBox
    checkBoxRestore: QCheckBox
    lnEdBeepInterval: QLineEdit
    lnEdBeepPeriodInFinal: QLineEdit
    lnEdFileTunes: QLineEdit
    lnEdFileMelody: QLineEdit
    lnEditCycleIntervals: QLineEdit
    lnEdVoiceInterval: QLineEdit
    toolBtnFileTunes: QToolButton
    toolBtnMelody: QToolButton

    controller: TunesController
    configurator: TunesConfigurator

    def __init__(self, settings: Context) -> None:
        super().__init__()
        self.settings = settings
        uic.loadUi(str(f.resource_path(C.TUNES_UI)), self)

        self.controller = TunesController(self)
        self.configurator = TunesConfigurator(self, self.controller)

    def refresh_ui(self) -> None:
        self.controller.refresh_tune_ui()

    def show_ui(self) -> None:
        self.show()
