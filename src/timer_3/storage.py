from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from .dto import DTO
from .mapper import default_dto, dto_to_json_dict, json_dict_to_dto

PROGRAM_NAME = "Timer_3"

ACTIVE_SETTINGS_FILE_NAME = "active_settings.json"
ACTIVE_SETTINGS_KEY = "active_settings_file"
USER_PROFILE_FILE_NAME = "user.json"


class Storage:
    """
    Файловое хранилище настроек.

    Архитектура:
    - default_dto() — заводские значения в коде;
    - profiles/user.json — основной рабочий файл пользователя;
    - active_settings.json — служебный указатель на активный файл настроек.
    """

    def __init__(self, app_dir: Path | None = None) -> None:
        self.warnings: list[str] = []

        self._app_dir_path = (
            app_dir.expanduser().resolve()
            if app_dir is not None
            else self._default_app_dir()
        )
        self._app_dir_path.mkdir(parents=True, exist_ok=True)

        self.settings_file = self._load_active_settings_file()

    # ------------------------------------------------------------------
    # Публичные методы
    # ------------------------------------------------------------------

    def load(self) -> DTO:
        """
        Загружает активный файл настроек.

        Если активный файл отсутствует, недоступен или повреждён,
        используются настройки по умолчанию.

        Если активный путь оказался каталогом или другим не-файлом,
        активным файлом становится profiles/user.json.
        """
        safe_settings_file = self._safe_settings_file(self.settings_file)

        if safe_settings_file is None:
            self.settings_file = self._user_settings_file()
            dto = default_dto()
            self.save(dto)
            self._save_active_settings_file(self.settings_file)
            return dto

        self.settings_file = safe_settings_file

        dto = self._load_from_file(self.settings_file)
        self.save(dto)

        return dto

    def save(self, dto: DTO) -> None:
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

    def switch_settings_file(self, settings_file: Path) -> DTO:
        """
        Переключает активный файл настроек.

        Если выбранный путь является каталогом или другим не-файлом,
        переключение не выполняется.

        Если выбранный файл отсутствует, он будет создан с настройками
        по умолчанию.
        """
        new_file = self._safe_settings_file(settings_file)

        if new_file is None:
            dto = self._load_from_file(self.settings_file)
            self.save(dto)
            return dto

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

    @staticmethod
    def _default_app_dir() -> Path:
        base_dir = Path(os.getenv("APPDATA", Path.home()))
        return (base_dir / PROGRAM_NAME).expanduser().resolve()

    def _app_dir(self) -> Path:
        self._app_dir_path.mkdir(parents=True, exist_ok=True)
        return self._app_dir_path

    def _profiles_dir(self) -> Path:
        profiles_dir = self._app_dir() / "profiles"
        profiles_dir.mkdir(parents=True, exist_ok=True)
        return profiles_dir

    def _registry_file(self) -> Path:
        return self._app_dir() / ACTIVE_SETTINGS_FILE_NAME

    def _user_settings_file(self) -> Path:
        """
        Основной рабочий файл пользователя.

        Это не файл заводских настроек.
        Это обычный изменяемый файл настроек.
        """
        return self._profiles_dir() / USER_PROFILE_FILE_NAME

    def _safe_settings_file(self, path: Path) -> Path | None:
        """
        Нормализует путь к файлу настроек.

        Возвращает:
            Path — путь отсутствует или является файлом;
            None — путь существует, но не является файлом.
        """
        try:
            normalized_path = path.expanduser().resolve()
        except (OSError, RuntimeError) as err:
            self.warnings.append(
                "Некорректный путь к файлу настроек.\n"
                f"Путь: {path}\n"
                f"Причина: {err}\n"
                "Будет использован основной файл настроек пользователя."
            )
            return None

        if normalized_path.exists() and not normalized_path.is_file():
            self.warnings.append(
                "Путь настроек не является файлом.\n"
                f"Путь: {normalized_path}\n"
                "Будет использован основной файл настроек пользователя."
            )
            return None

        return normalized_path

    # ------------------------------------------------------------------
    # Загрузка active_settings.json
    # ------------------------------------------------------------------

    def _load_active_settings_file(self) -> Path:
        """
        Загружает путь к активному файлу настроек из active_settings.json.

        Если служебный файл отсутствует, повреждён, не содержит путь
        или содержит путь к каталогу, возвращает путь к user.json.
        """
        data = self._load_active_settings_data()

        if data is None:
            return self._user_settings_file()

        active_file = self._get_active_file_from_data(data)

        if active_file is None:
            return self._user_settings_file()

        return active_file

    # ------------------------------------------------------------------
    # Запись файлов
    # ------------------------------------------------------------------

    def _write_dto_to_file(self, path: Path, dto: DTO) -> bool:
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
            safe_path = self._safe_settings_file(path)

            if safe_path is None:
                return False

            safe_path.parent.mkdir(parents=True, exist_ok=True)
            safe_path.write_text(
                json.dumps(data, ensure_ascii=False, indent=4),
                encoding="utf-8",
            )
            return True
        except (OSError, UnicodeError, TypeError):
            return False

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _load_from_file(self, settings_file: Path) -> DTO:
        """
        Загружает настройки из указанного файла.

        Если файл отсутствует, недоступен, повреждён
        или имеет неверную структуру:
        - добавляет предупреждение в self.warnings;
        - возвращает DTO по умолчанию.
        """
        safe_settings_file = self._safe_settings_file(settings_file)

        if safe_settings_file is None:
            return default_dto()

        if not self._is_readable_settings_file(safe_settings_file):
            return default_dto()

        try:
            raw_data = json.loads(safe_settings_file.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as err:
            self._warn_bad_settings_file(safe_settings_file, err)
            return default_dto()

        if not isinstance(raw_data, dict):
            self._warn_invalid_settings_structure(safe_settings_file)
            return default_dto()

        return json_dict_to_dto(raw_data)

    def _is_readable_settings_file(self, path: Path) -> bool:
        """
        Проверяет, что путь существует и является файлом.

        Если файл отсутствует, это не фатальная ошибка:
        при следующем save() будет создан файл с настройками по умолчанию.
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

    def _load_active_settings_data(self) -> dict[str, Any] | None:
        registry_file = self._registry_file()

        if not registry_file.exists():
            return None

        if not registry_file.is_file():
            self.warnings.append(
                "Путь служебного файла настроек не является файлом.\n"
                f"Путь: {registry_file}\n"
                "Будет использован основной файл настроек пользователя."
            )
            return None

        try:
            text = registry_file.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as err:
            self.warnings.append(
                "Служебный файл настроек недоступен.\n"
                f"Файл: {registry_file}\n"
                f"Причина: {err}\n"
                "Будет использован основной файл настроек пользователя."
            )
            return None

        try:
            data = json.loads(text)
        except json.JSONDecodeError as err:
            self.warnings.append(
                "Служебный файл настроек повреждён.\n"
                f"Файл: {registry_file}\n"
                f"Причина: {err}\n"
                "Будет использован основной файл настроек пользователя."
            )
            return None

        if not isinstance(data, dict):
            self.warnings.append(
                "Служебный файл настроек содержит некорректную структуру.\n"
                f"Файл: {registry_file}\n"
                "Будет использован основной файл настроек пользователя."
            )
            return None

        return data

    def _get_active_file_from_data(self, data: dict[str, Any]) -> Path | None:
        value = data.get(ACTIVE_SETTINGS_KEY)

        if not isinstance(value, str) or not value.strip():
            return None

        return self._safe_settings_file(Path(value))
