from typing import Callable
from precise_timer import PreciseTimer
from tunes import Tunes
from const import Const as C
import functions as f


class Clock:
    """
    Этот класс управляет отсчётом времени, отправляет уведомления и
    выполняет действия при завершении времени.

    Атрибуты:
        draw_time (callable): Функция для обновления отображения оставшегося времени.
                        Функция должна быть задана вызывающей программой
    """

    def __init__(self, seconds_left: int):
        """
        Инициализация таймера.

        Args:
            seconds_left (int): Начальное количество секунд для таймера.
        """
        self.seconds_left = seconds_left  # Значение времени таймера
        self.connections = dict()
        self.tunes = Tunes()

        # Создаём и запускаем объект, который будет отсчитывать интервалы времени
        self.timer = PreciseTimer(C.TIMER_INTERVAL, self.on_time_out)

    def on_time_out(self):
        """
        Обработчик события таймера, вызываемый каждую секунду.
        Отправляет уведомления о наступивших событиях.
        """

        self.seconds_left -= 1
        voice_interval = self.tunes.get_tune(C.TUNE_VOICE_INTERVAL)
        beep_interval = self.tunes.get_tune(C.TUNE_BEEP_INTERVAL)
        beep_period_in_final = self.tunes.get_tune(C.TUNE_BEEP_PERIOD_IN_FINAL)

        # Отображение оставшегося времени
        self.callback("draw_time", self.seconds_left)

        # Уведомление об окончании таймера
        if self.is_end_timer():
            self.callback("inform_done")

        # Уведомление об оставшемся времени
        if not self.seconds_left % voice_interval:
            self.callback("inform_voice", self.seconds_left)

        # Уведомление о скором завершении таймера
        if (
            self.seconds_left < beep_period_in_final
            and not self.seconds_left % beep_interval
        ):
            f.beep()

    def is_end_timer(self) -> bool:
        """
        Проверяет, истёк ли таймер.
        :return True если таймер завершился, False - если НЕ завершился
        """
        if self.seconds_left <= 0:
            # Завершаем выполнение программы
            return True
        return False

    def connect(self, name_callback: str, func: Callable):
        """
        Регистрация callback функции.
        Args:
            name_callback (str): - имя функции, используется в методе callback
            func (Callable): - ссылка на регистрируемую функцию
        """
        self.connections[name_callback] = func

    def callback(self, func_name: str, param: int | None = None) -> None:
        """
        Вызывает callback функцию. Ссылки на функции хранятся в словаре self.connections
        Args:
            func_name(str): имя вызываемой функции
            param: - параметр, передаваемый функции
        """
        try:
            if param is None:
                self.connections[func_name]()
            else:
                self.connections[func_name](param)
        except Exception as e:
            f.inform_fatal_error(
                C.TITLE_INTERNAL_ERROR, f"{C.TEXT_ERROR_CALLBACK} {func_name} \n{e}"
            )

    def start(self):
        """Старт точного таймера"""
        self.timer.start()
