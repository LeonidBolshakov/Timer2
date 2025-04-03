from dataclasses import dataclass
from typing import Any

from PyQt6 import QtCore


@dataclass
class TuneDescr:
    """Описание настройки"""

    name_tune: str  # имя настройки
    default: Any  # значение по умолчанию


@dataclass(frozen=True, slots=False)
class Const:
    """Константы программ"""

    FILE_UI = "timer_2.ui"  # имя/путь UI файла
    RE_PATTERN_0_24 = (
        r"[0-9]|1[0-9]|2[0-3]"  # Шаблон для часа суток. Пустое поле допустимо.
    )
    RE_PATTERN_0_60 = (
        r"[0-5][0-9]"  # Шаблон для количества минут или секунд. Пустое поле допустимо.
    )
    SECONDS_IN_MINUTE = 60  # Секунд в минуте
    SECONDS_IN_HOUR = 3600  # Секунд в часе
    TEXT_NO_TUNES = "Ошибка в программе.\nЗапрошена несуществующая настройка - "
    TEXT_NO_VALIDATION = "Ошибка в программе. Провальная валидация - "
    TEXT_TYPE_ERROR = (
        "Ошибка в программе. Метод Put_tune. Непредусмотренный тип настройки .\n"
    )
    TITLE_ERROR_READ = "Ошибка при вводе файла настроек"
    TEXT_ERROR_READ = (
        "Файл настроек недоступен или в нём недостоверная информация.\n"
        "Работаем с настройками по умолчанию"
    )
    TITLE_ERROR_WRITE = "Ошибка при выводе файла настроек"
    TEXT_ERROR_WRITE = "Настройки программы не сохранены.\n"
    TITLE_ERROR_TUNE = "Ошибка при сохранении настройки"
    TEXT_ERROR_VALUE = "Неправильное значение ключа"
    TEXT_ERROR_KEY = "Не зарегистрированное имя настройки"
    TEXT_ERROR_UNKNOWN = "Не известная ошибка"
    TITLE_INTERNAL_ERROR = "Внутренняя ошибка"
    TEXT_INTERNAL_ERROR = "Внутренняя ошибка: Экземпляр приложения не существует!"
    TITLE_ERROR_SPEACH = "Инициализация синтезатора речи"
    TEXT_NO_INIT_SPEECH = "Не удалось инициировать синтезатор речи"
    TEXT_ERROR_CALLBACK = "Класс Clock. Неверно указана функция callback - "
    TITLE_NO_MELODY = "Не задана мелодия"
    TEXT_NO_MELODY = "Не задана мелодия окончания таймера"
    TEXT_NO_PLAY_MELODY = "Ошибка при инициализации/использования проигрывателя музыки"
    TEXT_ERROR_PARAM = (
        "методу timer_2.active_time_field передан непредусмотренный параметр widget."
    )
    TEXT_SELECT_MELODY = "Выбери файл мелодии"
    TYPES_FILE_MELODY = "*.mp3"
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
    END_CHECK_INTERVAL = 100  # интервал опроса завершения проигрывания мелодии (мс)
    TIMER_INTERVAL = (
        1000  # Интервал таймера - 1 секунда (1000 миллисекунд). Менять нельзя
    )
    FILE_TUNES = "tunes.json"
    TUNE_VOICE_INTERVAL = TuneDescr(
        "TUNE_VOICE_INTERVAL", 10
    )  # Интервал в секундах между голосовыми сообщениями
    TUNE_FILE_MELODY = TuneDescr(
        "TUNE_FILE_MELODY", "default.mp3"
    )  # имя/путь файла с музыкой, завершающей таймер
    TUNE_RESTORE_TIME = TuneDescr(
        "TUNE_RESTORE_TIME", QtCore.Qt.CheckState.Unchecked
    )  # Восстановление времени таймера
    TUNE_BEEP_INTERVAL = TuneDescr(
        "TUNE_BEEP_INTERVAL", 3
    )  # Интервал в секундах между сигналами beep в конце работы таймера
    TUNE_BEEP_PERIOD_IN_FINAL = TuneDescr(
        "TUNE_BEEP_PERIOD_IN_FINAL", 11
    )  # количество секунд до конца таймера для выдачи beep
