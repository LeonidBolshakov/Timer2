import sys
from enum import Enum

import PyQt6
from PyQt6.QtWidgets import QMainWindow, QLineEdit, QPushButton, QLabel
from PyQt6 import uic
from PyQt6.QtGui import QRegularExpressionValidator
from PyQt6.QtCore import QRegularExpression

from clock import Clock
from functions import on_lineEdit_edited, num, on_quit


class TimeField(Enum):
    HM = 1
    MS = 2


class Timer2(QMainWindow):
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
        self.time_min_sec = False
        self.time_hour_min = False

        self.validator_hour = QRegularExpressionValidator()
        self.validator_min_sec = QRegularExpressionValidator()
        self.set_validators()

        self.assign_validators()
        self.set_bolds()
        self.connect_signals()
        self.assign_validators()

    def connect_signals(self):

        self.btnQuit.clicked.connect(on_quit)
        self.btnStart.clicked.connect(self.on_btnStart_click)
        self.btnTunes.clicked.connect(self.on_btnTunes_click)
        self.lineEdit_HM_H.textEdited.connect(self.on_lineEdit_HM_H_edited)
        self.lineEdit_HM_M.textEdited.connect(self.on_lineEdit_HM_M_edited)
        self.lineEdit_MS_M.textEdited.connect(self.on_lineEdit_MS_M_edited)
        self.lineEdit_MS_S.textEdited.connect(self.on_lineEdit_MS_S_edited)

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

    def on_btnStart_click(self):
        if self.clock is None:  # Создаем объект Clock, если его ещё нет
            self.clock = Clock(self.get_seconds_left())
            self.clock.draw_time = self.draw_time

    def on_btnTunes_click(self):
        pass

    def on_lineEdit_HM_H_edited(self, txt):
        on_lineEdit_edited(
            txt, self.lineEdit_HM_M, self.lineEdit_MS_M, self.lineEdit_MS_S
        )

    def on_lineEdit_HM_M_edited(self, txt):
        on_lineEdit_edited(txt, self.btnStart, self.lineEdit_MS_M, self.lineEdit_MS_S)

    def on_lineEdit_MS_M_edited(self, txt):
        on_lineEdit_edited(
            txt, self.lineEdit_MS_S, self.lineEdit_HM_H, self.lineEdit_HM_M
        )

    def on_lineEdit_MS_S_edited(self, txt):
        on_lineEdit_edited(txt, self.btnStart, self.lineEdit_HM_H, self.lineEdit_HM_M)

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

    def draw_time(self, seconds_left: int):
        if self.time_hour_min:
            self.draw_hour_min(seconds_left)
            return
        if self.time_min_sec:
            self.draw_min_sec(seconds_left)
            return
        return

    def draw_hour_min(self, seconds_left: int):
        hour, min_sec = divmod(seconds_left, 3600)
        minutes, sec = divmod(min_sec, 60)
        self.lineEdit_HM_H.setText(f"{hour:02}")
        self.lineEdit_HM_M.setText(f"{minutes:02}")
        self.lblSec.setText(f": {sec:02}")

    def draw_min_sec(self, seconds_left: int):
        minutes, sec = divmod(seconds_left, 60)
        self.lineEdit_MS_M.setText(f"{minutes:02}")
        self.lineEdit_MS_S.setText(f"{sec:02}")

    def get_seconds_left(self) -> int:
        match self.time_field():
            case TimeField.MS:
                return num(self.lineEdit_MS_M) * 60 + num(self.lineEdit_MS_S)
            case TimeField.HM:
                return num(self.lineEdit_HM_H) * 3600 + num(self.lineEdit_HM_M) * 60
            case _:
                return 0

    def time_field(self) -> TimeField | None:
        if self.lineEdit_MS_M.text() or self.lineEdit_MS_S.text():
            self.time_min_sec = True
            return TimeField.MS
        if self.lineEdit_HM_H.text() or self.lineEdit_HM_M.text():
            self.time_hour_min = True
            return TimeField.HM
        return None

    def start(self) -> int:
        """Запуск приложения и отображение главного окна."""

        self.show()  # Показ формы
        return PyQt6.QtWidgets.QApplication.exec()  # Запуск основного цикла приложения


# Запуск приложения
if __name__ == "__main__":
    app = PyQt6.QtWidgets.QApplication(sys.argv)  # Создание экземпляра приложения
    timer_2_app = Timer2()  # Создание экземпляра таймера
    sys.exit(timer_2_app.start())  # Запуск таймера
