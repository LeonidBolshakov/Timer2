import io
import sys
import threading

import pyttsx3  # type: ignore
from PyQt6.QtCore import QEventLoop, QTimer

sys.stdout = io.StringIO()
import pygame  # type: ignore

sys.stdout = sys.__stdout__

import functions as f
from const import Const as C
from signals import signals
from tunes import TunesSettings


class InformTime:
    """Голосовое и звуковое информирование пользователя."""

    def __init__(self, settings: TunesSettings) -> None:
        self.settings = settings
        self.voice_lock = threading.Lock()

    def inform_voice(self, seconds: int) -> None:
        """
        Запускает голосовое сообщение в отдельном потоке.

        Для каждого сообщения создаётся отдельный pyttsx3 engine.
        Это устойчивее, чем многократно использовать один общий engine.
        """
        thread = threading.Thread(
            target=self._voice_once,
            args=(seconds,),
            daemon=True,
        )
        thread.start()

    def _voice_once(self, seconds: int) -> None:
        """
        Однократно произносит остаток времени.

        Если предыдущее голосовое сообщение ещё не закончилось,
        новое сообщение пропускается.
        """
        if not self.voice_lock.acquire(blocking=False):
            return

        voice_engine = None

        try:
            text = f.time_to_text(seconds)

            voice_engine = pyttsx3.init()
            voice_engine.say(text)
            voice_engine.runAndWait()

        except Exception as err:
            print(f"Ошибка голосового сообщения: {type(err).__name__}: {err}")

        finally:
            if voice_engine is not None:
                try:
                    # noinspection PyUnresolvedReferences
                    voice_engine.stop()
                except Exception:
                    pass

            self.voice_lock.release()

    def inform_done(self) -> None:
        file_melody = self.settings.model.file_melody

        if not file_melody:
            f.inform_fatal_error_and_quit(C.TITLE_NO_MELODY, C.TEXT_NO_MELODY)

        try:
            pygame.init()
            pygame.mixer.init()
            pygame.mixer.music.load(file_melody)
            pygame.mixer.music.play()

        except Exception as err:
            f.inform_fatal_error_and_quit(
                C.TITLE_INTERNAL_ERROR,
                f"{C.TEXT_NO_PLAY_MELODY}\n{err}",
            )

        self.control_end_of_melody()
        f.go_quit()

    @staticmethod
    def control_end_of_melody() -> None:
        timer = QTimer()
        timer.timeout.connect(f.check_music_finished)
        timer.start(C.END_CHECK_INTERVAL)

        loop = QEventLoop()
        signals.melody_finished.connect(loop.quit)
        loop.exec()
