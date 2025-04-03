from typing import Callable

from PyQt6.QtCore import QTimer, QElapsedTimer


class PreciseTimer:
    """Точный таймер. Похож на Qtimer, но исправляет его неточности измерения времени"""

    def __init__(self, interval_ms: int, callback: Callable) -> None:
        """
        Инициализация точного таймера
        :param interval_ms: Интервал прерываний точного таймера.
        :param callback: Слот для прерываний точного таймера.
        """
        self.interval = interval_ms
        self.callback = callback
        self.elapsed = (
            QElapsedTimer()
        )  # Класс для точного измерения временных интервалов.
        self.timer = (
            QTimer()
        )  # Класс для выдачи сигналов через заданный интервал времени.
        self.timer.setSingleShot(True)  # Таймер будет выполняться только один раз.
        self.timer.setInterval(self.interval)
        self.timer.timeout.connect(
            self._on_timeout
        )  # Внутренний слот для обработки прерывания
        self.tick_count = 0  # Количество прерываний точного таймера

    def start(self):
        """Старт точного таймера"""
        self.elapsed.start()  # старт точного таймера для начала отсчёта интервала
        self.timer.start(0)  # Первый тик сразу

    def _on_timeout(self):
        """Обработчик окончания работы QTimer"""
        self.tick_count += 1
        now = self.elapsed.elapsed()  # Время от начала работы точного таймера
        expected_time = self.tick_count * self.interval
        drift = now - expected_time  # Погрешность работы QTimer

        # Вызов слота
        self.callback()

        # Следующий запуск QTimer с учётом накопленного дрифта
        next_delay = self.interval - drift
        next_delay = max(0, next_delay)  # чтобы не было отрицательного времени
        self.timer.start(next_delay)


if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication

    def on_precise_tick(now_ms, expected_ms, drift_ms):
        print(
            f"Тик #{pt.tick_count} | Реальное время: {now_ms} мс | Ожидалось: {expected_ms} мс | Дрифт: {drift_ms:+} мс"
        )

    app = QApplication(sys.argv)

    pt = PreciseTimer(1000, on_precise_tick)
    pt.start()

    sys.exit(app.exec())
