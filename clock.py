from PyQt6.QtCore import QTimer
from functions import on_quit


class Clock:
    def __init__(self, seconds_left: int):
        self.seconds_left = seconds_left
        self.draw_time = self.does_nothing  # Перерисовка времени
        self.inform_time_left = self.does_nothing
        self.inform_signal = self.does_nothing
        self.inform_done = self.does_nothing  # Информирование об окончании таймера

        self.timer = QTimer()
        self.start()

    def on_time_out(self):
        self.seconds_left -= 1
        # Отрисовка времени на главном меню.
        self.draw_time(self.seconds_left)

        # Контроль истечения времени таймера
        self.check_end_timer()

        # Выдача сообщения об оставшемся времени.
        self.inform_time_left(self.seconds_left)

        # Посекундные сигналы о завершении работы таймера.
        self.inform_signal(self.seconds_left)

    @staticmethod
    def does_nothing(seconds_left: int):
        return

    def check_end_timer(self):
        if self.seconds_left <= 0:
            # Сообщение о завершении работы таймера.
            self.inform_done(self.seconds_left)

            # Завершение работы программы
            on_quit()

    def start(self):
        self.timer.timeout.connect(self.on_time_out)
        self.timer.start(1000)  # Запускаем таймер с интервалом 1000 мс (1 секунда)
