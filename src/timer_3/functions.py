from __future__ import annotations

import os
import sys
import re
from pathlib import Path
from typing import NoReturn

import pygame
from PyQt6.QtWidgets import QApplication, QLineEdit, QMessageBox
from num2words import num2words  # type: ignore

from .param_keys import TuneValue
from .const import Const as C
from .signals import signals
from . import settings_schema as schema

PROGRAM_NAME = "Timer_3"


def num(line_edit: QLineEdit) -> int:
    return int(line_edit.text()) if line_edit.text() else 0


def go_quit() -> NoReturn:
    # noinspection PyArgumentList
    app = QApplication.instance()
    if app is not None:
        app.quit()
        app.processEvents()
        sys.exit(0)

    QMessageBox.warning(None, C.TITLE_INTERNAL_ERROR, C.TEXT_INTERNAL_ERROR)
    sys.exit(1)


def hour_minutes_sec(seconds: int) -> tuple[int, int, int]:
    hour, min_sec = divmod(seconds, C.SECONDS_IN_HOUR)
    minutes, sec = divmod(min_sec, C.SECONDS_IN_MINUTE)
    return hour, minutes, sec


def time_to_text(seconds: int) -> str:
    hour, minutes, sec = hour_minutes_sec(seconds)
    hour_text = num_to_text(hour, C.GENDER_M, C.FORMS_HOUR)
    minutes_text = num_to_text(minutes, C.GENDER_F, C.FORMS_MINUTE)
    sec_text = num_to_text(sec, C.GENDER_F, C.FORMS_SECUNDA)
    return (hour_text + minutes_text + sec_text).capitalize()


def num_to_text(number: int, gender: str, word_forms: list[str]) -> str:
    if number == 0:
        return ""
    return (
        f"{num2words(number, lang=C.LANG_RU, gender=gender)} "
        f"{get_word_form(number, word_forms)} "
    )


def get_word_form(number: int, word_after_number: list[str]) -> str:
    last_digit = number % 10
    last_digits = number % 100

    match last_digit:
        case 1 if not 11 <= last_digits <= 14:
            return word_after_number[1]
        case 2 | 3 | 4 if not 11 <= last_digits <= 14:
            return word_after_number[2]
        case _:
            return word_after_number[0]


def beep() -> None:
    # noinspection PyArgumentList
    QApplication.beep()


def inform_fatal_error_and_quit(title: str, text: str) -> NoReturn:
    QMessageBox.warning(None, title, text)
    go_quit()


def check_music_finished() -> None:
    if not pygame.mixer.music.get_busy():
        signals.melody_finished.emit()


def get_app_settings_dir() -> Path:
    settings_dir = Path(os.getenv("APPDATA", Path.home())) / PROGRAM_NAME
    settings_dir.mkdir(parents=True, exist_ok=True)
    return settings_dir


def resource_path(path: str | Path) -> Path:
    """
    Возвращает путь к ресурсу в исходниках,
    PyInstaller-сборке или внешний абсолютный путь.
    """
    resource = Path(path)

    if resource.is_absolute():
        return resource

    if getattr(sys, "frozen", False):
        base_dir = Path(sys._MEIPASS)  # type: ignore[attr-defined]
    else:
        base_dir = Path(__file__).resolve().parents[2]

    return base_dir / resource


def cycle_intervals_list(text: str) -> list[int]:
    try:
        # Сразу переводим в int при разделении строки
        lst = [int(x) for x in re.split(C.CYCLE_SEPARATOTS, text.strip()) if x]
    except ValueError:
        # Если попалась буква или некорректный символ
        return []

    # Защита от пустой строки
    if not lst:
        return []

    # Быстрая проверка диапазона для уже готовых чисел
    for number in lst:
        if not (0 < number <= schema.CYCLE_INTERVAL_ELEMENT_MAX):
            return []
    return lst


def error(widget: QLineEdit) -> None:
    beep()


def _to_int(value: TuneValue, *, min_value: int = 0, max_value: int = 999999999) -> int:
    """
    Строго преобразует значение настройки в int.

    bool специально запрещён: в Python bool является подклассом int,
    но для числовых настроек таймера это ошибка ввода.
    """
    if isinstance(value, bool):
        inform_fatal_error_and_quit(C.TITLE_INTERNAL_ERROR, C.TEXT_ERROR_BOOL)

    if isinstance(value, int):
        result = value
    elif isinstance(value, str):
        text = value.strip()
        if not text:
            return 0
        result = int(text)
    else:
        inform_fatal_error_and_quit(
            C.TITLE_INTERNAL_ERROR, f"{C.TEXT_ERROR_NO_INT} - {value!r}"
        )

    if not min_value <= result <= max_value:
        inform_fatal_error_and_quit(
            C.TITLE_ERROR_READ,
            f" Испорчен файл с параметрами (JSON)\n"
            f"Значение {result} вне диапазона {min_value}..{max_value}",
        )

    return result


def _to_bool(value: TuneValue) -> bool:
    if isinstance(value, bool):
        return value

    if isinstance(value, int):
        if value in (0, 1):
            return bool(value)
        inform_fatal_error_and_quit(
            C.TITLE_INTERNAL_ERROR, f"{C.TEXT_ERROR_BOOL} - {value!r}"
        )
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"1", "true", "yes", "on", "checked", "checkstate.checked"}:
            return True
        if normalized in {
            "0",
            "false",
            "no",
            "off",
            "unchecked",
            "checkstate.unchecked",
        }:
            return False

    inform_fatal_error_and_quit(
        C.TITLE_INTERNAL_ERROR, f"{C.TEXT_ERROR_BOOL} - {value!r}"
    )


def _to_cycle_interval(value: list[int]) -> str:
    return str(value)


def _to_str(
    value: object,
) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return str(value)

    inform_fatal_error_and_quit(
        C.TITLE_INTERNAL_ERROR,
        f"Функция _to_str. Неверный тип переменной\n" f" - {type(value).__name__}",
    )
