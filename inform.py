import threading  # Для работы с потоками
import pyttsx3  # Для синтеза речи
from PyQt6.QtWidgets import QApplication  # Для работы с графическим интерфейсом
from playsound import playsound  # Для воспроизведения звуков

# pip install --upgrade setuptools wheel
# pip install playsound
# pip install playsound==1.2.2

import functions as f  # Импорт пользовательских функций
from const import Const as c


class InformTimeLeft:
    """
    Класс для голосового информирования об оставшемся времени.

    Атрибуты:
        voice_engine (pyttsx3.Engine): Движок синтеза речи для воспроизведения текста вслух.

    Методы:
        voice(seconds: int): Преобразует оставшееся время в текст и воспроизводит его голосом.
        inform_time_left(seconds: int): Информирует пользователя голосом через заданные интервалы времени.
    """

    def __init__(self):
        """
        Инициализация класса InformTimeLeft.
        Создаёт экземпляр движка синтеза речи (pyttsx3).
        """
        self.voice_engine = pyttsx3.init()  # Инициализация синтезатора речи

    def voice(self, seconds: int):
        """
        Преобразует количество оставшихся секунд в текст и воспроизводит его голосом.

        Args:
            seconds (int): Оставшееся время в секундах.
        """
        self.voice_engine.say(
            f.time_to_text(seconds)
        )  # Преобразуем секунды в текст и передаём синтезатору речи
        self.voice_engine.runAndWait()  # Запускаем воспроизведение речи

    def inform_time_left(self, seconds: int):
        """
        Информирует голосом об оставшемся времени через определённые интервалы (каждые 7 секунд).
        Запускает воспроизведение речи в отдельном потоке, чтобы не блокировать выполнение программы.

        Args:
            seconds (int): Оставшееся время в секундах.
        """
        # Если секунды не кратны c.VOICE_MESSAGE_INTERVAL_SECONDS, ничего не делаем
        if seconds % c.VOICE_MESSAGE_INTERVAL_SECONDS:
            return

        # Создаём и запускаем отдельный поток для голосового оповещения
        thread = threading.Thread(target=self.voice, args=(seconds,))
        thread.start()
        return


def inform_done():
    """
    Воспроизводит звуковой сигнал, информирующий о завершении работы таймера.
    Использует файл `example.mp3` для воспроизведения.
    """
    playsound(c.FILE_SOUND)  # Воспроизводим файл звука


def inform_signal(seconds):
    """
    Отправляет звуковой сигнал, если до завершения таймера осталось менее 10 секунд
    и текущее количество секунд нечётное.

    Args:
        seconds (int): Оставшееся время в секундах.
    """
    # Если таймер подходит к концу, выдаём короткие предупреждения
    if seconds < c.FINAL_BEEP_SECONDS:
        if seconds % c.BEEP_MESSAGE_INTERVAL_SECONDS:
            return
        beep()  # Воспроизводим звуковой сигнал


def beep():
    """
    Воспроизводит короткий звуковой сигнал (системный звуковой сигнал приложения).
    """
    QApplication.beep()  # Используем стандартный метод для воспроизведения системного сигнала
