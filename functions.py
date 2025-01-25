from PyQt6.QtWidgets import QLineEdit, QApplication


def on_lineEdit_edited(txt: str, focus, clear_1: QLineEdit, clear_2: QLineEdit):
    clear_1.clear()
    clear_2.clear()
    if len(txt) == 2:
        focus.setFocus()


def num(line_edit: QLineEdit) -> int:
    return int(line_edit.text()) if line_edit.text() else 0


def on_quit():
    # Завершение работы программы
    QApplication.instance().quit()
