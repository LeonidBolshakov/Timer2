from __future__ import annotations

from dataclasses import asdict
from typing import Any

from . import functions as f
from . import settings_schema as shema
from .defaults import default_model
from .dto import DTO
from .settings_schema import CURRENT_SETTINGS_VERSION
from .model import Model


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
        cycle_intervals=f.cycle_intervals_list(dto.cycle_intervals),
        cycle_repetitions=dto.cycle_repetitions,
        endlessly=dto.endlessly,
        current_interval=dto.current_interval,
        interval_duration=dto.interval_duration,
        left=dto.left,
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
        cycle_intervals=f.cycle_intervals_to_display(model.cycle_intervals),
        cycle_repetitions=model.cycle_repetitions,
        endlessly=model.endlessly,
        current_interval=model.current_interval,
        interval_duration=model.interval_duration,
        left=model.left,
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

    base = dto_to_json_dict(defaults)

    base.update({key: data[key] for key in base if key in data})

    return DTO(
        version=CURRENT_SETTINGS_VERSION,
        file_melody=f._to_str(
            base["file_melody"],
        ),
        voice_interval=f._to_int(
            base["voice_interval"],
            min_value=shema.VOICE_INTERVAL_MIN,
            max_value=shema.VOICE_INTERVAL_MAX,
        ),
        beep_interval=f._to_int(
            base["beep_interval"],
            min_value=shema.BEEP_INTERVAL_MIN,
            max_value=shema.BEEP_INTERVAL_MAX,
        ),
        beep_period_in_final=f._to_int(
            base["beep_period_in_final"],
            min_value=shema.BEEP_PERIOD_IN_FINAL_MIN,
            max_value=shema.BEEP_PERIOD_IN_FINAL_MAX,
        ),
        restore_time=f._to_bool(
            base["restore_time"],
        ),
        hm_h=f._to_int(
            base["hm_h"],
            min_value=0,
            max_value=23,
        ),
        hm_m=f._to_int(
            base["hm_m"],
            min_value=0,
            max_value=59,
        ),
        ms_m=f._to_int(
            base["ms_m"],
            min_value=0,
            max_value=59,
        ),
        ms_s=f._to_int(
            base["ms_s"],
            min_value=0,
            max_value=59,
        ),
        cycle_intervals=f._to_str(base["cycle_intervals"]),
        cycle_repetitions=f._to_int(
            base["cycle_repetitions"],
            min_value=1,
            max_value=59,
        ),
        endlessly=f._to_bool(base["endlessly"]),
        current_interval=f._to_int(base["current_interval"]),
        interval_duration=f._to_int(base["interval_duration"]),
        left=f._to_int(base["left"]),
    )
