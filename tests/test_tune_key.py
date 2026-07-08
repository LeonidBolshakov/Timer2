from dataclasses import fields

from timer_3.param_keys import ParamKeys
from timer_3.dto import DTO


def test_tune_key_values_are_stable() -> None:
    assert ParamKeys.FILE_MELODY == "file_melody"
    assert ParamKeys.RESTORE_TIME == "restore_time"
    assert ParamKeys.MS_S == "ms_s"


def active_tab_in_QTabWidget() -> None:
    dto_fields = {field.name for field in fields(DTO)}
    tune_keys = {key.value for key in ParamKeys}
    print(sorted(dto_fields))
    print(sorted(tune_keys))
    assert tune_keys <= dto_fields
