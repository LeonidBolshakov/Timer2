from .model import Model


def default_model() -> Model:
    """
    Возвращает настройки программы по умолчанию.
    Это единственный источник значений по умолчанию.
    """
    return Model(
        file_melody="_internal/default.mp3",
        voice_interval=10,
        beep_interval=3,
        beep_period_in_final=11,
        restore_time=False,
        hm_h=0,
        hm_m=0,
        ms_m=0,
        ms_s=0,
        active_tab_in_QTabWidget=0,
        cycle_intervals=list(),
        cycle_repetitions=3,
        endlessly=False,
        current_interval=0,
        interval_duration=0,
        left=0,
    )
