from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import NoReturn

from PyQt6.QtWidgets import QApplication, QLineEdit, QMessageBox
from num2words import num2words  # type: ignore
import pygame

from .const import Const as C
from .signals import signals

PROGRAM_NAME = "Timer_2"


def num(line_edit: QLineEdit) -> int:
    return int(line_edit.text()) if line_edit.text() else 0


def go_quit() -> NoReturn:
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
