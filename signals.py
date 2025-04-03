from PyQt6.QtCore import QObject, pyqtSignal


class Signals(QObject):

    melody_finished = (
        pyqtSignal()
    )  # Сигнал о завершении проигрывания мелодии, завершающей таймер


signals = Signals()
