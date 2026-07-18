"""Главное окно и точка входа desktop-приложения Timer 3."""

import io
import sys
from contextlib import suppress

sys.stdout = io.StringIO()
import pygame  # type: ignore

sys.stdout = sys.__stdout__

from PyQt6 import uic  # type: ignore
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QLineEdit,
    QPushButton,
    QTabWidget,
    QWidget,
    QCheckBox,
    QSpinBox,
)


from .const import Const as C
from . import functions as f
from .timer_configurator import Timer3UiConfigurator
from .timer_controller import Timer3Controller


class Timer_3(QMainWindow):
    """Главное окно приложения."""

    btnQuit: QPushButton
    btnStart: QPushButton
    btnTunes: QPushButton
    checkboxEndlessly: QCheckBox
    lblSec: QLabel
    lineEditCurrentInterval: QLineEdit
    lineEditCycleIntervals: QLineEdit
    lineEditIntervalDuration: QLineEdit
    lineEditLeft: QLineEdit
    lineEdit_HM_H: QLineEdit
    lineEdit_HM_M: QLineEdit
    lineEdit_MS_M: QLineEdit
    lineEdit_MS_S: QLineEdit
    spinBoxCycleRepetitions: QSpinBox
    tabCycle: QWidget
    tabOrdinary: QWidget
    tabWidgetSetTime: QTabWidget

    controller: Timer3Controller
    ui_configurator: Timer3UiConfigurator

    def __init__(self) -> None:
        super().__init__(None)
        uic.loadUi(str(f.resource_path(C.TIMER_3_UI)), self)

        self.controller = Timer3Controller(self)
        self.ui_configurator = Timer3UiConfigurator(
            self,
            self.controller,
        )

    def start(self) -> int:
        """Показать главное окно и запустить цикл событий Qt."""
        self.show()
        # noinspection PyArgumentList
        return QApplication.exec()


def main() -> None:
    """Создать QApplication, главное окно и освободить mixer при выходе."""
    def on_app_exit() -> None:
        with suppress(pygame.error):
            pygame.mixer.quit()

    app = QApplication(sys.argv)
    app.aboutToQuit.connect(on_app_exit)

    timer_3_app = Timer_3()
    sys.exit(timer_3_app.start())


if __name__ == "__main__":
    main()
