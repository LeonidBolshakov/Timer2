from __future__ import annotations

from dataclasses import asdict
from typing import Any

from . import functions as f
from . import settings_schema as schema
from .defaults import default_model
from .dto import DTO
from .model import Model
from .settings_schema import CURRENT_SETTINGS_VERSION


def dto_to_model(dto: DTO) -> Model:
    return Model(
        file_melody=dto.file_melody,
        voice_interval=dto.voice_interval,
        beep_interval=dto.beep_interval,
        beep_period_in_final=dto.beep_period_in_final,
        restore_time=dto.restore_time,
        hm_h=dto.hm_h,
        hm_m=dto.hm_m,
        ms_m=dto.ms_m,
        ms_s=dto.ms_s,
        active_tab_in_QTabWidget=dto.active_tab_in_QTabWidget,
        cycle_intervals=f.cycle_intervals_list(dto.cycle_intervals),
        cycle_repetitions=dto.cycle_repetitions,
        endlessly=dto.cycle_endlessly,
        current_interval=dto.current_interval,
        interval_duration=dto.interval_duration,
        left=dto.cycle_left,
    )


def default_dto() -> DTO:
    """
    DTO по умолчанию для записи в JSON.
    """
    return model_to_dto(default_model())


def model_to_dto(model: Model) -> DTO:
    return DTO(
        version=CURRENT_SETTINGS_VERSION,
        file_melody=model.file_melody,
        voice_interval=model.voice_interval,
        beep_interval=model.beep_interval,
        beep_period_in_final=model.beep_period_in_final,
        restore_time=model.restore_time,
        hm_h=model.hm_h,
        hm_m=model.hm_m,
        ms_m=model.ms_m,
        ms_s=model.ms_s,
        active_tab_in_QTabWidget=model.active_tab_in_QTabWidget,
        cycle_intervals=f.cycle_intervals_to_display(model.cycle_intervals),
        cycle_repetitions=model.cycle_repetitions,
        cycle_endlessly=model.endlessly,
        current_interval=model.current_interval,
        interval_duration=model.interval_duration,
        cycle_left=model.left,
    )


def dto_to_json_dict(dto: DTO) -> dict[str, Any]:
    return asdict(dto)


def json_dict_to_dto(data: object) -> DTO:
    """
    Преобразует JSON-словарь в DTO.

    Неизвестные ключи игнорируются.
    Некорректные значения заменяются значениями по умолчанию.
    Если данные не являются словарём, возвращает DTO по умолчанию.
    """
    defaults = default_dto()

    if not isinstance(data, dict):
        return defaults

    def raw(name: str) -> object:
        return data.get(name, getattr(defaults, name))

    def int_or_default(
        name: str,
        *,
        min_value: int | None = None,
        max_value: int | None = None,
    ) -> int:
        default_value = getattr(defaults, name)
        value = raw(name)

        if not isinstance(value, int | str) or isinstance(value, bool):
            return default_value

        try:
            result = int(value)
        except ValueError:
            return default_value

        if min_value is not None and result < min_value:
            return default_value

        if max_value is not None and result > max_value:
            return default_value

        return result

    def bool_or_default(name: str) -> bool:
        default_value = getattr(defaults, name)
        value = raw(name)

        if isinstance(value, bool):
            return value

        return default_value

    def str_or_default(name: str) -> str:
        default_value = getattr(defaults, name)
        value = raw(name)

        if isinstance(value, str):
            return value

        return default_value

    return DTO(
        version=CURRENT_SETTINGS_VERSION,
        file_melody=str_or_default("file_melody"),
        voice_interval=int_or_default(
            "voice_interval",
            min_value=schema.VOICE_INTERVAL_MIN,
            max_value=schema.VOICE_INTERVAL_MAX,
        ),
        beep_interval=int_or_default(
            "beep_interval",
            min_value=schema.BEEP_INTERVAL_MIN,
            max_value=schema.BEEP_INTERVAL_MAX,
        ),
        beep_period_in_final=int_or_default(
            "beep_period_in_final",
            min_value=schema.BEEP_PERIOD_IN_FINAL_MIN,
            max_value=schema.BEEP_PERIOD_IN_FINAL_MAX,
        ),
        restore_time=bool_or_default("restore_time"),
        hm_h=int_or_default(
            "hm_h",
            min_value=0,
            max_value=23,
        ),
        hm_m=int_or_default(
            "hm_m",
            min_value=0,
            max_value=59,
        ),
        ms_m=int_or_default(
            "ms_m",
            min_value=0,
            max_value=59,
        ),
        ms_s=int_or_default(
            "ms_s",
            min_value=0,
            max_value=59,
        ),
        active_tab_in_QTabWidget=int_or_default("active_tab_in_QTabWidget"),
        cycle_intervals=str_or_default("cycle_intervals"),
        cycle_repetitions=int_or_default(
            "cycle_repetitions",
            min_value=1,
            max_value=99,
        ),
        cycle_endlessly=bool_or_default("cycle_endlessly"),
        current_interval=int_or_default("current_interval"),
        interval_duration=int_or_default("interval_duration"),
        cycle_left=int_or_default("cycle_left"),
    )
