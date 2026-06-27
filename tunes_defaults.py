from tunes_model import TunesModel


def default_model() -> TunesModel:
    """
    Возвращает настройки программы по умолчанию.
    Это единственный источник значений по умолчанию.
    """
    return TunesModel(
        file_melody="_internal\\default.mp3",
        voice_interval=10,
        beep_interval=3,
        beep_period_in_final=11,
        restore_time=False,
        hm_h=0,
        hm_m=0,
        ms_m=0,
        ms_s=0,
    )
