from typing import Callable

import functions as f
from inform import InformTimeLeft
from const import Const as C
from tunes import Tunes
from precise_timer import PreciseTimer


class Clock:
    """
    Класс работы со временем.
    Этот класс управляет обратным отсчётом времени, и инициирует отправку уведомлений.

    Атрибуты:
        draw_time (callable): Callback для посекундного отображения оставшегося времени.
                                Необходимо задать в вызывающем объекте.
    """

    def __init__(self, main_object: object, seconds_left: int):
        """
        Инициализация таймера.
        Args:
            main_object (object): Вызывающий объект.
            seconds_left (int): Начальное количество секунд таймера.
        """
        self.main_object = main_object
        self.tunes = Tunes()
        self.inform_time_left = InformTimeLeft()
        self.seconds_left = seconds_left  # Значение времени таймера

        self.draw_time: Callable[[int], None] | None = (
            None  # CallBack для обновления отображения оставшегося времени. Необходимо задать в вызывающем объекте.
        )

        # Создаём объект, который будет отсчитывать время.
        self.timer = PreciseTimer(C.TIMER_INTERVAL, self.on_time_out)
        self.timer.start()  # Запускаем таймер

    def on_time_out(self) -> None:
        """
        Обработчик события таймера, вызываемый каждую секунду.
        Уменьшает количество оставшихся секунд, проверяет завершение таймера, обновляет отображение времени,
        и отправляет уведомления.
        """
        self.seconds_left -= 1

        # Считываем переменные из настроек
        voice_interval = self.tunes.get_tune(C.TUNE_VOICE_INTERVAL)
        beep_interval = self.tunes.get_tune(C.TUNE_BEEP_INTERVAL)
        beep_period_in_final = self.tunes.get_tune(C.TUNE_BEEP_PERIOD_IN_FINAL)

        # Обновляем отображение оставшегося времени
        if self.draw_time is not None:
            self.draw_time(self.seconds_left)

        # Проигрываем мелодию при завершении работы
        if self.seconds_left <= 0:
            self.inform_time_left.inform_done()
            f.on_quit()

        # Отправляем голосовое уведомление об оставшемся времени
        if not self.seconds_left % voice_interval:
            self.inform_time_left.inform_voice(self.seconds_left)

        # Отправляем звуковые сигналы если оставшиеся секунды кратны TUNE_VOICE_INTERVAL.
        if self.seconds_left < beep_period_in_final:
            if not self.seconds_left % beep_interval:
                f.beep()
