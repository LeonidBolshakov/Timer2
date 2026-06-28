import pytest

from tune_key import TuneKey
from tunes_defaults import default_model


def test_default_model_contains_valid_values() -> None:
    model = default_model()

    assert model.file_melody == "_internal/default.mp3"
    assert model.voice_interval == 10
    assert model.beep_interval == 3
    assert model.beep_period_in_final == 11
    assert model.restore_time is False


def test_set_numeric_value_from_string() -> None:
    model = default_model()

    model.set_value(TuneKey.MS_S, "15")

    assert model.ms_s == 15


def test_reject_bool_for_numeric_setting() -> None:
    model = default_model()

    with pytest.raises(ValueError):
        model.set_value(TuneKey.MS_S, True)


def test_reject_number_out_of_range() -> None:
    model = default_model()

    with pytest.raises(ValueError):
        model.set_value(TuneKey.HM_H, 24)
