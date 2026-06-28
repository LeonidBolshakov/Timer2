from timer_2.tune_key import TuneKey


def test_tune_key_values_are_stable() -> None:
    assert TuneKey.FILE_MELODY == "file_melody"
    assert TuneKey.RESTORE_TIME == "restore_time"
    assert TuneKey.MS_S == "ms_s"
