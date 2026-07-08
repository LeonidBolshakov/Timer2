from timer_3.param_keys import ParamKeys
from timer_3.defaults import default_model


def test_set_file_melody_accepts_string_value() -> None:
    model = default_model()

    model.set_value(ParamKeys.FILE_MELODY, "music/end.mp3")

    assert model.file_melody == "music/end.mp3"


def test_set_bool_value_from_supported_strings() -> None:
    model = default_model()

    model.set_value(ParamKeys.RESTORE_TIME, "yes")
    assert model.restore_time is True

    model.set_value(ParamKeys.RESTORE_TIME, "off")
    assert model.restore_time is False
