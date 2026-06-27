from __future__ import annotations

from dataclasses import asdict
from typing import Any

from tunes_defaults import default_model
from tunes_dto import TunesDTO
from tunes_schema import CURRENT_SETTINGS_VERSION
from tunes_model import TunesModel


def dto_to_model(dto: TunesDTO) -> TunesModel:
    return TunesModel(
        file_melody=dto.file_melody,
        voice_interval=dto.voice_interval,
        beep_interval=dto.beep_interval,
        beep_period_in_final=dto.beep_period_in_final,
        restore_time=dto.restore_time,
        hm_h=dto.hm_h,
        hm_m=dto.hm_m,
        ms_m=dto.ms_m,
        ms_s=dto.ms_s,
    )


def default_dto() -> TunesDTO:
    """
    DTO по умолчанию для записи в JSON.
    """
    return model_to_dto(default_model())


def model_to_dto(model: TunesModel) -> TunesDTO:
    return TunesDTO(
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
    )


def dto_to_json_dict(dto: TunesDTO) -> dict[str, Any]:
    return asdict(dto)


def json_dict_to_dto(data: object) -> TunesDTO:
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

    return TunesDTO(
        version=CURRENT_SETTINGS_VERSION,
        file_melody=_to_str(
            base["file_melody"],
            default=defaults.file_melody,
        ),
        voice_interval=_to_int(
            base["voice_interval"],
            default=defaults.voice_interval,
            min_value=1,
            max_value=59,
        ),
        beep_interval=_to_int(
            base["beep_interval"],
            default=defaults.beep_interval,
            min_value=1,
            max_value=59,
        ),
        beep_period_in_final=_to_int(
            base["beep_period_in_final"],
            default=defaults.beep_period_in_final,
            min_value=1,
            max_value=59,
        ),
        restore_time=_to_bool(
            base["restore_time"],
            default=defaults.restore_time,
        ),
        hm_h=_to_int(
            base["hm_h"],
            default=defaults.hm_h,
            min_value=0,
            max_value=23,
        ),
        hm_m=_to_int(
            base["hm_m"],
            default=defaults.hm_m,
            min_value=0,
            max_value=59,
        ),
        ms_m=_to_int(
            base["ms_m"],
            default=defaults.ms_m,
            min_value=0,
            max_value=59,
        ),
        ms_s=_to_int(
            base["ms_s"],
            default=defaults.ms_s,
            min_value=0,
            max_value=59,
        ),
    )


def _to_str(value: object, *, default: str) -> str:
    if isinstance(value, str):
        return value
    return default


def _to_int(value: object, *, default: int, min_value: int, max_value: int) -> int:
    """
    Безопасно преобразует JSON-значение в int.

    Принимает только int и str с целым числом.
    bool не принимается, потому что bool является подклассом int.
    """
    result: int

    if isinstance(value, bool):
        return default

    if isinstance(value, int):
        result = value
    elif isinstance(value, str):
        text = value.strip()
        if not text:
            return default
        try:
            result = int(text)
        except ValueError:
            return default
    else:
        return default

    if not min_value <= result <= max_value:
        return default

    return result


def _to_bool(value: object, *, default: bool) -> bool:
    if isinstance(value, bool):
        return value

    if isinstance(value, int):
        if value in (0, 1):
            return bool(value)
        return default

    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"1", "true", "yes", "on", "checked", "checkstate.checked"}:
            return True
        if normalized in {
            "0",
            "false",
            "no",
            "off",
            "unchecked",
            "checkstate.unchecked",
        }:
            return False

    return default
