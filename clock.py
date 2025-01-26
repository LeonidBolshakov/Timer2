from PyQt6.QtCore import QTimer

import inform
from functions import on_quit
from inform import InformTimeLeft


class Clock:
    """
    Основной класс таймера.
    Управляет отсчётом времени и отправкой уведомлений.
    """

    def __init__(self, seconds_left: int):
        self.seconds_left = seconds_left  # Стартовое время таймера
        self.draw_time = None  # Функция для перерисовки времени окончания таймера

        self.timer = QTimer()
        self.start()

    def on_time_out(self):
        self.seconds_left -= 1
        # Отрисовка времени на главном меню.
        self.draw_time(self.seconds_left)

        # Контроль истечения времени таймера
        self.check_end_timer()

        # Выдача голосового сообщения об оставшемся времени.
        InformTimeLeft().inform_time_left(self.seconds_left)

        # Посекундные сигналы о завершении работы таймера.
        inform.inform_signal(self.seconds_left)

    def check_end_timer(self):
        if self.seconds_left <= 0:
            # Информирование о завершении работы таймера.
            inform.inform_done()

            # Завершение работы программы
            on_quit()

    def start(self):
        # noinspection PyUnresolvedReferences
        self.timer.timeout.connect(self.on_time_out)
        self.timer.start(1000)  # Запускаем таймер с интервалом 1000 мс (1 секунда)
