from dataclasses import dataclass


@dataclass(frozen=True)
class Const:
    FILE_UI = "timer_2.ui"  # имя/путь UI файла
    RE_PATTERN_0_24 = r"[0-9]|1[0-9]|2[0-3]"  # Шаблон для часа суток
    RE_PATTERN_0_60 = r"[0-5][0-9]"  # Шаблон для количества минут или секунд
    SECONDS_IN_MINUTE = 60  # Секунд в минуте
    SECONDS_IN_HOUR = 3600  # Секунд в часе
    ACTIVE_FIELD_BG_COLOR = (
        "QLineEdit { background-color: #f5ffb3; }"  # Желтый фон для активных полей
    )
    INACTIVE_FIELD_BG_COLOR = (
        "QLineEdit { background-color: white; }"  # Белый фон для неактивных полей
    )
    FORMS_HOUR = [
        "часов",
        "час",
        "часа",
    ]  # множественная, единственная, двойственная формы слова Час
    FORMS_MINUTE = [
        "минут",
        "минута",
        "минуты",
    ]  # множественная, единственная, двойственная формы слова Минута
    FORMS_SECUNDA = [
        "секунд",
        "секунда",
        "секунды",
    ]  # множественная, единственная, двойственная формы слова Секунда
    GENDER_M = "m"  # Мужской род
    GENDER_F = "f"  # Женский род
    LANG_RU = "ru"  # Обозначение русского языка
    TIMER_INTERVAL = 1000  # таймер с интервалом в 1 секунду (1000 миллисекунд)
    VOICE_MESSAGE_INTERVAL_SECONDS = (
        10  # Интервал в секундах между голосовыми сообщениями
    )
    FILE_SOUND = "example.mp3"  # имя/путь файла с музыкой/сообщением, извещающем о завершении таймера
    BEEP_MESSAGE_INTERVAL_SECONDS = (
        2  # Интервал в секундах между сигналами beep в конце работы таймера
    )
    FINAL_BEEP_SECONDS = 10  # количество секунд до конца таймера для начала выдачи beep
