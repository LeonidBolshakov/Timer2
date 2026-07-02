from dataclasses import dataclass


@dataclass(frozen=True, slots=False)
class Const:
    """Константы программы. Настройки пользователя здесь не хранятся."""

    ACTIVE_FIELD_BG_COLOR = "QLineEdit { background-color: #f5ffb3; }"
    END_CHECK_INTERVAL = 100
    FILE_TUNES_0 = "../../tunes.json"

    FORMS_HOUR = ["часов", "час", "часа"]
    FORMS_MINUTE = ["минут", "минута", "минуты"]
    FORMS_SECUNDA = ["секунд", "секунда", "секунды"]
    GENDER_F = "f"
    GENDER_M = "m"
    INACTIVE_FIELD_BG_COLOR = "QLineEdit { background-color: white; }"
    JSON = "json"
    LANG_RU = "ru"

    RE_PATTERN_0_24 = r"[0-9]|1[0-9]|2[0-3]"
    RE_PATTERN_0_60 = r"[0-5][0-9]"

    SECONDS_IN_HOUR = 3600
    SECONDS_IN_MINUTE = 60

    TEXT_ERROR_CALLBACK = "Класс Clock. Неверно указана функция callback - "
    TEXT_ERROR_NAME_CALLBACK = (
        "Класс Clock. Функция callback регистрируется повторно - "
    )
    TEXT_ERROR_PARAM = (
        "методу timer_3.active_time_field передан непредусмотренный параметр widget."
    )
    TEXT_ERROR_READ = (
        "Файл настроек недоступен или в нём недостоверная информация.\n"
        "Работаем с настройками по умолчанию"
    )
    TEXT_ERROR_UNKNOWN = "Неизвестная ошибка"
    TEXT_ERROR_VALUE = "Неправильное значение настройки"
    TEXT_ERROR_WRITE = "Настройки программы не сохранены.\n"
    TEXT_ERROR_FILE_NAME = "Задано некорректное имя файла"
    TEXT_INTERNAL_ERROR = "Внутренняя ошибка: экземпляр приложения не существует!"
    TEXT_NO_INIT_SPEECH = "Не удалось инициировать синтезатор речи"
    TEXT_NO_MELODY = "Не задана мелодия окончания таймера"
    TEXT_NO_PLAY_MELODY = "Ошибка при инициализации/использовании проигрывателя музыки"

    TIMER_3_UI = "_internal/timer_3.ui"
    TIMER_INTERVAL = 1000
    TUNES_UI = "_internal/tunes.ui"

    TITLE_ERROR_READ = "Ошибка при вводе файла настроек"
    TITLE_ERROR_SPEACH = "Инициализация синтезатора речи"
    TITLE_ERROR_TUNE = "Ошибка настройки"
    TITLE_ERROR_WRITE = "Ошибка при выводе файла настроек"
    TITLE_INTERNAL_ERROR = "Внутренняя ошибка"
    TITLE_NO_MELODY = "Не задана мелодия"
    TITLE_SELECT_FILE_TUNE = "Выбери файл настроек"
    TITLE_SELECT_MELODY = "Выбери файл мелодии"

    TYPES_FILE_MELODY = "*.mp3"
    TYPES_FILE_TUNES = f"JSON файлы (*.{JSON})"
