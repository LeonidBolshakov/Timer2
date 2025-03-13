from typing import Callable
from inform import InformTime
from precise_timer import PreciseTimer
from tunes import Tunes
from const import Const as C
from functions import beep


class Clock:
    """
    Этот класс управляет отсчётом времени, отправляет уведомления и
    выполняет действия при завершении времени.

    Атрибуты:
        draw_time (callable): Функция для обновления отображения оставшегося времени.
                        Функция должна быть задана вызывающей программой
    """

    def __init__(self, seconds_left: int, draw_time: Callable[[int], None]):
        """
        Инициализация таймера.

        Args:
            seconds_left (int): Начальное количество секунд для таймера.
            draw_time (Callable[[int], None]) - callback для обновления отображения оставшегося времени
        """
        self.seconds_left = seconds_left  # Значение времени таймера
        self.draw_time = draw_time
        self.tunes = Tunes()

        # Создаём и запускаем объект, который будет отсчитывать интервалы времени
        self.timer = PreciseTimer(C.TIMER_INTERVAL, self.on_time_out)

    def on_time_out(self):
        """
        Обработчик события таймера, вызываемый каждую секунду.
        Отправляет уведомления о наступивших событиях.
        """

        self.seconds_left -= 1
        inform_time = InformTime()
        voice_interval = self.tunes.get_tune(C.TUNE_VOICE_INTERVAL)
        beep_interval = self.tunes.get_tune(C.TUNE_BEEP_INTERVAL)
        beep_period_in_final = self.tunes.get_tune(C.TUNE_BEEP_PERIOD_IN_FINAL)

        # Отображение оставшегося времени
        self.draw_time(self.seconds_left)

        # Уведомление об окончании таймера
        if self.is_end_timer():
            inform_time.inform_done()

        # Уведомление об оставшемся времени
        if not self.seconds_left % voice_interval:
            inform_time.inform_voice(self.seconds_left)

        # Уведомление о скором завершении таймера
        if (
            self.seconds_left < beep_period_in_final
            and not self.seconds_left % beep_interval
        ):
            beep()

    def is_end_timer(self) -> bool:
        """
        Проверяет, истёк ли таймер.
        :return True если таймер завершился, False - если НЕ завершился
        """
        if self.seconds_left <= 0:
            # Завершаем выполнение программы
            return True
        return False

    def start(self):
        self.timer.start()
