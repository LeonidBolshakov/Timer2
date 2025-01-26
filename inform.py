import threading

import pyttsx3
from PyQt6.QtWidgets import QApplication
from playsound import playsound

# pip install --upgrade setuptools wheel
# pip install playsound
# pip install playsound==1.2.2

import functions as f


class InformTimeLeft:
    """
    Класс для голосового информирования об оставшемся времени.
    Использует отдельный поток для воспроизведения звука.
    """

    def __init__(self):
        self.voice_engine = pyttsx3.init()

    def voice(self, seconds: int):
        self.voice_engine.say(f.time_to_text(seconds))
        self.voice_engine.runAndWait()

    def inform_time_left(self, seconds: int):
        if seconds % 7:
            return

        thread = threading.Thread(target=self.voice, args=(seconds,))
        thread.start()
        return


def inform_done():
    playsound("example.mp3")


def inform_signal(seconds):
    if seconds < 10 and seconds % 2:
        QApplication.beep()
