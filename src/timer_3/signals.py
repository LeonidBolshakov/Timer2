"""Общие Qt-сигналы, не принадлежащие отдельному окну."""

from PyQt6.QtCore import QObject, pyqtSignal


class Signals(QObject):
    """Контейнер межкомпонентных сигналов приложения."""
    melody_finished = (
        pyqtSignal()
    )  # Сигнал о завершении проигрывания мелодии, завершающей таймер


signals = Signals()
