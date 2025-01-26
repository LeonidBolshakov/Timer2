from PyQt6.QtWidgets import (
    QLineEdit,
    QApplication,
)  # Импорт виджета QLineEdit и QApplication
from num2words import num2words  # Библиотека для преобразования чисел в текст


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
    )  # Если текст есть, преобразуем его в число, иначе возвращаем 0


def on_quit():
    """
    Завершает выполнение программы, вызывая метод `quit()` у текущего экземпляра QApplication.
    """
    QApplication.instance().quit()  # Завершение текущего приложения


def hour_minutes_sec(seconds: int) -> (int, int, int):
    """
    Конвертирует секунды в часы, минуты и секунды.

    Args:
        seconds (int): Общее количество секунд.

    Returns:
        tuple: Кортеж в формате (часы, минуты, секунды).
    """
    hour, min_sec = divmod(seconds, 3600)  # Вычисляем часы и остаток в секундах
    minutes, sec = divmod(min_sec, 60)  # Вычисляем из остатка минуты и секунды

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
    hour_text = num_to_text(hour, "m", ["часов", "час", "часа"])
    minutes_text = num_to_text(minutes, "f", ["минут", "минута", "минуты"])
    sec_text = num_to_text(sec, "f", ["секунд", "секунда", "секунды"])

    # Объединяем текстовое представление времени и приводим первую букву к заглавной
    return (hour_text + minutes_text + sec_text).capitalize()


def num_to_text(number: int, gender: str, word_forms: list[str]) -> str:
    """
    Преобразует число в текст с указанием правильной формы слова, следующего за цифрами

    Args:
        number (int): Число, которое нужно преобразовать.
        gender (str): Род числа ("m" для мужского, "f" для женского).
        word_forms (list[str]): Список трёх форм слова (множественная, единственная, двойственная).

    Returns:
        str: Текстовое представление числа с правильной формой слова, следующего за цифрами.
    """
    # Преобразуем число в текст и добавляем правильную форму слова
    return (
        num2words(
            number, lang="ru", gender=gender
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
    Определяет правильную форму слова в зависимости от числа.

    Args:
        number (int): Число, для которого нужно определить форму слова.
        word_after_number (list[str]): Список трёх форм слова (множественная, единственная, двойственная).

    Returns:
        str: Правильная форма слова для данного числа.
    """
    last_digit = number % 10  # Последняя цифра числа
    last_digits = number % 100  # Два последние цифры числа

    # Определяем правильную форму слова на основе последней и двух последних цифр
    match last_digit:
        case (
        1
        ) if not 11 <= last_digits <= 14:  # Если число оканчивается на 1 (кроме 11-14), используем вторую форму
            return word_after_number[1]
        case (
        2 | 3 | 4
        ) if not 11 <= last_digits <= 14:  # Если число оканчивается на 2, 3 или 4 (кроме 11-14), используем третью форму
            return word_after_number[2]
        case (
        _
        ):  # Во всех остальных случаях используем первую форму (множественное число)
            return word_after_number[0]
