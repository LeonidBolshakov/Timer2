import sys
from enum import Enum
from functools import lru_cache

import PyQt6
from PyQt6.QtWidgets import QMainWindow, QLineEdit, QPushButton, QLabel, QApplication
from PyQt6 import uic
from PyQt6.QtGui import QRegularExpressionValidator
from PyQt6.QtCore import QRegularExpression

import inform  # Модуль для работы с уведомлениями (например, звуковые сигналы)
from clock import Clock  # Модуль для управления таймером
import functions as f  # Вспомогательные функции


class TimeField(Enum):
    """
    Перечисление для указания режима ввода времени:
    HM: Часы и минуты
    MS: Минуты и секунды
    """

    HM = 1
    MS = 2


class Timer2(QMainWindow):
    """
    Главное окно приложения.
    Обеспечивает пользовательский интерфейс и обработку действий пользователя.
    """

    # Компоненты пользовательского интерфейса, задаются в Qt Designer
    btnQuit: QPushButton  # Кнопка "Выход"
    btnStart: QPushButton  # Кнопка "Старт"
    btnTunes: QPushButton  # Кнопка для настройки
    lblSec: QLabel  # Метка для отображения секунд при работе в режиме Часы: Минуты
    lineEdit_HM_H: QLineEdit  # Поле для ввода часов
    lineEdit_HM_M: QLineEdit  # Поле для ввода минут (режим ЧЧ:ММ)
    lineEdit_MS_M: QLineEdit  # Поле для ввода минут (режим ММ:СС)
    lineEdit_MS_S: QLineEdit  # Поле для ввода секунд

    def __init__(self):
        """
        Конструктор для инициализации основного окна.
        Устанавливает валидаторы, подключает события и задает начальные параметры.
        """
        super().__init__()
        uic.loadUi("timer_2.ui", self)  # Загрузка интерфейса из файла .ui

        self.clock = None  # Атрибут для хранения объекта Clock

        # Создание валидаторов для ввода времени
        self.validator_hour = QRegularExpressionValidator()
        self.validator_min_sec = QRegularExpressionValidator()
        self.set_validators()  # Установка правил валидации
        self.assign_validators()  # Назначение валидаторов полям ввода

        self.connect_signals()  # Подключение сигналов к обработчикам событий
        self.set_bolds()  # Установка жирного шрифта для полей ввода
        self.init_vars()  # Инициализация переменных и начальных значений

    def set_validators(self):
        """
        Устанавливает регулярные выражения для валидации ввода времени.
        """
        # Валидация для часов (0-23, пустое поле допустимо)
        self.validator_hour = QRegularExpressionValidator(
            QRegularExpression(r"[0-9]|1[0-9]|2[0-3]")
        )
        # Валидация для минут и секунд (0-59, пустое поле допустимо)
        self.validator_min_sec = QRegularExpressionValidator(
            QRegularExpression(r"[0-5][0-9]")
        )

    def assign_validators(self):
        """
        Назначает валидаторы соответствующим полям ввода.
        """
        self.lineEdit_HM_H.setValidator(self.validator_hour)
        self.lineEdit_HM_M.setValidator(self.validator_min_sec)
        self.lineEdit_MS_M.setValidator(self.validator_min_sec)
        self.lineEdit_MS_S.setValidator(self.validator_min_sec)

    def connect_signals(self):
        """
        Подключает сигналы компонентов пользовательского интерфейса к обработчикам событий.
        """
        self.btnQuit.clicked.connect(f.on_quit)  # Кнопка "Выход"
        self.btnStart.clicked.connect(self.on_btnStart_click)  # Кнопка "Старт"
        self.btnTunes.clicked.connect(self.on_btnTunes_click)  # Кнопка "Настройки"
        # Редактирование полей ввода времени
        self.lineEdit_HM_H.textEdited.connect(self.on_lineEdit_HM_H_edited)
        self.lineEdit_HM_M.textEdited.connect(self.on_lineEdit_HM_M_edited)
        self.lineEdit_MS_M.textEdited.connect(self.on_lineEdit_MS_M_edited)
        self.lineEdit_MS_S.textEdited.connect(self.on_lineEdit_MS_S_edited)

    def set_bolds(self):
        """
        Устанавливает жирный шрифт для всех полей ввода времени.
        """
        for line_edit in (
                self.lineEdit_HM_H,
                self.lineEdit_HM_M,
                self.lineEdit_MS_M,
                self.lineEdit_MS_S,
        ):
            font = line_edit.font()
            font.setBold(True)
            line_edit.setFont(font)

    def init_vars(self):
        """
        Инициализирует начальные значения интерфейса и переменных.
        """
        self.lblSec.setText("")  # Очищает метку для секунд
        self.lineEdit_MS_M.setFocus()  # Устанавливает фокус на поле ввода минут в режиме ММ:СС

    def on_btnStart_click(self):
        """
        Обработчик нажатия кнопки "Старт".
        Создает объект Clock и запускает таймер, если указано время.
        """
        # Проверка, что таймер еще не создан и время больше нуля
        if self.clock is None and self.get_seconds_left() != 0:
            self.clock = Clock(self.get_seconds_left())  # Создание объекта Clock
            self.clock.draw_time = (
                self.draw_time
            )  # Установка функции обновления времени

        inform.beep()  # Проигрывание звукового сигнала

    def on_btnTunes_click(self):
        """
        Обработчик нажатия кнопки "Настройки".
        Пока не реализован.
        """
        pass

    def on_lineEdit_HM_H_edited(self, txt: str):
        """
        Обработчик изменения текста в поле ввода часов.
        """
        self.on_lineEdit_edited(txt, self.lineEdit_HM_M)

    def on_lineEdit_HM_M_edited(self, txt: str):
        """
        Обработчик изменения текста в поле ввода минут (ЧЧ:ММ).
        """
        self.on_lineEdit_edited(txt, self.btnStart)

    def on_lineEdit_MS_M_edited(self, txt: str):
        """
        Обработчик изменения текста в поле ввода минут (ММ:СС).
        """
        self.on_lineEdit_edited(txt, self.lineEdit_MS_S)

    def on_lineEdit_MS_S_edited(self, txt: str):
        """
        Обработчик изменения текста в поле ввода секунд.
        """
        self.on_lineEdit_edited(txt, self.btnStart)

    def draw_time(self, seconds_left: int):
        """
        Обновляет отображение времени на экране.

        Args:
            seconds_left (int): Оставшееся количество секунд.

        Отображает время в формате ЧЧ:ММ или ММ:СС в зависимости от выбранного режима.
        """
        hour, minutes, sec = f.hour_minutes_sec(seconds_left)

        match self.active_time_field():
            case TimeField.MS:
                self.draw_min_sec(minutes, sec)
            case TimeField.HM:
                self.draw_hour_min(hour, minutes, sec)

        if seconds_left <= 0:
            QApplication.processEvents()  # Обновление интерфейса

    def draw_hour_min(self, hour: int, minutes: int, sec: int):
        """
        Отображает оставшееся время в формате ЧЧ:ММ.
        """
        self.lineEdit_HM_H.setText(f"{hour:02}")
        self.lineEdit_HM_M.setText(f"{minutes:02}")
        self.lblSec.setText(f": {sec:02}")

    def draw_min_sec(self, minutes: int, sec: int):
        """
        Отображает оставшееся время в формате ММ:СС.
        """
        self.lineEdit_MS_M.setText(f"{minutes:02}")
        self.lineEdit_MS_S.setText(f"{sec:02}")

    def get_seconds_left(self) -> int:
        """
        Вычисляет общее оставшееся время в секундах в зависимости от режима.

        Returns:
            int: Общее количество оставшихся секунд.
        """
        match self.active_time_field():
            case TimeField.MS:
                return f.num(self.lineEdit_MS_M) * 60 + f.num(self.lineEdit_MS_S)
            case TimeField.HM:
                return f.num(self.lineEdit_HM_H) * 3600 + f.num(self.lineEdit_HM_M) * 60
            case _:
                return 0

    @lru_cache
    def active_time_field(self) -> TimeField | None:
        """
        Определяет активное поле ввода времени (ЧЧ:ММ или ММ:СС).

        Returns:
            TimeField | None: Активное поле ввода или None.
        """
        if self.lineEdit_MS_M.text() or self.lineEdit_MS_S.text():
            return TimeField.MS
        if self.lineEdit_HM_H.text() or self.lineEdit_HM_M.text():
            return TimeField.HM
        return None

    def on_lineEdit_edited(self, txt: str, focus):
        """
        Обработчик изменения текста в любом поле ввода.
        Обновляет стили полей ввода в зависимости от активного режима и устанавливает фокус.

        Args:
            txt (str): Введенный текст.
            focus: Поле ввода, на которое нужно переместить фокус.
        """
        # Определение стилей для активного и неактивного состояния полей
        active_style = (
            "QLineEdit { background-color: #f5ffb3; }"  # Желтый фон для активных полей
        )
        inactive_style = (
            "QLineEdit { background-color: white; }"  # Белый фон для неактивных полей
        )

        # Определяем активное поле ввода на основе текущего режима
        match self.active_time_field():
            case TimeField.HM:  # Режим ЧЧ:ММ
                # Очистка полей для секунд и минут (ММ:СС)
                self.lineEdit_MS_M.clear()
                self.lineEdit_MS_S.clear()

                # Применение активного стиля к полям ЧЧ:ММ
                self.lineEdit_HM_H.setStyleSheet(active_style)
                self.lineEdit_HM_M.setStyleSheet(active_style)

                # Применение неактивного стиля к полям ММ:СС
                self.lineEdit_MS_M.setStyleSheet(inactive_style)
                self.lineEdit_MS_S.setStyleSheet(inactive_style)
            case TimeField.MS:  # Режим ММ:СС
                # Очистка полей для часов и минут (ЧЧ:ММ)
                self.lineEdit_HM_H.clear()
                self.lineEdit_HM_M.clear()

                # Применение активного стиля к полям ММ:СС
                self.lineEdit_MS_M.setStyleSheet(active_style)
                self.lineEdit_MS_S.setStyleSheet(active_style)

                # Применение неактивного стиля к полям ЧЧ:ММ
                self.lineEdit_HM_H.setStyleSheet(inactive_style)
                self.lineEdit_HM_M.setStyleSheet(inactive_style)

        # Если длина введенного текста достигает 2 символов, перемещаем фокус на следующее поле
        if len(txt) == 2:
            focus.setFocus()

    def start(self) -> int:
        """
        Запускает приложение и отображает главное окно.

        Returns:
            int: Код завершения приложения.
        """
        self.show()  # Отображает главное окно
        return PyQt6.QtWidgets.QApplication.exec()  # Запускает основной цикл приложения


# Запуск приложения
if __name__ == "__main__":
    # Создаем экземпляр приложения PyQt
    app = PyQt6.QtWidgets.QApplication(sys.argv)

    # Создаем экземпляр главного окна таймера
    timer_2_app = Timer2()

    # Запускаем приложение и передаем управление системе
    sys.exit(timer_2_app.start())
