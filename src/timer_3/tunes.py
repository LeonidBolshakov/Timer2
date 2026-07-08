from __future__ import annotations

from pathlib import Path

from PyQt6 import uic
from PyQt6.QtWidgets import (
    QCheckBox,
    QDialogButtonBox,
    QLineEdit,
    QToolButton,
    QWidget,
)

from .const import Const as C
from .param_keys import ParamKeys
from .mapper import dto_to_model, model_to_dto
from .model import TuneValue, Model
from .storage import Storage
from . import functions as f
from .tunes_configurator import TunesConfigurator
from .tunes_controller import TunesController


class TunesSettings:
    """Менеджер настроек: модель + загрузка/сохранение + переключение файла."""

    def __init__(self) -> None:
        self.storage = Storage()
        self.model: Model = dto_to_model(self.storage.load())

    @property
    def settings_file(self) -> Path:
        return self.storage.settings_file

    def save(self) -> None:
        self.storage.save(model_to_dto(self.model))

    def switch_settings_file(self, settings_file: Path) -> None:
        """
        Переключает активный файл настроек.
        """
        dto = self.storage.switch_settings_file(settings_file)
        self.model = dto_to_model(dto)

    def set_value(self, key: ParamKeys, value: TuneValue) -> None:
        self.model.set_value(key, value)
        self.save()


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

    def __init__(self, settings: TunesSettings) -> None:
        super().__init__()
        self.settings = settings
        uic.loadUi(str(f.resource_path(C.TUNES_UI)), self)

        self.controller = TunesController(self)
        self.configurator = TunesConfigurator(self, self.controller)

    def refresh_ui(self) -> None:
        self.controller.refresh_ui()

    def show_ui(self) -> None:
        self.show()
