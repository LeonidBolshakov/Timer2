from __future__ import annotations

from dataclasses import dataclass
from typing import TypeAlias

from tune_key import TuneKey

TuneValue: TypeAlias = str | int | bool


@dataclass(slots=True)
class TunesModel:
    file_melody: str
    voice_interval: int
    beep_interval: int
    beep_period_in_final: int
    restore_time: bool
    hm_h: int
    hm_m: int
    ms_m: int
    ms_s: int

    def get_value(self, key: TuneKey) -> TuneValue:
        match key:
            case TuneKey.FILE_MELODY:
                return self.file_melody
            case TuneKey.VOICE_INTERVAL:
                return self.voice_interval
            case TuneKey.BEEP_INTERVAL:
                return self.beep_interval
            case TuneKey.BEEP_PERIOD_IN_FINAL:
                return self.beep_period_in_final
            case TuneKey.RESTORE_TIME:
                return self.restore_time
            case TuneKey.HM_H:
                return self.hm_h
            case TuneKey.HM_M:
                return self.hm_m
            case TuneKey.MS_M:
                return self.ms_m
            case TuneKey.MS_S:
                return self.ms_s

        raise KeyError(f"Неизвестный ключ настройки: {key!r}")

    def set_value(self, key: TuneKey, value: TuneValue | str) -> None:
        match key:
            case TuneKey.FILE_MELODY:
                self.file_melody = str(value)

            case TuneKey.VOICE_INTERVAL:
                self.voice_interval = _to_int(value, min_value=1, max_value=59)

            case TuneKey.BEEP_INTERVAL:
                self.beep_interval = _to_int(value, min_value=1, max_value=59)

            case TuneKey.BEEP_PERIOD_IN_FINAL:
                self.beep_period_in_final = _to_int(value, min_value=1, max_value=59)

            case TuneKey.RESTORE_TIME:
                self.restore_time = _to_bool(value)

            case TuneKey.HM_H:
                self.hm_h = _to_int(value, min_value=0, max_value=23)

            case TuneKey.HM_M:
                self.hm_m = _to_int(value, min_value=0, max_value=59)

            case TuneKey.MS_M:
                self.ms_m = _to_int(value, min_value=0, max_value=59)

            case TuneKey.MS_S:
                self.ms_s = _to_int(value, min_value=0, max_value=59)

            case _:
                raise KeyError(f"Неизвестный ключ настройки: {key!r}")


def _to_int(value: TuneValue | str, *, min_value: int, max_value: int) -> int:
    """
    Строго преобразует значение настройки в int.

    bool специально запрещён: в Python bool является подклассом int,
    но для числовых настроек таймера это ошибка ввода.
    """
    if isinstance(value, bool):
        raise ValueError("Логическое значение нельзя использовать как число")

    if isinstance(value, int):
        result = value
    elif isinstance(value, str):
        text = value.strip()
        if not text:
            raise ValueError("Пустая строка не является числом")
        result = int(text)
    else:
        raise ValueError(f"Нельзя преобразовать в int: {value!r}")

    if not min_value <= result <= max_value:
        raise ValueError(f"Значение {result} вне диапазона {min_value}..{max_value}")

    return result


def _to_bool(value: TuneValue | str) -> bool:
    if isinstance(value, bool):
        return value

    if isinstance(value, int):
        if value in (0, 1):
            return bool(value)
        raise ValueError(f"Нельзя преобразовать в bool: {value!r}")

    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on", "checked", "checkstate.checked"}:
        return True
    if normalized in {"0", "false", "no", "off", "unchecked", "checkstate.unchecked"}:
        return False

    raise ValueError(f"Нельзя преобразовать в bool: {value!r}")
