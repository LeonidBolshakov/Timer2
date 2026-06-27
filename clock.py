from collections.abc import Callable

from precise_timer import PreciseTimer
from const import Const as C
import functions as f
from tunes import TunesSettings


class Clock:
    """Управляет отсчётом времени и событиями таймера."""

    def __init__(self, seconds_left: int, settings: TunesSettings) -> None:
        self.seconds_left = seconds_left
        self.settings = settings
        self.connections: dict[str, Callable[..., None]] = {}
        self.timer = PreciseTimer(C.TIMER_INTERVAL, self.on_time_out)

    def on_time_out(self) -> None:
        self.seconds_left -= 1

        self.callback("draw_time", self.seconds_left)

        if self.is_end_timer():
            self.callback("inform_done")
            return

        model = self.settings.model

        if self.seconds_left % model.voice_interval == 0:
            self.callback("inform_voice", self.seconds_left)

        if (
            self.seconds_left < model.beep_period_in_final
            and self.seconds_left % model.beep_interval == 0
        ):
            f.beep()

    def is_end_timer(self) -> bool:
        return self.seconds_left <= 0

    def connect(self, name_callback: str, func: Callable[..., None]) -> None:
        if name_callback in self.connections:
            f.inform_fatal_error_and_quit(
                C.TITLE_INTERNAL_ERROR,
                f"{C.TEXT_ERROR_NAME_CALLBACK} {name_callback}",
            )
        self.connections[name_callback] = func

    def callback(self, func_name: str, param: int | None = None) -> None:
        try:
            callback = self.connections[func_name]
            if param is None:
                callback()
            else:
                callback(param)
        except Exception as err:
            f.inform_fatal_error_and_quit(
                C.TITLE_INTERNAL_ERROR,
                f"{C.TEXT_ERROR_CALLBACK} {func_name}\n{err}",
            )

    def start(self) -> None:
        self.timer.start()
