from PyQt6.QtWidgets import QLineEdit, QApplication

from num2words import num2words


def on_lineEdit_edited(
        highlight_active_field, txt: str, focus, clear_1: QLineEdit, clear_2: QLineEdit
):
    clear_1.clear()
    clear_2.clear()
    highlight_active_field()
    if len(txt) == 2:
        focus.setFocus()


def num(line_edit: QLineEdit) -> int:
    return int(line_edit.text()) if line_edit.text() else 0


def on_quit():
    # Завершение работы программы
    QApplication.instance().quit()


def hour_minutes_sec(seconds: int) -> (int, int, int):
    hour, min_sec = divmod(seconds, 3600)
    minutes, sec = divmod(min_sec, 60)

    return hour, minutes, sec


def time_to_text(seconds: int) -> str:
    hour, minutes, sec = hour_minutes_sec(seconds)

    hour_text = num_to_text(hour, "m", ["часов", "час", "часа"])
    minutes_text = num_to_text(minutes, "f", ["минут", "минута", "минуты"])
    sec_text = num_to_text(sec, "f", ["секунд", "секунда", "секунды"])

    return (hour_text + minutes_text + sec_text).capitalize()


def num_to_text(number: int, gender: str, word_forms: list[str]) -> str:
    return (
        num2words(number, lang="ru", gender=gender)
        + " "
        + get_word_form(number, word_forms)
        + " "
        if number != 0
        else ""
    )


def get_word_form(number: int, word_after_number: list[str]) -> str:
    last_digit = number % 10
    last_digits = number % 100
    match last_digit:
        case 1 if not 11 <= last_digits <= 14:
            return word_after_number[1]
        case 2 | 3 | 4 if not 11 <= last_digits <= 14:
            return word_after_number[2]
        case _:
            return word_after_number[0]
