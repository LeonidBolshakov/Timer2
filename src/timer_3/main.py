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
)
from PyQt6.QtWidgets import (
    QLabel,
    QLineEdit,
    QPushButton,
)


from .const import Const as C
from . import functions as f
from .ui_configurator import Timer3UiConfigurator
from .timer_controller import Timer3Controller


class Timer_3(QMainWindow):
    """Главное окно приложения."""

    btnQuit: QPushButton
    btnStart: QPushButton
    btnTunes: QPushButton
    lblSec: QLabel
    lineEdit_HM_H: QLineEdit
    lineEdit_HM_M: QLineEdit
    lineEdit_MS_M: QLineEdit
    lineEdit_MS_S: QLineEdit

    def __init__(self) -> None:
        super().__init__(None)
        uic.loadUi(str(f.resource_path(C.TIMER_3_UI)), self)

        controller = Timer3Controller(self)
        Timer3UiConfigurator(self, controller)

    def start(self) -> int:
        self.show()
        # noinspection PyArgumentList
        return QApplication.exec()


def main() -> None:
    def on_app_exit() -> None:
        with suppress(pygame.error):
            pygame.mixer.quit()

    app = QApplication(sys.argv)
    app.aboutToQuit.connect(on_app_exit)

    timer_3_app = Timer_3()
    sys.exit(timer_3_app.start())


if __name__ == "__main__":
    main()
