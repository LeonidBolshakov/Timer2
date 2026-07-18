from __future__ import annotations

import pytest

from timer_3 import model as model_module
from timer_3.defaults import default_model
from timer_3.param_keys import ParamKeys
from timer_3.time_input_mode import TimeInputMode


@pytest.mark.parametrize(
    ("key", "value", "attribute", "expected"),
    [
        (ParamKeys.FILE_MELODY, 123, "file_melody", "123"),
        (ParamKeys.VOICE_INTERVAL, "120", "voice_interval", 120),
        (ParamKeys.BEEP_INTERVAL, "30", "beep_interval", 30),
        (ParamKeys.BEEP_PERIOD_IN_FINAL, "20", "beep_period_in_final", 20),
        (ParamKeys.RESTORE_TIME, "yes", "restore_time", True),
        (ParamKeys.HM_H, "23", "hm_h", 23),
        (ParamKeys.HM_M, "59", "hm_m", 59),
        (ParamKeys.MS_M, "58", "ms_m", 58),
        (ParamKeys.MS_S, "57", "ms_s", 57),
        (ParamKeys.CYCLE_INTERVALS, [3, 5], "cycle_intervals", [3, 5]),
        (ParamKeys.CYCLE_ENDLESSLY, 1, "endlessly", True),
        (ParamKeys.CYCLE_REPETITIONS, "4", "cycle_repetitions", 4),
        (ParamKeys.ACTIVE_TAB_IN_QTABWIDGET, "1", "active_tab_in_QTabWidget", 1),
    ],
)
def test_set_value_updates_every_supported_setting(
    key: ParamKeys,
    value: object,
    attribute: str,
    expected: object,
) -> None:
    model = default_model()

    model.set_value(key, value)  # type: ignore[arg-type]

    assert getattr(model, attribute) == expected


def test_cycle_intervals_require_list(monkeypatch: pytest.MonkeyPatch) -> None:
    model = default_model()

    def fatal(_title: str, text: str) -> None:
        raise RuntimeError(text)

    monkeypatch.setattr(model_module.f, "inform_fatal_error_and_quit", fatal)

    with pytest.raises(RuntimeError, match="list"):
        model.set_value(ParamKeys.CYCLE_INTERVALS, "1 2")


@pytest.mark.parametrize(
    "key",
    [
        ParamKeys.CYCLE_LEFT,
        ParamKeys.CURRENT_INTERVAL,
        ParamKeys.INTERVAL_DURATION,
    ],
)
def test_runtime_only_keys_cannot_be_changed_through_settings(
    key: ParamKeys,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    model = default_model()

    def fatal(_title: str, text: str) -> None:
        raise RuntimeError(text)

    monkeypatch.setattr(model_module.f, "inform_fatal_error_and_quit", fatal)

    with pytest.raises(RuntimeError, match="Неизвестный ключ"):
        model.set_value(key, 1)


@pytest.mark.parametrize(
    ("values", "expected"),
    [
        ((0, 0, 0, 0), None),
        ((1, 0, 5, 0), TimeInputMode.HM),
        ((0, 0, 5, 0), TimeInputMode.MS),
        ((0, 0, 0, 7), TimeInputMode.MS),
    ],
)
def test_active_time_mode(
    values: tuple[int, int, int, int],
    expected: TimeInputMode | None,
) -> None:
    model = default_model()
    model.hm_h, model.hm_m, model.ms_m, model.ms_s = values

    assert model.active_time_mode is expected
