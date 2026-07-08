from timer_3.param_keys import ParamKeys
from timer_3.defaults import default_model


def test_default_model_contains_valid_values() -> None:
    model = default_model()

    assert model.file_melody == "_internal/default.mp3"
    assert model.voice_interval == 10
    assert model.beep_interval == 3
    assert model.beep_period_in_final == 11
    assert model.restore_time is False


def test_set_numeric_value_from_string() -> None:
    model = default_model()

    model.set_value(ParamKeys.MS_S, "15")

    assert model.ms_s == 15
