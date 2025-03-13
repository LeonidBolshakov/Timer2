import sys
import io
from enum import Enum

sys.stdout = io.StringIO()  # Заглушает вывод рекламы pygame
import pygame  # type: ignore

sys.stdout = sys.__stdout__  # Возвращает стандартный вывод
from PyQt6.QtWidgets import (
    QMainWindow,
    QLineEdit,
    QPushButton,
    QLabel,
    QApplication,
    QWidget,
)

from PyQt6 import uic  # type: ignore
from PyQt6.QtGui import QRegularExpressionValidator
from PyQt6.QtCore import QRegularExpression

from const import Const as C
from clock import Clock  # Класс таймера
import functions as f  # Вспомогательные функции

from tunes import Tunes


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

    def __init__(self) -> None:
        """
        Конструктор для инициализации основного окна.
        Устанавливает валидаторы, подключает события и задает начальные параметры.
        """
        super().__init__()
        uic.loadUi(C.FILE_UI, self)  # Загрузка интерфейса из файла .ui

        self.clock: Clock | None = None  # Объект Clock
        self.tunes = Tunes()  # объект настроек
        self.tunes_window: Tunes | None = None

        # Создание и назначение валидаторов для ввода времени
        self.validator_hour = QRegularExpressionValidator()
        self.validator_min_sec = QRegularExpressionValidator()
        self.set_validators()  # Установка правил валидации

        self.connect_signals()  # Подключение сигналов к обработчикам событий
        self.set_bolds()  # Установка жирного шрифта для полей ввода

        self.init_vars()  # Инициализация переменных

    def set_validators(self) -> None:
        """
        Устанавливает регулярные выражения для валидации ввода времени.
        """
        # Валидация для часов (0-23, пустое поле допустимо)
        self.validator_hour = QRegularExpressionValidator(
            QRegularExpression(C.RE_PATTERN_0_24)
        )
        # Валидация для минут и секунд (0-59, пустое поле допустимо)
        self.validator_min_sec = QRegularExpressionValidator(
            QRegularExpression(C.RE_PATTERN_0_60)
        )

        # Назначает валидаторы соответствующим полям ввода.
        self.lineEdit_HM_H.setValidator(self.validator_hour)
        self.lineEdit_HM_M.setValidator(self.validator_min_sec)
        self.lineEdit_MS_M.setValidator(self.validator_min_sec)
        self.lineEdit_MS_S.setValidator(self.validator_min_sec)

    def connect_signals(self) -> None:
        """
        Подключает сигналы компонентов пользовательского интерфейса к обработчикам событий.
        """
        self.btnQuit.clicked.connect(f.go_quit)  # Кнопка "Выход"
        self.btnStart.clicked.connect(self.on_btnStart_click)  # Кнопка "Старт"
        self.btnTunes.clicked.connect(self.on_btnTunes_click)  # Кнопка "Настройки"

        # Обработка окончания редактирования полей ввода времени
        self.lineEdit_HM_H.textEdited.connect(
            lambda: self.on_lineEdit_edited(self.lineEdit_HM_H, self.lineEdit_HM_M)
        )
        self.lineEdit_HM_M.textEdited.connect(
            lambda: self.on_lineEdit_edited(self.lineEdit_HM_M, self.btnStart)
        )
        self.lineEdit_MS_M.textEdited.connect(
            lambda: self.on_lineEdit_edited(self.lineEdit_MS_M, self.lineEdit_MS_S)
        )
        self.lineEdit_MS_S.textEdited.connect(
            lambda: self.on_lineEdit_edited(self.lineEdit_MS_S, self.btnStart)
        )

    def set_bolds(self) -> None:
        """
        Устанавливает жирный шрифт для всех полей ввода времени.
        """
        for line_edit in (
            self.lineEdit_HM_H,
            self.lineEdit_HM_M,
            self.lineEdit_MS_M,
            self.lineEdit_MS_S,
        ):  # Поля ввода времени
            font = line_edit.font()
            font.setBold(True)
            line_edit.setFont(font)

    def init_vars(self) -> None:
        """
        Инициализирует начальные значения интерфейса и переменных.
        """
        self.lblSec.setText(
            ""
        )  # Очищает метку для секунд. Задана в Qt Designer для служебных целей

    def on_btnStart_click(self) -> None:
        """
        Обработчик нажатия кнопки "Старт".
        Создает объект Clock и запускает таймер.
        """
        # Создание таймера
        if self.clock is None and self.get_seconds_left():
            self.clock = Clock(
                self.get_seconds_left(), self.draw_time
            )  # Создание объекта Clock
            self.clock.start()  # Старт таймера
            self.btnStart.setDisabled(True)  # Кнопка больше НЕ нужна
            f.beep()

    def on_btnTunes_click(self) -> None:
        """
        Обработчик нажатия кнопки "Настройки".
        """
        if (
            self.tunes_window is None
        ):  # Защита от создания многих окон при повторном нажатии кнопки.
            self.tunes_window = Tunes()
        self.tunes_window.show()  # Self.tunes_window не закрыт. Продолжаем с ним работать.

    def draw_time(self, seconds_left: int) -> None:
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
            case _:
                pass

    def draw_hour_min(self, hour: int, minutes: int, sec: int) -> None:
        """
        Отображает оставшееся время в формате ЧЧ:ММ.
        """
        self.lineEdit_HM_H.setText(f"{hour:02}")
        self.lineEdit_HM_M.setText(f"{minutes:02}")
        self.lblSec.setText(f": {sec:02}")

    def draw_min_sec(self, minutes: int, sec: int) -> None:
        """
        Отображает оставшееся время в формате ММ:СС.
        """
        self.lineEdit_MS_M.setText(f"{minutes:02}")
        self.lineEdit_MS_S.setText(f"{sec:02}")

    def get_seconds_left(self) -> int:
        """
        Вычисляет общее оставшееся время в секундах.

        Returns:
            int: Общее количество оставшихся секунд.
        """
        match self.active_time_field():
            case TimeField.MS:
                return f.num(self.lineEdit_MS_M) * C.SECONDS_IN_MINUTE + f.num(
                    self.lineEdit_MS_S
                )
            case TimeField.HM:
                return (
                    f.num(self.lineEdit_HM_H) * C.SECONDS_IN_HOUR
                    + f.num(self.lineEdit_HM_M) * C.SECONDS_IN_MINUTE
                )
            case _:
                return 0

    def active_time_field(self, widget: QLineEdit | None = None) -> TimeField | None:
        """
        Определяет активное поле ввода времени (ЧЧ:ММ или ММ:СС).

        Returns:
            TimeField | None: Активное поле ввода или None.
        """
        match widget:
            case None:
                return self._active_time_field()
            case self.lineEdit_HM_H | self.lineEdit_HM_M:
                return TimeField.HM
            case self.lineEdit_MS_M | self.lineEdit_MS_S:
                return TimeField.MS
            case _:
                f.inform_fatal_error(
                    C.TITLE_INTERNAL_ERROR,
                    f"{C.TEXT_ERROR_PARAM}\n{widget.objectName()=}",
                )

    def _active_time_field(self):
        """
        Определяет активное поле ввода времени (ЧЧ:ММ или ММ:СС),
        в случае, если поле ввода времени не было изменено

        Returns:
            TimeField | None: Активное поле ввода или None.
        """
        if self.lineEdit_MS_M.text() or self.lineEdit_MS_S.text():
            return TimeField.MS
        if self.lineEdit_HM_H.text() or self.lineEdit_HM_M.text():
            return TimeField.HM
        return None

    def on_lineEdit_edited(self, widget: QLineEdit, focus: QWidget) -> None:
        """
        Обработчик изменения текста в любом поле ввода.
        Устанавливает стили полей ввода и, при необходимости, устанавливает фокус.

        Args:
            widget (str): Виджет, в который введена информация.
            focus: Виджет, на который, при необходимости, нужно переместить фокус.
        """

        # Активируем/деактивируем поля ввода времени
        match self.active_time_field(widget):
            case TimeField.HM:  # Режим ЧЧ:ММ
                self.activate_time_input_widgets(
                    self.lineEdit_HM_H,
                    self.lineEdit_HM_M,
                    self.lineEdit_MS_M,
                    self.lineEdit_MS_S,
                )
            case TimeField.MS:  # Режим ММ:СС
                self.activate_time_input_widgets(
                    self.lineEdit_MS_M,
                    self.lineEdit_MS_S,
                    self.lineEdit_HM_H,
                    self.lineEdit_HM_M,
                )
            case _:
                f.inform_fatal_error(C.TITLE_INTERNAL_ERROR, C.TEXT_ERROR_UNKNOWN)

        # Если длина введенного текста достигает 2 символов, перемещаем фокус на следующее поле
        if len(widget.text()) == 2:
            focus.setFocus()

    @staticmethod
    def activate_time_input_widgets(
        active_1: QLineEdit,
        active_2: QLineEdit,
        inactive_1: QLineEdit,
        inactive_2: QLineEdit,
    ) -> None:
        """
        Активируем / деактивируем поля ввода времени
        :param active_1: Виджет, который следует сделать активным.
        :param active_2: Виджет, который следует сделать активным.
        :param inactive_1: Виджет, который следует сделать НЕ активным.
        :param inactive_2: Виджет, который следует сделать НЕ активным.
        :return: None
        """

        # Очистка неактивных виджетов
        inactive_1.clear()
        inactive_2.clear()

        # Применение к неактивным виджетам неактивного стиля
        inactive_1.setStyleSheet(C.INACTIVE_FIELD_BG_COLOR)
        inactive_2.setStyleSheet(C.INACTIVE_FIELD_BG_COLOR)

        # Применение к активным виджетам активного стиля
        active_1.setStyleSheet(C.ACTIVE_FIELD_BG_COLOR)
        active_2.setStyleSheet(C.ACTIVE_FIELD_BG_COLOR)

    def start(self) -> int:
        """
        Запускает приложение и отображает главное окно.

        Returns:
            int: Код завершения приложения.
        """
        self.show()  # Отображает главное окно
        return QApplication.exec()  # Запускает основной цикл приложения


# Запуск приложения
if __name__ == "__main__":

    def on_app_exit():
        """При завершении приложения прекращаем проигрывание музыки"""
        pygame.mixer.quit()

    # Создаем экземпляр приложения PyQt
    app = QApplication(sys.argv)

    app.aboutToQuit.connect(on_app_exit)

    # Создаем экземпляр главного окна таймера
    timer_2_app = Timer2()

    # Запускаем приложение и передаем управление системе
    sys.exit(timer_2_app.start())
