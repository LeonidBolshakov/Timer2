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
)

import functions as f

# noinspection PyPep8Naming
from const import Const as C, TuneDescr


class Tunes(QWidget):
    """
    Класс для работы с настройками программы
    Описание настроек находятся в const.py. Имена описаний начинаются на TUNE_
    """

    dict_tunes: dict[str, Any] = dict()

    btnBoxOk: QDialogButtonBox
    checkBoxRestore: QCheckBox
    lnEdVoiceInterval: QLineEdit
    lnEdBeepInterval: QLineEdit
    lnEdBeepPeriodInFinal: QLineEdit
    lnEdFileTunes: QLineEdit
    lnEdFileMelody: QLineEdit
    toolBtnFileTunes: QToolButton
    toolBtnMelody: QToolButton

    def __init__(self):
        super().__init__()

        uic.loadUi(C.TUNES_UI, self)  # Установка данных Qt Designer в объект
        self.path_file_tunes = ""  # Путь на файл с настройками. Может изменяться.

        self.connections()  # Соединение слотов и сигналов
        self.set_validators()  # Установка валидаторов
        Tunes.dict_tunes = self.init_tunes()  # Инициализируем словарь настроек
        self.display = {
            C.TUNE_FILE_MELODY.name_tune: self.lnEdFileMelody,
            C.TUNE_FILE_TUNE.name_tune: self.lnEdFileTunes,
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
        self.toolBtnFileTunes.clicked.connect(self.on_toolBtnFileTunes)
        self.toolBtnMelody.clicked.connect(self.on_toolBtnMelody)
        self.checkBoxRestore.stateChanged.connect(self.on_checkBoxRestore)
        self.lnEdFileTunes.editingFinished.connect(self.on_lnEdFileTunes)
        self.connection_edit_line(self.lnEdVoiceInterval, C.TUNE_VOICE_INTERVAL)
        self.connection_edit_line(self.lnEdBeepInterval, C.TUNE_BEEP_INTERVAL)
        self.connection_edit_line(self.lnEdFileTunes, C.TUNE_FILE_TUNE)
        self.connection_edit_line(
            self.lnEdBeepPeriodInFinal, C.TUNE_BEEP_PERIOD_IN_FINAL
        )

    def set_validators(self):
        """Назначение валидаторов полям ввода"""
        self.lnEdVoiceInterval.setValidator(QIntValidator(0, 59, self))
        self.lnEdBeepInterval.setValidator(QIntValidator(0, 59, self))
        self.lnEdBeepPeriodInFinal.setValidator(QIntValidator(0, 59, self))

    def init_tunes(self) -> dict[str, Any]:
        Tunes.dict_tunes = self.read_new_file_tunes(C.FILE_TUNES_0)
        new_path_file_tunes = self.get_tune(C.TUNE_FILE_TUNE)
        return self.read_new_file_tunes(new_path_file_tunes)

    def read_new_file_tunes(self, new_path_file: str) -> dict[str, Any]:
        """
        Замена файла настроек
        :param: (str) - Путь на новый файл настроек
        :return: (dict[str, Any]) - Словарь настроек
        """
        self.path_file_tunes = new_path_file
        return self.read_tunes()

    def read_tunes(self) -> dict[str, Any]:
        """
        Инициализация словаря настроек.
        Словарь считывается с файла. Если файла нет или его структура испорчена - берутся настройки по умолчанию.
        :return: Словарь настроек
        """
        try:
            with open(self.path_file_tunes, "r") as file:
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
        widget.editingFinished.connect(lambda: self.finish_editing(tune))

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
            with open(self.path_file_tunes, "w") as file:
                json.dump(self.dict_tunes, file)
        except Exception as e:
            f.inform_fatal_error(C.TITLE_ERROR_WRITE, f"{C.TEXT_ERROR_WRITE}\n{e}")

    def on_toolBtnMelody(self) -> None:
        """Обработка нажатия кнопки выбора мелодии"""
        # Вызывается диалог выбора файла мелодии.
        file_path = self.get_file_path(
            tune=C.TUNE_FILE_MELODY,
            title=C.TITLE_SELECT_MELODY,
            types_file=C.TYPES_FILE_MELODY,
        )
        if file_path:
            self.finish_editing(C.TUNE_FILE_MELODY, file_path)

    def on_toolBtnFileTunes(self) -> None:
        """Обработка нажатия кнопки задания файла настроек"""
        # Вызывается диалог задания файла настроек.
        new_path_file_tunes = self.get_file_path(
            tune=C.TUNE_FILE_TUNE,
            title=C.TITLE_SELECT_FILE_TUNE,
            types_file=C.TYPES_FILE_TUNES,
        )
        # Устанавливаем новый файл настроек
        if new_path_file_tunes:
            self.set_new_tunes(new_path_file_tunes)

    def set_new_tunes(self, new_path_file_tunes: str):
        """
        Устанавливаем новый файл настроек
        :param: (str) Путь на новый файл настроек
        """
        Tunes.dict_tunes = self.read_new_file_tunes(C.FILE_TUNES_0)
        self.finish_editing(C.TUNE_FILE_TUNE, new_path_file_tunes)

        Tunes.dict_tunes = self.read_new_file_tunes(new_path_file_tunes)
        self.finish_editing(C.TUNE_FILE_TUNE, new_path_file_tunes)

        self.visualization_tunes()

    def get_file_path(self, tune: TuneDescr, title: str, types_file: str) -> str:
        """
        Вызов диалога определения имени файла
        :Params
            tune: TuneDescr. Настройка с именем файла
            title: str. Заголовок интерфейса выбора файла
            types_file: str. Допустимые типы файлов
        :Return
            str - путь на файл
        """
        # В качестве начальной директории назначаем директорию ранее выбранного файла.
        # Если ранее выбранного файла нет - назначаем рабочую папку программы
        directory = Path(self.get_tune(tune)).parent
        directory_str = str(directory) if directory else None
        file_path, _ = QFileDialog.getOpenFileName(
            None, title, directory_str, types_file
        )
        return file_path

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

    def finish_editing(self, tune: TuneDescr, value: str | None = None) -> None:
        """
        Завершает ввод настройки: сохраняет и визуализирует значение настройки.
        :param tune:    Введённая настройка.
                        По умолчанию предполагается, что значение настройки вводится и отображается в одном виджете.
                        Соответствие имён настроек и виджетов для их отображения задаётся словарём self.display.
        :param value:   (Опционально). Значение настройки.
                        Параметр определяет, что значение настройки берётся не из виджета, а задаётся параметром.
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

        if not display_tune or not value_tune:
            return

        match value_tune:
            case int():
                display_tune.setText(str(value_tune))

            case str() if value_tune.startswith(
                C.CHECK_STATE
            ):  # Настройка типа CheckState
                display_tune.setCheckState(f.get_check_state(value_tune))

            case str():
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

    @staticmethod
    def get_tune(tune: TuneDescr) -> Any:
        """
        Получить значение настройки
        :param tune: Настройка
        :return: Значение настройки
        """
        try:
            value = Tunes.dict_tunes[tune.name_tune]
            return value
        except KeyError:
            f.inform_fatal_error(
                C.TITLE_INTERNAL_ERROR, f"{C.TEXT_NO_TUNES} {tune.name_tune}"
            )

    def on_lnEdFileTunes(self) -> None:
        """
        Устанавливаем файл настроек, имя которого введено вручную.
        """
        # Проверяем и, при необходимости устанавливаем расширение файла
        new_file_name = self.lnEdFileTunes.text()
        if Path(new_file_name).suffix != f".{C.JSON}":
            new_file_name += f".{C.JSON}"

        # Проверяем валидность введённого имени файла
        if not f.is_valid_filename(new_file_name):
            QMessageBox.warning(
                None,
                C.TITLE_SELECT_FILE_TUNE,
                f"{C.TEXT_ERROR_FILE_NAME} {new_file_name}",
            )
            old_file_name = self.get_tune(C.TUNE_FILE_TUNE)
            self.lnEdFileTunes.setText(old_file_name)
            return

        # Устанавливаем новый файл настроек
        self.set_new_tunes(new_file_name)
