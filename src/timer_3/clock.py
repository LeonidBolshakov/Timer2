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
        self.seconds_left -= 1

        self.callback("a_second_passed", self.seconds_left)

        if self.is_end_timer():
            self.callback("end_of_timer")
            return

    def is_end_timer(self) -> bool:
        return self.seconds_left <= 0

    def connect(self, name_callback: str, func: Callable[..., None]) -> None:
        self.connections[name_callback] = func

    def callback(self, func_name: str, param: int | None = None) -> None:
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
        self.timer.start()

    def stop(self) -> None:
        self.timer.stop()

    def restart(self, seconds_left: int) -> None:
        self.stop()
        self.seconds_left = seconds_left
        self.timer.restart()
