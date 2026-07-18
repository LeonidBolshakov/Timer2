"""Событийный обратный отсчёт поверх точного таймера."""

import traceback
from collections.abc import Callable

from .precise_timer import PreciseTimer
from .const import Const as C
from . import functions as f


class Clock:
    """Управляет отсчётом времени и событиями таймера."""

    def __init__(self) -> None:
        self.seconds_left = 0
        self.connections: dict[str, Callable[..., None]] = {}
        self.timer = PreciseTimer(C.TIMER_INTERVAL, self.on_time_out)

    def on_time_out(self) -> None:
        """Обработать секундный тик и уведомить подписчиков.

        Сначала передаёт новое значение остатка времени, затем при достижении нуля
        вызывает обработчик завершения.
        """
        self.seconds_left -= 1

        self.callback("a_second_passed", self.seconds_left)

        if self.is_end_timer():
            self.callback("end_of_timer")
            return

    def is_end_timer(self) -> bool:
        """Вернуть True, если отсчёт достиг нуля или прошёл его."""
        return self.seconds_left <= 0

    def connect(self, name_callback: str, func: Callable[..., None]) -> None:
        """Зарегистрировать callback под именем события Clock."""
        self.connections[name_callback] = func

    def callback(self, func_name: str, param: int | None = None) -> None:
        """Вызвать именованный callback с необязательным целым аргументом.

        Отсутствующий обработчик или исключение в нём считаются нарушением внутреннего
        контракта и приводят к завершению приложения.
        """
        try:
            callback = self.connections[func_name]
            if param is None:
                callback()
            else:
                callback(param)
        except Exception as err:
            traceback.print_exc()
            f.inform_fatal_error_and_quit(
                C.TITLE_INTERNAL_ERROR,
                f"{C.TEXT_ERROR_CALLBACK} {func_name}\n{err}",
            )

    def start(self) -> None:
        """Запустить отсчёт с текущим значением seconds_left."""
        self.timer.start()

    def stop(self) -> None:
        """Остановить генерацию тиков, сохранив остаток времени."""
        self.timer.stop()

    def restart(self, seconds_left: int) -> None:
        """Перезапустить отсчёт с новым остатком времени.

        Сбрасывает временную базу PreciseTimer, чтобы новый интервал не наследовал дрейф
        предыдущего.
        """
        self.stop()
        self.seconds_left = seconds_left
        self.timer.restart()
