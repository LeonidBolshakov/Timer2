"""Класс для работы с настройками программы"""

import json
from typing import Any
from pathlib import Path

from PyQt6 import uic
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIntValidator
from PyQt6.QtWidgets import (
    QWidget,
    QLineEdit,
    QToolButton,
    QFileDialog,
    QMessageBox,
    QDialogButtonBox,
    QCheckBox,
    QMainWindow,
)

import functions as f

# noinspection PyPep8Naming
from const import Const as C, TuneDescr


class Tunes(QWidget):
    """
    Класс для работы с настройками программы
    Описание настроек находятся в const.py. Имена описаний начинаются на TUNE_
    """

    btnBoxOk: QDialogButtonBox
    checkBoxRestore: QCheckBox
    lnEdVoiceInterval: QLineEdit
    lnEdBeepInterval: QLineEdit
    lnEdBeepPeriodInFinal: QLineEdit
    lnEdFileMelody: QLineEdit
    toolBtnMelody: QToolButton

    def __init__(self, timer_2=None):
        super().__init__()

        self.timer_2 = timer_2

        uic.loadUi(C.TUNES_UI, self)  # Установка данных Qt Designer в объект

        self.connections()  # Соединение слотов и сигналов
        self.set_validators()  # Установка валидаторов
        self.dict_tunes = self.init_tunes()  # Инициализируем словарь настроек
        self.display = {
            C.TUNE_FILE_MELODY.name_tune: self.lnEdFileMelody,
            C.TUNE_VOICE_INTERVAL.name_tune: self.lnEdVoiceInterval,
            C.TUNE_BEEP_INTERVAL.name_tune: self.lnEdBeepInterval,
            C.TUNE_BEEP_PERIOD_IN_FINAL.name_tune: self.lnEdBeepPeriodInFinal,
            C.TUNE_RESTORE_TIME.name_tune: self.checkBoxRestore,
            C.TUNE_HM_H.name_tune: None,
            C.TUNE_HM_M.name_tune: None,
            C.TUNE_MS_M.name_tune: None,
            C.TUNE_MS_S.name_tune: None,
        }  # Словарь соответствий между именами настроек и отображающими их виджетами
        self.visualization_tunes()  # Отображение первоначального состояния настроек

    def connections(self):
        """Назначение программ обработки сигналов"""
        self.btnBoxOk.clicked.connect(self.hide)
        self.toolBtnMelody.clicked.connect(self.on_toolBtnMelody)
        self.checkBoxRestore.stateChanged.connect(self.on_checkBoxRestore)
        self.connection_edit_line(self.lnEdVoiceInterval, C.TUNE_VOICE_INTERVAL)
        self.connection_edit_line(self.lnEdBeepInterval, C.TUNE_BEEP_INTERVAL)
        self.connection_edit_line(
            self.lnEdBeepPeriodInFinal, C.TUNE_BEEP_PERIOD_IN_FINAL
        )

    def set_validators(self):
        """Назначение валидаторов полям ввода"""
        self.lnEdVoiceInterval.setValidator(QIntValidator(0, 59, self))
        self.lnEdBeepInterval.setValidator(QIntValidator(0, 59, self))
        self.lnEdBeepPeriodInFinal.setValidator(QIntValidator(0, 59, self))

    def init_tunes(self) -> dict[str, Any]:
        """
        Инициализация словаря настроек.
        Словарь считывается с файла. Если файла нет или его структура испорчена - берутся настройки по умолчанию.
        :return: Словарь настроек
        """
        try:
            with open(C.FILE_TUNES, "r") as file:
                tunes_from_file = json.load(file)
                if self.is_validate(tunes_from_file):
                    return tunes_from_file
                else:
                    QMessageBox.warning(None, C.TITLE_ERROR_READ, C.TEXT_ERROR_READ)
        except FileNotFoundError:
            pass  # Отсутствие файла настроек не ошибка.
        except Exception as e:
            QMessageBox.warning(None, C.TITLE_ERROR_READ, f"{C.TEXT_ERROR_READ}\n{e}")
        return self.get_default_tunes()

    def connection_edit_line(self, widget: QLineEdit, tune: TuneDescr):
        """Назначение программы обработки сигнала"""
        widget.editingFinished.connect(lambda: self.editing_finished(tune))

    @staticmethod
    def is_validate(tunes: object) -> bool:
        """
        Проверяет валидность объекта настроек.
        Это должен быть словарь, каждый ключ которого строка.
        :param tunes: Объект с настройками.
        :return: FALSE, если tunes невалиден. TRUE если замечания не найдены.
        """
        if not isinstance(tunes, dict):
            return False
        for key in tunes.keys():
            if not isinstance(key, str):
                return False
        return True

    @staticmethod
    def get_default_tunes() -> dict[str, Any]:
        """
        Формирует настройки по умолчанию.
        Настройки по умолчанию заданы в классе констант. Их имена начинаются на 'TUNE_'
        :returns: Словарь настроек.
        """

        # Формирование словаря настроек со значениями по умолчанию.
        return {
            key: value.default
            for key, value in vars(
                C
            ).items()  # цикл по всем переменным словаря констант
            if key.startswith("TUNE_")
        }  # Пробегаем по всем константам и выбираем нужные.

    # noinspection PyTypeChecker
    def write_tunes(self) -> None:
        """
        Запись словаря настроек в файл настроек
        :return: None
        """
        try:
            with open(C.FILE_TUNES, "w") as file:
                json.dump(self.dict_tunes, file)
        except Exception as e:
            f.inform_fatal_error(C.TITLE_ERROR_WRITE, f"{C.TEXT_ERROR_WRITE}\n{e}")

    def on_toolBtnMelody(self) -> None:
        """Обработка нажатия кнопки выбора мелодии"""
        # Вызывается диалог выбора файла мелодии.
        # В качестве начальной директории назначаем директорию ранее выбранного файла.
        # Если ранее выбранного файла нет - назначаем рабочую папку программы
        directory = Path(self.get_tune(C.TUNE_FILE_MELODY)).parent
        directory_str = str(directory) if directory else None
        file_melody, _ = QFileDialog.getOpenFileName(
            self, C.TEXT_SELECT_MELODY, directory_str, C.TYPES_FILE_MELODY
        )
        if file_melody:
            self.editing_finished(C.TUNE_FILE_MELODY, file_melody)

    def on_checkBoxRestore(self, state: int) -> None:
        """Обработка изменения статуса чекбокса"""
        match state:
            case 0:
                self.put_tune(C.TUNE_RESTORE_TIME, str(Qt.CheckState.Unchecked))
            case 2:
                self.put_tune(C.TUNE_RESTORE_TIME, str(Qt.CheckState.Checked))
            case _:
                f.inform_fatal_error(
                    C.TITLE_ERROR_TUNE, f"{C.TEXT_ERROR_VALUE} *'{state}'*"
                )

    def editing_finished(self, tune: TuneDescr, value: str | None = None) -> None:
        """
        Завершает ввод настройки: сохраняет и визуализирует значение настройки.
        :param tune:    Введённая настройка.
                        По умолчанию предполагается, что значение настройки вводится и отображается в одном виджете.
                        Соответствие имён настроек и виджетов для их отображения задаётся словарём self.display.
        :param value:   (Опционально). Значение настройки.
                        Параметр задаётся если значение настройки берётся не из виджета, а получается иным путём.
        :return: None
        """
        # Записывает настройку в словарь настроек.
        # Если значение настройки не задано параметром, то оно берётся из виджета
        if value:
            self.put_tune(tune, value)
            self.visualization_tune(tune.name_tune)  # Визуализирует введённую настройку
        else:
            self.put_tune(tune, self.display[tune.name_tune].text())

    def visualization_tunes(self):
        """Визуализация всех настроек"""
        for key in self.dict_tunes.keys():
            self.visualization_tune(key)

    def visualization_tune(self, name_tune: str) -> None:
        """Визуализация значения настройки"""
        display_tune = self.display[name_tune]
        value_tune = self.dict_tunes[name_tune]
        value_type = type(value_tune).__name__

        if not display_tune or not value_tune:
            return
        match value_type:
            case "int":
                display_tune.setText(str(value_tune))
            case "str" if value_tune.startswith(
                "CheckState."
            ):  # Настройка типа CheckState
                display_tune.setCheckState(f.get_check_state(value_tune))
            case "str":
                display_tune.setText(value_tune)

    def put_tune(self, tune: TuneDescr, value: str | int) -> None:
        """
        Запись настройки в словарь настроек
        :param tune: настройка
        :param value: значение настройки
        :return: None
        """
        # Тип настройки должен быть такой же, как тип настройки по умолчанию.
        try:
            match type(tune.default).__name__:
                case "int":
                    self.dict_tunes[tune.name_tune] = int(value)
                case "str":
                    self.dict_tunes[tune.name_tune] = value
                case _:
                    current_value = self.dict_tunes[tune.name_tune]
                    f.inform_fatal_error(
                        f"{C.TITLE_INTERNAL_ERROR}",
                        f"{C.TEXT_TYPE_ERROR} {tune.name_tune} - {current_value}",
                    )
        except ValueError as e:
            f.inform_fatal_error(C.TITLE_ERROR_TUNE, f"{C.TEXT_ERROR_VALUE}\n*'{e}'*")
        except KeyError as e:
            f.inform_fatal_error(C.TITLE_ERROR_TUNE, f"{C.TEXT_ERROR_KEY}\n{e}")
        except Exception as e:
            f.inform_fatal_error(C.TITLE_ERROR_TUNE, f"{C.TEXT_ERROR_UNKNOWN}\n{e}")

        self.write_tunes()  # Записывает все настройки в файл настроек

        return

    def get_tune(self, tune: TuneDescr) -> Any:
        """
        Получить значение настройки
        :param tune: Настройка
        :return: Значение настройки
        """
        try:
            value = self.dict_tunes[tune.name_tune]
            return value
        except KeyError:
            f.inform_fatal_error(
                C.TITLE_INTERNAL_ERROR, "{C.TEXT_NO_TUNES} {tune.name_tune}"
            )
