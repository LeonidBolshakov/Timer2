from dataclasses import dataclass


@dataclass(slots=True)
class TunesDTO:
    """JSON-представление настроек. Только простые JSON-типы."""

    version: int
    file_melody: str
    voice_interval: int
    beep_interval: int
    beep_period_in_final: int
    restore_time: bool
    hm_h: int
    hm_m: int
    ms_m: int
    ms_s: int
