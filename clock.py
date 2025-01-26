from PyQt6.QtCore import QTimer

import inform
from functions import on_quit
from inform import InformTimeLeft
from const import Const as c


class Clock:
    """
    Основной класс таймера.
    Этот класс управляет отсчётом времени, отправляет уведомления и
    выполняет действия при завершении времени.

    Атрибуты:
        seconds_left (int): Количество секунд, оставшихся до завершения таймера.
        draw_time (callable): Функция для обновления отображения оставшегося времени.
        timer (QTimer): Таймер, который запускает события с заданным интервалом.

    Методы:
        on_time_out(): Обработчик события таймера, вызывается каждую секунду.
        check_end_timer(): Проверяет, истёк ли таймер, и выполняет действия при завершении.
        start(): Запускает таймер с интервалом в 1 секунду.
    """

    def __init__(self, seconds_left: int):
        """
        Инициализация таймера.

        Args:
            seconds_left (int): Начальное количество секунд для таймера.
        """
        self.seconds_left = seconds_left  # Стартовое значение времени таймера
        self.draw_time = None  # Функция для обновления отображения оставшегося времени

        # Создаём объект QTimer, который будет отсчитывать интервал времени
        self.timer = QTimer()

        # Запускаем таймер сразу после инициализации
        self.start()

    def on_time_out(self):
        """
        Обработчик события таймера, вызываемый каждую секунду.
        Уменьшает количество оставшихся секунд, обновляет отображение времени,
        отправляет уведомления и проверяет завершение таймера.
        """
        # Уменьшаем количество оставшихся секунд на 1
        self.seconds_left -= 1

        # Вызываем функцию для обновления отображения оставшегося времени
        if self.draw_time is not None:
            self.draw_time(self.seconds_left)

        # Проверяем, истёк ли таймер
        self.check_end_timer()

        # Отправляем голосовое уведомление об оставшемся времени
        InformTimeLeft().inform_time_left(self.seconds_left)

        # Отправляем сигналы обратной связи (например, звуковые сигналы)
        inform.inform_signal(self.seconds_left)

    def check_end_timer(self):
        """
        Проверяет, истёк ли таймер.
        Если время закончилось, отправляет уведомление и завершает работу программы.
        """
        if self.seconds_left <= 0:
            # Отправляем уведомление о завершении таймера
            inform.inform_done()

            # Завершаем выполнение программы
            on_quit()

    def start(self):
        """
        Запускает таймер с интервалом в c.TIMER_INTERVAL миллисекунд.
        """
        # Подключаем обработчик события (on_time_out) к сигналу timeout от QTimer
        # noinspection PyUnresolvedReferences
        self.timer.timeout.connect(self.on_time_out)

        # Запускаем таймер. Интервал установлен на c.TIMER_INTERVAL миллисекунд
        self.timer.start(c.TIMER_INTERVAL)
