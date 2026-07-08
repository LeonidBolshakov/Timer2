from enum import StrEnum


class ParamKeys(StrEnum):
    """Ключи пользовательских параметров таймера."""

    FILE_MELODY = "file_melody"
    VOICE_INTERVAL = "voice_interval"
    BEEP_INTERVAL = "beep_interval"
    BEEP_PERIOD_IN_FINAL = "beep_period_in_final"
    RESTORE_TIME = "restore_time"

    HM_H = "hm_h"
    HM_M = "hm_m"
    MS_M = "ms_m"
    MS_S = "ms_s"

    CYCLE_INTERVALS = "cycle_intervals"
    CYCLE_REPETITIONS = "cycle_repetitions"
    CYCLE_ENDLESSLY = "cycle_endlessly"

    CYCLE_LEFT = "cycle_left"
    CURRENT_INTERVAL = "current_interval"
    INTERVAL_DURATION = "interval_duration"


type TuneValue = str | int | bool | list[int]
