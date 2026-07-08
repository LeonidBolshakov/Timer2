from __future__ import annotations

from typing import TYPE_CHECKING
from pathlib import Path

from PyQt6.QtCore import QSignalBlocker, Qt
from PyQt6.QtWidgets import (
    QFileDialog,
    QLineEdit,
    QMessageBox,
)

from .const import Const as C
from .param_keys import ParamKeys

if TYPE_CHECKING:
    from .tunes import TunesWindow


class TunesController:
    def __init__(self, window: TunesWindow) -> None:
        self.window = window
        self.settings = window.settings

    def refresh_ui(self) -> None:
        model = self.settings.model

        self.window.lnEdFileTunes.setText(str(self.settings.settings_file))
        self.window.lnEdFileMelody.setText(model.file_melody)
        self.window.lnEdVoiceInterval.setText(str(model.voice_interval))
        self.window.lnEdBeepInterval.setText(str(model.beep_interval))
        self.window.lnEdBeepPeriodInFinal.setText(str(model.beep_period_in_final))

        with QSignalBlocker(self.window.checkBoxRestore):
            self.window.checkBoxRestore.setCheckState(
                Qt.CheckState.Checked if model.restore_time else Qt.CheckState.Unchecked
            )

    def on_voice_interval_edited(self) -> None:
        self._set_int_from_line_edit(
            ParamKeys.VOICE_INTERVAL, self.window.lnEdVoiceInterval
        )

    def on_beep_interval_edited(self) -> None:
        self._set_int_from_line_edit(
            ParamKeys.BEEP_INTERVAL, self.window.lnEdBeepInterval
        )

    def on_beep_period_in_final_edited(self) -> None:
        self._set_int_from_line_edit(
            ParamKeys.BEEP_PERIOD_IN_FINAL,
            self.window.lnEdBeepPeriodInFinal,
        )

    def on_restore_changed(self, state: int) -> None:
        self.settings.set_value(
            ParamKeys.RESTORE_TIME,
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
        self.settings.set_value(ParamKeys.FILE_MELODY, file_path)
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
        text = self.window.lnEdFileTunes.text().strip()
        if not text:
            self.refresh_ui()
            return
        path = self._normalize_json_path(text)
        self._switch_settings_file(path)

    def _set_int_from_line_edit(self, key: ParamKeys, line_edit: QLineEdit) -> None:
        try:
            self.settings.set_value(key, line_edit.text())
        except ValueError as err:
            QMessageBox.warning(
                self.window,
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

    def _select_file(self, current_file: str, title: str, types_file: str) -> str:
        directory = (
            Path(current_file).expanduser().parent if current_file else Path.cwd()
        )
        file_path, _ = QFileDialog.getOpenFileName(
            self.window,
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
            self.window,
            C.TITLE_ERROR_WRITE,
            "\n\n".join(warnings),
        )
