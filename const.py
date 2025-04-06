from dataclasses import dataclass
from typing import Any

from PyQt6.QtCore import Qt


@dataclass
class TuneDescr:
    """Описание настройки"""

    name_tune: str  # имя настройки
    default: Any  # значение по умолчанию


@dataclass(frozen=True, slots=False)
class Const:
    """Константы программ"""

    ACTIVE_FIELD_BG_COLOR = (
        "QLineEdit { background-color: #f5ffb3; }"  # Желтый фон для активных полей
    )
    END_CHECK_INTERVAL = 100  # интервал опроса завершения проигрывания мелодии (мс)
    FILE_TUNES = "tunes.json"
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
    GENDER_F = "f"  # Женский род
    GENDER_M = "m"  # Мужской род
    INACTIVE_FIELD_BG_COLOR = (
        "QLineEdit { background-color: white; }"  # Белый фон для неактивных полей
    )
    LANG_RU = "ru"  # Обозначение русского языка
    RE_PATTERN_0_24 = (
        r"[0-9]|1[0-9]|2[0-3]"  # Шаблон для часа суток. Пустое поле допустимо.
    )
    RE_PATTERN_0_60 = (
        r"[0-5][0-9]"  # Шаблон для количества минут или секунд. Пустое поле допустимо.
    )
    SECONDS_IN_HOUR = 3600  # Секунд в часе
    SECONDS_IN_MINUTE = 60  # Секунд в минуте
    TEXT_ERROR_CALLBACK = "Класс Clock. Неверно указана функция callback - "
    TEXT_ERROR_KEY = "Не зарегистрированное имя настройки"
    TEXT_ERROR_PARAM = (
        "методу timer_2.active_time_field передан непредусмотренный параметр widget."
    )
    TEXT_ERROR_READ = (
        "Файл настроек недоступен или в нём недостоверная информация.\n"
        + "Работаем с настройками по умолчанию"
    )
    TEXT_ERROR_UNKNOWN = "Не известная ошибка"
    TEXT_ERROR_VALUE = "Неправильное значение ключа"
    TEXT_ERROR_WRITE = "Настройки программы не сохранены.\n"
    TEXT_INTERNAL_ERROR = "Внутренняя ошибка: Экземпляр приложения не существует!"
    TEXT_NO_INIT_SPEECH = "Не удалось инициировать синтезатор речи"
    TEXT_NO_MELODY = "Не задана мелодия окончания таймера"
    TEXT_NO_PLAY_MELODY = "Ошибка при инициализации/использования проигрывателя музыки"
    TEXT_NO_TUNES = "Ошибка в программе.\nЗапрошена несуществующая настройка - "
    TEXT_SELECT_MELODY = "Выбери файл мелодии"
    TEXT_TYPE_ERROR = (
        "Ошибка в программе. Метод Put_tune. Непредусмотренный тип настройки .\n"
    )
    TIMER_2_UI = "_internal/timer_2.ui"  # имя/путь UI файла главного окна
    TIMER_INTERVAL = (
        1000  # Интервал таймера - 1 секунда (1000 миллисекунд). Менять нельзя
    )
    TITLE_ERROR_READ = "Ошибка при вводе файла настроек"
    TITLE_ERROR_SPEACH = "Инициализация синтезатора речи"
    TITLE_ERROR_TUNE = "Ошибка при сохранении настройки"
    TITLE_ERROR_WRITE = "Ошибка при выводе файла настроек"
    TITLE_INTERNAL_ERROR = "Внутренняя ошибка"
    TITLE_NO_MELODY = "Не задана мелодия"
    TUNE_BEEP_INTERVAL = TuneDescr(
        "TUNE_BEEP_INTERVAL", 3
    )  # Интервал в секундах между сигналами beep в конце работы таймера
    TUNE_BEEP_PERIOD_IN_FINAL = TuneDescr(
        "TUNE_BEEP_PERIOD_IN_FINAL", 11
    )  # количество секунд до конца таймера для выдачи beep
    TUNE_FILE_MELODY = TuneDescr(
        "TUNE_FILE_MELODY", "_internal\\default.mp3"
    )  # имя/путь файла с музыкой, завершающей таймер
    TUNE_HM_H = TuneDescr("TUNE_HM_H", 0)
    TUNE_HM_M = TuneDescr("TUNE_HM_M", 0)
    TUNE_MS_M = TuneDescr("TUNE_MS_M", 0)
    TUNE_MS_S = TuneDescr("TUNE_MS_S", 0)
    TUNE_RESTORE_TIME = TuneDescr(
        "TUNE_RESTORE_TIME", str(Qt.CheckState.Unchecked)
    )  # Признак - Восстановление времени таймера
    TUNE_VOICE_INTERVAL = TuneDescr(
        "TUNE_VOICE_INTERVAL", 10
    )  # Интервал в секундах между голосовыми сообщениями
    TUNES_UI = "_internal/tunes.ui"  # имя/путь UI файла настроек
    TYPES_FILE_MELODY = "*.mp3"
