from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from .tunes_dto import TunesDTO
from .tunes_mapper import default_dto, dto_to_json_dict, json_dict_to_dto

PROGRAM_NAME = "Timer_2"

ACTIVE_SETTINGS_FILE_NAME = "active_settings.json"
ACTIVE_SETTINGS_KEY = "active_settings_file"
USER_PROFILE_FILE_NAME = "user.json"


class TunesStorage:
    """
    Файловое хранилище настроек.

    Архитектура:
    - default_dto() — заводские значения в коде;
    - profiles/user.json — основной рабочий файл пользователя;
    - active_settings.json — служебный указатель на активный файл настроек.
    """

    def __init__(self) -> None:
        self.warnings: list[str] = []
        self.settings_file = self._load_active_settings_file()

    # ------------------------------------------------------------------
    # Публичные методы
    # ------------------------------------------------------------------

    def load(self) -> TunesDTO:
        """
        Загружает активный файл настроек.

        Если активный файл отсутствует, недоступен или повреждён,
        используются настройки по умолчанию.

        Предупреждения для пользователя накапливаются в self.warnings.
        """
        dto = self._load_from_file(self.settings_file)
        self.save(dto)

        return dto

    def save(self, dto: TunesDTO) -> None:
        """
        Сохраняет настройки в текущий активный файл.
        """
        if not self._write_dto_to_file(self.settings_file, dto):
            self.warnings.append(
                "Не удалось сохранить файл настроек.\n"
                f"Файл: {self.settings_file}\n"
                "Изменения будут действовать до завершения программы, "
                "но могут быть потеряны после перезапуска."
            )

    def switch_settings_file(self, settings_file: Path) -> TunesDTO:
        """
        Переключает активный файл настроек.

        Если выбранный файл отсутствует, недоступен или повреждён,
        используются настройки по умолчанию, а предупреждение
        передаётся UI-слою через self.warnings.
        """
        new_file = settings_file.expanduser().resolve()

        dto = self._load_from_file(new_file)

        self.settings_file = new_file
        self._save_active_settings_file(new_file)
        self.save(dto)

        return dto

    def pop_warnings(self) -> list[str]:
        """
        Возвращает накопленные предупреждения и очищает список.
        """
        warnings = self.warnings.copy()
        self.warnings.clear()
        return warnings

    # ------------------------------------------------------------------
    # Пути
    # ------------------------------------------------------------------

    @classmethod
    def _app_dir(cls) -> Path:
        base_dir = Path(os.getenv("APPDATA", Path.home()))
        app_dir = base_dir / PROGRAM_NAME
        app_dir.mkdir(parents=True, exist_ok=True)
        return app_dir

    @classmethod
    def _profiles_dir(cls) -> Path:
        profiles_dir = cls._app_dir() / "profiles"
        profiles_dir.mkdir(parents=True, exist_ok=True)
        return profiles_dir

    @classmethod
    def _registry_file(cls) -> Path:
        return cls._app_dir() / ACTIVE_SETTINGS_FILE_NAME

    @classmethod
    def _user_settings_file(cls) -> Path:
        """
        Основной рабочий файл пользователя.

        Это не файл заводских настроек.
        Это обычный изменяемый файл настроек.
        """
        return cls._profiles_dir() / USER_PROFILE_FILE_NAME

    # ------------------------------------------------------------------
    # Загрузка active_settings.json
    # ------------------------------------------------------------------

    def _load_active_settings_file(self) -> Path:
        """
        Загружает путь к активному файлу настроек из active_settings.json.

        Если служебный файл отсутствует, повреждён или не содержит путь,
        возвращает путь к user.json.

        Важно:
        существование самого активного файла здесь не проверяется.
        Это делает load().
        """
        registry_file = self._registry_file()

        if not registry_file.exists():
            return self._user_settings_file()

        try:
            text = registry_file.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return self._user_settings_file()

        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            return self._user_settings_file()

        if not isinstance(data, dict):
            return self._user_settings_file()

        value = data.get(ACTIVE_SETTINGS_KEY)

        if not isinstance(value, str) or not value.strip():
            return self._user_settings_file()

        try:
            return Path(value).expanduser().resolve()
        except (OSError, RuntimeError):
            return self._user_settings_file()

    # ------------------------------------------------------------------
    # Запись файлов
    # ------------------------------------------------------------------

    def _write_dto_to_file(self, path: Path, dto: TunesDTO) -> bool:
        """
        Записывает DTO в файл.

        Не меняет self.settings_file.
        Не меняет active_settings.json.
        """
        return self._write_json_file(dto_to_json_dict(dto), path)

    def _save_active_settings_file(self, settings_file: Path) -> None:
        """
        Сохраняет путь к активному файлу настроек в active_settings.json.
        """
        registry_file = self._registry_file()
        registry_file.parent.mkdir(parents=True, exist_ok=True)

        data: dict[str, Any] = {
            ACTIVE_SETTINGS_KEY: str(settings_file.expanduser().resolve())
        }
        if not self._write_json_file(data, registry_file):
            self.warnings.append(
                "Не удалось сохранить указатель активного файла настроек.\n"
                f"Файл: {registry_file}\n"
                "Программа продолжит работу, но при следующем запуске может быть "
                "открыт не тот файл настроек."
            )

    def _write_json_file(self, data: dict[str, Any], path: Path) -> bool:
        """
        Пытается записать словарь в JSON-файл.

        Метод:
        - создаёт родительский каталог файла, если он отсутствует;
        - сериализует data в JSON;
        - записывает JSON в файл path в кодировке UTF-8.

        Возвращает:
            True  — файл успешно записан;
            False — файл не удалось записать.
        """
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                json.dumps(data, ensure_ascii=False, indent=4),
                encoding="utf-8",
            )
            return True
        except (OSError, UnicodeError, TypeError):
            return False

    # ------------------------------------------------------------------
    # Чтение файлов
    # ------------------------------------------------------------------

    def _load_from_file(self, settings_file: Path) -> TunesDTO:
        """
        Загружает настройки из указанного файла.

        Если файл отсутствует, недоступен, повреждён
        или имеет неверную структуру:
        - добавляет предупреждение в self.warnings;
        - возвращает DTO по умолчанию.
        """
        path = settings_file.expanduser().resolve()

        if not self._is_readable_settings_file(path):
            return default_dto()

        try:
            raw_data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as err:
            self._warn_bad_settings_file(path, err)
            return default_dto()

        if not isinstance(raw_data, dict):
            self._warn_invalid_settings_structure(path)
            return default_dto()

        return json_dict_to_dto(raw_data)

    def _is_readable_settings_file(self, path: Path) -> bool:
        """
        Проверяет, что путь существует и является файлом.
        При ошибке добавляет предупреждение.
        """
        if not path.exists():
            self.warnings.append(
                "Файл настроек не найден.\n"
                f"Файл: {path}\n"
                "Будут использованы настройки по умолчанию."
            )
            return False

        if not path.is_file():
            self.warnings.append(
                "Путь настроек не является файлом.\n"
                f"Путь: {path}\n"
                "Будут использованы настройки по умолчанию."
            )
            return False

        return True

    def _warn_bad_settings_file(self, path: Path, err: Exception) -> None:
        """
        Добавляет предупреждение о недоступном или повреждённом файле настроек.
        """
        self.warnings.append(
            "Файл настроек недоступен или повреждён.\n"
            f"Файл: {path}\n"
            f"Причина: {err}\n"
            "Будут использованы настройки по умолчанию."
        )

    def _warn_invalid_settings_structure(self, path: Path) -> None:
        """
        Добавляет предупреждение о неверной структуре файла настроек.
        """
        self.warnings.append(
            "Файл настроек содержит некорректную структуру.\n"
            f"Файл: {path}\n"
            "Будут использованы настройки по умолчанию."
        )
