from PyQt6.QtWidgets import (
    QLineEdit,
    QApplication,
    QMessageBox,
)
from num2words import num2words  # type: ignore # Библиотека для преобразования чисел в текст

from const import Const as c


def num(line_edit: QLineEdit) -> int:
    """
    Преобразует текст из виджета QLineEdit в целое число.
    В тексте могут быть только цифры. Это обеспечивает валидация при вводе текста.

    Args:
        line_edit (QLineEdit): Виджет для ввода текста.

    Returns:
        int: Целое число, полученное из текста. Если текст пустой, возвращает 0.
    """
    return (
        int(line_edit.text()) if line_edit.text() else 0
    )  # Если текст не пустой, преобразуем его в число, иначе возвращаем 0


def go_quit() -> None:
    """
    Завершает выполнение программы, вызывая метод `quit()` у текущего экземпляра QApplication.
    """
    app = QApplication.instance()
    if app is not None:
        app.quit()
    else:
        QMessageBox.warning(None, c.TITLE_INTERNAL_ERROR, c.TEXT_INTERNAL_ERROR)


def hour_minutes_sec(seconds: int) -> tuple[int, int, int]:
    """
    Конвертирует секунды в часы, минуты и секунды.

    Args:
        seconds (int): Общее количество секунд.

    Returns:
        tuple: Кортеж в формате (часы, минуты, секунды).
    """
    hour, min_sec = divmod(
        seconds, c.SECONDS_IN_HOUR
    )  # Вычисляем часы и остаток в секундах
    minutes, sec = divmod(
        min_sec, c.SECONDS_IN_MINUTE
    )  # Вычисляем из остатка минуты и секунды

    return hour, minutes, sec


def time_to_text(seconds: int) -> str:
    """
    Преобразует время в секундах в текстовое представление на русском языке.

    Args:
        seconds (int): Общее количество секунд.

    Returns:
        str: Текстовое представление времени в формате "часов, минут, секунд".
    """
    # Расчёт часов, минут и секунд
    hour, minutes, sec = hour_minutes_sec(seconds)

    # Генерация текстового представления для каждого компонента времени
    hour_text = num_to_text(hour, c.GENDER_M, c.FORMS_HOUR)
    minutes_text = num_to_text(minutes, c.GENDER_F, c.FORMS_MINUTE)
    sec_text = num_to_text(sec, c.GENDER_F, c.FORMS_SECUNDA)

    # Объединяем текстовое представление времени и приводим первую букву к заглавной
    return (hour_text + minutes_text + sec_text).capitalize()


def num_to_text(number: int, gender: str, word_forms: list[str]) -> str:
    """
    Преобразует число в текст с указанием правильной формы слова, следующего за цифрами

    Args:
        number (int): Число, которое нужно преобразовать
        gender (str): Род числа ("m" для мужского, "f" для женского)
        word_forms (list[str]): Список трёх форм слова (множественная, единственная, двойственная).

    Returns:
        str: Текстовое представление числа с правильной формой слова, следующего за цифрами.
    """
    # Преобразуем число в текст и добавляем правильную форму слова
    return (
        num2words(
            number, lang=c.LANG_RU, gender=gender
        )  # Число в текстовом виде (например, "один", "два")
        + " "
        + get_word_form(
            number, word_forms
        )  # Добавляем форму слова (например, "час", "часа")
        + " "
        if number != 0
        else ""  # Если число равно 0, возвращаем пустую строку
    )


def get_word_form(number: int, word_after_number: list[str]) -> str:
    """
    Определяет правильную форму слова в зависимости от числительного.

    Args:
        number (int): Число, для которого нужно определить форму слова
        word_after_number (list[str]): Список трёх форм слова (множественная, единственная, двойственная).

    Returns:
        str: Правильная форма слова для данного числа.
    """
    last_digit = number % 10  # Последняя цифра числа
    last_digits = number % 100  # Два последние цифры числа

    # Определяем правильную форму слова на основе последней и двух последних цифр
    match last_digit:
        case 1 if (
            not 11 <= last_digits <= 14
        ):  # Если число оканчивается на 1 (кроме 11-14), используем вторую форму
            return word_after_number[1]
        case 2 | 3 | 4 if (
            not 11 <= last_digits <= 14
        ):  # Если число оканчивается на 2, 3 или 4 (кроме 11-14), используем третью форму
            return word_after_number[2]
        case (
            _
        ):  # Во всех остальных случаях используем первую форму (множественное число)
            return word_after_number[0]


def beep() -> None:
    """
    Воспроизводит короткий звуковой сигнал (системный звуковой сигнал приложения).
    """
    QApplication.beep()  # Используем стандартный метод для воспроизведения системного сигнала


def inform_fatal_error(title: str, text: str) -> None:
    """
    Действия при фатальной ошибке
    :param title: заголовок сообщения об ошибке
    :param text: текст сообщения об ошибке
    :return:
    """
    QMessageBox.warning(None, title, text)
    go_quit()
