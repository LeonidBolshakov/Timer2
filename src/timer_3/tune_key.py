from enum import StrEnum


class TuneKey(StrEnum):
    """Ключи пользовательских настроек таймера."""

    FILE_MELODY = "file_melody"
    VOICE_INTERVAL = "voice_interval"
    BEEP_INTERVAL = "beep_interval"
    BEEP_PERIOD_IN_FINAL = "beep_period_in_final"
    RESTORE_TIME = "restore_time"
    HM_H = "hm_h"
    HM_M = "hm_m"
    MS_M = "ms_m"
    MS_S = "ms_s"
