import pytest

from timer_2.tune_key import TuneKey
from timer_2.tunes_defaults import default_model


def test_get_value_returns_current_setting() -> None:
    model = default_model()
    model.set_value(TuneKey.VOICE_INTERVAL, 25)

    assert model.get_value(TuneKey.VOICE_INTERVAL) == 25


def test_set_file_melody_accepts_string_value() -> None:
    model = default_model()

    model.set_value(TuneKey.FILE_MELODY, "music/end.mp3")

    assert model.file_melody == "music/end.mp3"


def test_set_bool_value_from_supported_strings() -> None:
    model = default_model()

    model.set_value(TuneKey.RESTORE_TIME, "yes")
    assert model.restore_time is True

    model.set_value(TuneKey.RESTORE_TIME, "off")
    assert model.restore_time is False


def test_reject_empty_string_for_numeric_setting() -> None:
    model = default_model()

    with pytest.raises(ValueError):
        model.set_value(TuneKey.VOICE_INTERVAL, "")


def test_reject_invalid_bool_string() -> None:
    model = default_model()

    with pytest.raises(ValueError):
        model.set_value(TuneKey.RESTORE_TIME, "maybe")


def test_reject_bool_for_min_sec_setting() -> None:
    model = default_model()

    with pytest.raises(ValueError):
        model.set_value(TuneKey.MS_M, False)
