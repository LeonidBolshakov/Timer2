"""Фасад рабочей модели и файлового хранилища настроек."""

from pathlib import Path

from .param_keys import ParamKeys, TuneValue
from .mapper import dto_to_model, model_to_dto
from .model import Model
from .storage import Storage


class Context:
    """Менеджер настроек: модель + загрузка/сохранение + переключение файла."""

    def __init__(self) -> None:
        self.storage = Storage()
        self.model: Model = dto_to_model(self.storage.load())

    @property
    def settings_file(self) -> Path:
        """Вернуть абсолютный путь активного JSON-профиля."""
        return self.storage.settings_file

    def save(self) -> None:
        """Преобразовать текущую модель в DTO и сохранить её."""
        self.storage.save(model_to_dto(self.model))

    def switch_settings_file(self, settings_file: Path) -> None:
        """
        Переключает активный файл настроек.
        """
        dto = self.storage.switch_settings_file(settings_file)
        self.model = dto_to_model(dto)

    def set_value(self, key: ParamKeys, value: TuneValue, save: bool = True) -> None:
        """Изменить значение модели и при необходимости сразу сохранить профиль.

        Параметр save=False используется для групповых изменений, после которых
        выполняется одна итоговая запись.
        """
        self.model.set_value(key, value)
        if save:
            self.save()
