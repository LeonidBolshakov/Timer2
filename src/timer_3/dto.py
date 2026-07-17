from dataclasses import dataclass


@dataclass(slots=True)
class DTO:
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
    active_tab_in_QTabWidget: int
    cycle_intervals: str
    cycle_Repetitions: int
    cycle_endlessly: bool

    current_interval: int
    interval_duration: int
    cycle_left: int
