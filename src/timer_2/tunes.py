from __future__ import annotations

from pathlib import Path

from PyQt6 import uic
from PyQt6.QtCore import QSignalBlocker, Qt
from PyQt6.QtGui import QIntValidator
from PyQt6.QtWidgets import (
    QCheckBox,
    QDialogButtonBox,
    QFileDialog,
    QLineEdit,
    QMessageBox,
    QToolButton,
    QWidget,
)

from .const import Const as C
from .tune_key import TuneKey
from .tunes_mapper import dto_to_model, model_to_dto
from .tunes_model import TuneValue, TunesModel
from .tunes_storage import TunesStorage


class TunesSettings:
    """Менеджер настроек: модель + загрузка/сохранение + переключение файла."""

    def __init__(self) -> None:
        self.storage = TunesStorage()
        self.model: TunesModel = dto_to_model(self.storage.load())

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

    def set_value(self, key: TuneKey, value: TuneValue | str) -> None:
        self.model.set_value(key, value)
        self.save()


class TunesWindow(QWidget):
    """Окно настроек. Работает только с UI и вызывает TunesSettings."""

    btnBoxOk: QDialogButtonBox
    checkBoxRestore: QCheckBox
    lnEdVoiceInterval: QLineEdit
    lnEdBeepInterval: QLineEdit
    lnEdBeepPeriodInFinal: QLineEdit
    lnEdFileTunes: QLineEdit
    lnEdFileMelody: QLineEdit
    toolBtnFileTunes: QToolButton
    toolBtnMelody: QToolButton

    def __init__(self, settings: TunesSettings) -> None:
        super().__init__()
        self.settings = settings
        uic.loadUi(C.TUNES_UI, self)

        self._connect_signals()
        self._set_validators()
        self.refresh_ui()

    def _connect_signals(self) -> None:
        self.btnBoxOk.clicked.connect(self.hide)
        self.toolBtnFileTunes.clicked.connect(self.on_tool_btn_file_tunes)
        self.toolBtnMelody.clicked.connect(self.on_tool_btn_melody)
        self.checkBoxRestore.stateChanged.connect(self.on_restore_changed)
        self.lnEdFileTunes.editingFinished.connect(self.on_file_tunes_edited)
        self.lnEdVoiceInterval.editingFinished.connect(self.on_voice_interval_edited)
        self.lnEdBeepInterval.editingFinished.connect(self.on_beep_interval_edited)
        self.lnEdBeepPeriodInFinal.editingFinished.connect(
            self.on_beep_period_in_final_edited
        )

    def _set_validators(self) -> None:
        self.lnEdVoiceInterval.setValidator(QIntValidator(1, 59, self))
        self.lnEdBeepInterval.setValidator(QIntValidator(1, 59, self))
        self.lnEdBeepPeriodInFinal.setValidator(QIntValidator(1, 59, self))

    def refresh_ui(self) -> None:
        model = self.settings.model

        self.lnEdFileTunes.setText(str(self.settings.settings_file))
        self.lnEdFileMelody.setText(model.file_melody)
        self.lnEdVoiceInterval.setText(str(model.voice_interval))
        self.lnEdBeepInterval.setText(str(model.beep_interval))
        self.lnEdBeepPeriodInFinal.setText(str(model.beep_period_in_final))

        with QSignalBlocker(self.checkBoxRestore):
            self.checkBoxRestore.setCheckState(
                Qt.CheckState.Checked if model.restore_time else Qt.CheckState.Unchecked
            )

    def on_voice_interval_edited(self) -> None:
        self._set_int_from_line_edit(TuneKey.VOICE_INTERVAL, self.lnEdVoiceInterval)

    def on_beep_interval_edited(self) -> None:
        self._set_int_from_line_edit(TuneKey.BEEP_INTERVAL, self.lnEdBeepInterval)

    def on_beep_period_in_final_edited(self) -> None:
        self._set_int_from_line_edit(
            TuneKey.BEEP_PERIOD_IN_FINAL,
            self.lnEdBeepPeriodInFinal,
        )

    def on_restore_changed(self, state: int) -> None:
        self.settings.set_value(
            TuneKey.RESTORE_TIME,
            state == Qt.CheckState.Checked.value,
        )
        self._show_storage_warnings()

    def on_tool_btn_melody(self) -> None:
        file_path = self._select_file(
            current_file=self.settings.model.file_melody,
            title=C.TITLE_SELECT_MELODY,
            types_file=C.TYPES_FILE_MELODY,
        )
        if not file_path:
            return
        self.settings.set_value(TuneKey.FILE_MELODY, file_path)
        self._show_storage_warnings()
        self.refresh_ui()

    def on_tool_btn_file_tunes(self) -> None:
        file_path = self._select_file(
            current_file=str(self.settings.settings_file),
            title=C.TITLE_SELECT_FILE_TUNE,
            types_file=C.TYPES_FILE_TUNES,
        )
        if not file_path:
            return
        self._switch_settings_file(Path(file_path))

    def on_file_tunes_edited(self) -> None:
        text = self.lnEdFileTunes.text().strip()
        if not text:
            self.refresh_ui()
            return
        path = self._normalize_json_path(text)
        self._switch_settings_file(path)

    def _set_int_from_line_edit(self, key: TuneKey, line_edit: QLineEdit) -> None:
        try:
            self.settings.set_value(key, line_edit.text())
        except ValueError as err:
            QMessageBox.warning(
                self,
                C.TITLE_ERROR_TUNE,
                f"{C.TEXT_ERROR_VALUE}\n{err}",
            )
        finally:
            self._show_storage_warnings()
            self.refresh_ui()

    def _switch_settings_file(self, path: Path) -> None:
        self.settings.switch_settings_file(path)
        self._show_storage_warnings()
        self.refresh_ui()

    @staticmethod
    def _select_file(current_file: str, title: str, types_file: str) -> str:
        directory = (
            Path(current_file).expanduser().parent if current_file else Path.cwd()
        )
        file_path, _ = QFileDialog.getOpenFileName(
            None,
            title,
            str(directory),
            types_file,
        )
        return file_path

    def _normalize_json_path(self, text: str) -> Path:
        path = Path(text).expanduser()
        if path.suffix.lower() != f".{C.JSON}":
            path = path.with_suffix(f".{C.JSON}")
        if not path.is_absolute():
            path = self.settings.settings_file.parent / path
        return path.resolve()

    def _show_storage_warnings(self) -> None:
        warnings = self.settings.storage.pop_warnings()

        if not warnings:
            return

        QMessageBox.warning(
            self,
            C.TITLE_ERROR_WRITE,
            "\n\n".join(warnings),
        )
