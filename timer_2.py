import sys
from enum import Enum
from functools import lru_cache

import PyQt6
from PyQt6.QtWidgets import QMainWindow, QLineEdit, QPushButton, QLabel, QApplication
from PyQt6 import uic
from PyQt6.QtGui import QRegularExpressionValidator
from PyQt6.QtCore import QRegularExpression

from clock import Clock
import functions as f


class TimeField(Enum):
    HM = 1
    MS = 2


class Timer2(QMainWindow):
    """
    Главное окно приложения.
    Обеспечивает пользовательский интерфейс и обработку действий пользователя.
    """

    btnQuit: QPushButton
    btnStart: QPushButton
    btnTunes: QPushButton
    lblSec: QLabel
    lineEdit_HM_H: QLineEdit
    lineEdit_HM_M: QLineEdit
    lineEdit_MS_M: QLineEdit
    lineEdit_MS_S: QLineEdit

    def __init__(self):
        super().__init__()
        uic.loadUi("timer_2.ui", self)

        self.clock = None  # Создаем атрибут для хранения объекта Clock

        self.validator_hour = QRegularExpressionValidator()
        self.validator_min_sec = QRegularExpressionValidator()
        self.set_validators()
        self.assign_validators()

        self.connect_signals()
        self.set_bolds()
        self.init_vars()

    def set_validators(self):
        self.validator_hour = QRegularExpressionValidator(
            QRegularExpression(r"[0-9]|1[0-9]|2[0-3]")
        )
        self.validator_min_sec = QRegularExpressionValidator(
            QRegularExpression(r"[0-5][0-9]")
        )

    def assign_validators(self):
        self.lineEdit_HM_H.setValidator(self.validator_hour)
        self.lineEdit_HM_M.setValidator(self.validator_min_sec)
        self.lineEdit_MS_M.setValidator(self.validator_min_sec)
        self.lineEdit_MS_S.setValidator(self.validator_min_sec)

    def connect_signals(self):
        self.btnQuit.clicked.connect(f.on_quit)
        self.btnStart.clicked.connect(self.on_btnStart_click)
        self.btnTunes.clicked.connect(self.on_btnTunes_click)
        self.lineEdit_HM_H.textEdited.connect(self.on_lineEdit_HM_H_edited)
        self.lineEdit_HM_M.textEdited.connect(self.on_lineEdit_HM_M_edited)
        self.lineEdit_MS_M.textEdited.connect(self.on_lineEdit_MS_M_edited)
        self.lineEdit_MS_S.textEdited.connect(self.on_lineEdit_MS_S_edited)

    def set_bolds(self):
        for line_edit in (
                self.lineEdit_HM_H,
                self.lineEdit_HM_M,
                self.lineEdit_MS_M,
                self.lineEdit_MS_S,
        ):
            font = line_edit.font()
            font.setBold(True)
            line_edit.setFont(font)

    def init_vars(self):
        self.lblSec.setText("")
        self.lineEdit_MS_M.setFocus()

    def on_btnStart_click(self):
        # Создаем и настраиваем объект Clock, если в нём есть потребность и его ещё нет
        if self.clock is None and self.get_seconds_left() != 0:
            self.clock = Clock(self.get_seconds_left())
            self.clock.draw_time = self.draw_time

    def on_btnTunes_click(self):
        pass

    def on_lineEdit_HM_H_edited(self, txt: str):
        f.on_lineEdit_edited(
            self.highlight_active_field,
            txt,
            self.lineEdit_HM_M,
            self.lineEdit_MS_M,
            self.lineEdit_MS_S,
        )

    def on_lineEdit_HM_M_edited(self, txt: str):
        f.on_lineEdit_edited(
            self.highlight_active_field,
            txt,
            self.btnStart,
            self.lineEdit_MS_M,
            self.lineEdit_MS_S,
        )

    def on_lineEdit_MS_M_edited(self, txt: str):
        f.on_lineEdit_edited(
            self.highlight_active_field,
            txt,
            self.lineEdit_MS_S,
            self.lineEdit_HM_H,
            self.lineEdit_HM_M,
        )

    def on_lineEdit_MS_S_edited(self, txt: str):
        f.on_lineEdit_edited(
            self.highlight_active_field,
            txt,
            self.btnStart,
            self.lineEdit_HM_H,
            self.lineEdit_HM_M,
        )

    def draw_time(self, seconds_left: int):
        """
        Обновляет отображение времени на экране.

        Args:
            seconds_left (int): Оставшееся количество секунд

        Отображает время в формате ЧЧ:ММ или ММ:СС в зависимости от выбранного режима.
        """

        hour, minutes, sec = f.hour_minutes_sec(seconds_left)

        match self.active_time_field():
            case TimeField.MS:
                self.draw_min_sec(minutes, sec)
            case TimeField.HM:
                self.draw_hour_min(hour, minutes, sec)

        if seconds_left <= 0:
            QApplication.processEvents()

    def draw_hour_min(self, hour: int, minutes: int, sec: int):
        self.lineEdit_HM_H.setText(f"{hour:02}")
        self.lineEdit_HM_M.setText(f"{minutes:02}")
        self.lblSec.setText(f": {sec:02}")

    def draw_min_sec(self, minutes: int, sec: int):
        self.lineEdit_MS_M.setText(f"{minutes:02}")
        self.lineEdit_MS_S.setText(f"{sec:02}")

    def get_seconds_left(self) -> int:
        match self.active_time_field():
            case TimeField.MS:
                return f.num(self.lineEdit_MS_M) * 60 + f.num(self.lineEdit_MS_S)
            case TimeField.HM:
                return f.num(self.lineEdit_HM_H) * 3600 + f.num(self.lineEdit_HM_M) * 60
            case _:
                return 0

    @lru_cache
    def active_time_field(self) -> TimeField | None:
        if self.lineEdit_MS_M.text() or self.lineEdit_MS_S.text():
            return TimeField.MS
        if self.lineEdit_HM_H.text() or self.lineEdit_HM_M.text():
            return TimeField.HM
        return None

    def highlight_active_field(self):
        """Подсветка активного поля ввода"""
        active_style = "QLineEdit { background-color: #f0f0f0; }"
        inactive_style = "QLineEdit { background-color: white; }"

        match self.active_time_field():
            case TimeField.HM:
                self.lineEdit_HM_H.setStyleSheet(active_style)
                self.lineEdit_HM_M.setStyleSheet(active_style)
                self.lineEdit_MS_M.setStyleSheet(inactive_style)
                self.lineEdit_MS_S.setStyleSheet(inactive_style)
            case TimeField.MS:
                self.lineEdit_HM_H.setStyleSheet(inactive_style)
                self.lineEdit_HM_M.setStyleSheet(inactive_style)
                self.lineEdit_MS_M.setStyleSheet(active_style)
                self.lineEdit_MS_S.setStyleSheet(active_style)

    def start(self) -> int:
        """Запуск приложения и отображение главного окна."""

        self.show()  # Показ формы
        return PyQt6.QtWidgets.QApplication.exec()  # Запуск основного цикла приложения


# Запуск приложения
if __name__ == "__main__":
    app = PyQt6.QtWidgets.QApplication(sys.argv)  # Создание экземпляра приложения
    timer_2_app = Timer2()  # Создание экземпляра таймера
    sys.exit(timer_2_app.start())  # Запуск таймера
