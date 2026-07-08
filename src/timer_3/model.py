from __future__ import annotations

from dataclasses import dataclass

from . import functions as f
from .const import Const as C
from . import settings_schema as schema
from .param_keys import ParamKeys, TuneValue


@dataclass(slots=True)
class Model:
    file_melody: str
    voice_interval: int
    beep_interval: int
    beep_period_in_final: int
    restore_time: bool
    hm_h: int
    hm_m: int
    ms_m: int
    ms_s: int
    cycle_intervals: list[int]
    cycle_repetitions: int
    endlessly: bool
    current_interval: int
    interval_duration: int
    left: int

    def set_value(self, key: ParamKeys, value: TuneValue) -> None:
        match key:
            case ParamKeys.FILE_MELODY:
                self.file_melody = str(value)

            case ParamKeys.VOICE_INTERVAL:
                self.voice_interval = f._to_int(
                    value,
                    min_value=schema.VOICE_INTERVAL_MIN,
                    max_value=schema.VOICE_INTERVAL_MAX,
                )

            case ParamKeys.BEEP_INTERVAL:
                self.beep_interval = f._to_int(
                    value,
                    min_value=schema.BEEP_INTERVAL_MIN,
                    max_value=schema.BEEP_INTERVAL_MAX,
                )

            case ParamKeys.BEEP_PERIOD_IN_FINAL:
                self.beep_period_in_final = f._to_int(
                    value,
                    min_value=schema.BEEP_PERIOD_IN_FINAL_MIN,
                    max_value=schema.BEEP_PERIOD_IN_FINAL_MAX,
                )

            case ParamKeys.RESTORE_TIME:
                self.restore_time = f._to_bool(value)

            case ParamKeys.HM_H:
                self.hm_h = f._to_int(value, min_value=0, max_value=23)

            case ParamKeys.HM_M:
                self.hm_m = f._to_int(value, min_value=0, max_value=59)

            case ParamKeys.MS_M:
                self.ms_m = f._to_int(value, min_value=0, max_value=59)

            case ParamKeys.MS_S:
                self.ms_s = f._to_int(value, min_value=0, max_value=59)

            case ParamKeys.CYCLE_INTERVALS:
                if not isinstance(value, list):
                    f.inform_fatal_error_and_quit(
                        C.TITLE_INTERNAL_ERROR, C.TEXT_ERROR_CYCLE_INTERVALS
                    )
                self.cycle_intervals = value

            case ParamKeys.CYCLE_ENDLESSLY:
                self.endlessly = f._to_bool(value)

            case ParamKeys.CYCLE_REPETITIONS:
                self.cycle_repetitions = f._to_int(value)

            case _:
                f.inform_fatal_error_and_quit(
                    C.TITLE_INTERNAL_ERROR, f"Неизвестный ключ параметра: {key!r}"
                )
