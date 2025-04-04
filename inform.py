import threading  # Для работы с потоками
import sys
import io

import pyttsx3  # type: ignore # Для синтеза речи
from PyQt6.QtCore import QEventLoop, QTimer

sys.stdout = io.StringIO()  # Заглушает вывод рекламы
import pygame  # type: ignore

sys.stdout = sys.__stdout__

import functions as f  # Импорт пользовательских функций
from const import Const as C
from tunes import Tunes
from signals import signals


class InformTime:
    """
    Класс для голосового информирования об оставшемся времени.

    Методы:
        inform_voice(seconds: int): Преобразует оставшееся время в текст и воспроизводит его голосом
        inform_time_left(seconds: int): Информирует пользователя голосом через заданные интервалы времени.
    """

    def __init__(self) -> None:
        """
        Инициализация класса InformTimeLeft.
        Создаёт экземпляр движка синтеза речи (pyttsx3).
        """
        super().__init__()
        self.tunes = Tunes()

        try:
            self.voice_engine = pyttsx3.init()  # Инициализация синтезатора речи
        except Exception as e:
            f.inform_fatal_error(C.TITLE_ERROR_SPEACH, f"{C.TEXT_NO_INIT_SPEECH}\n{e}")

    def voice(self, seconds: int) -> None:
        """
        Преобразует количество оставшихся секунд в текст и воспроизводит его голосом.

        Args:
            seconds (int): Оставшееся время в секундах.
        """
        self.voice_engine.say(f.time_to_text(seconds))  # Преобразуем секунды в текст
        try:
            self.voice_engine.runAndWait()  # Запускаем воспроизведение речи
        except RuntimeError:
            pass  # Игнорируем вывод нового сообщения до окончания вывода предыдущего
        return

    def inform_voice(self, seconds: int) -> None:
        """
        Информирует голосом об оставшемся времени.
        Запускает воспроизведение речи в отдельном потоке, чтобы не блокировать выполнение программы.

        Args:
            seconds (int): Оставшееся время в секундах.
        """

        # Создаём и запускаем отдельный поток для голосового оповещения
        thread = threading.Thread(target=self.voice, args=(seconds,), daemon=True)
        thread.start()
        return

    def inform_done(self) -> None:
        """
        Воспроизводит мелодию, информирующую о завершении работы таймера.
        """
        file_melody = self.tunes.get_tune(C.TUNE_FILE_MELODY)
        if file_melody:
            try:
                pygame.init()
                pygame.mixer.init()
                pygame.mixer.music.load(file_melody)
                pygame.mixer.music.play()  # Обращение к pygame.mixer для проигрывания мелодии
            except Exception as e:
                f.inform_fatal_error(
                    C.TITLE_INTERNAL_ERROR, f"{C.TEXT_NO_PLAY_MELODY}\n{e}"
                )
            self.control_end_of_melody()
            f.go_quit()
        else:
            f.inform_fatal_error(C.TITLE_NO_MELODY, C.TEXT_NO_MELODY)

    @staticmethod
    def control_end_of_melody() -> None:
        """Ожидает получения сигнала завершения проигрывания мелодии.
        При получении сигнала прекращает ожидание"""
        timer = QTimer()
        timer.timeout.connect(f.check_music_finished)
        timer.start(C.END_CHECK_INTERVAL)
        loop = QEventLoop()
        signals.melody_finished.connect(loop.quit)
        loop.exec()  # Ожидание окончания проигрывания
