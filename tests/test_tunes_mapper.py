from timer_3.mapper import default_dto, json_dict_to_dto
from timer_3.settings_schema import CURRENT_SETTINGS_VERSION


def test_invalid_json_root_falls_back_to_defaults() -> None:
    assert json_dict_to_dto([]) == default_dto()


def test_unknown_json_keys_are_ignored() -> None:
    dto = json_dict_to_dto(
        {
            "voice_interval": 20,
            "unknown_key": "ignored",
        }
    )

    assert dto.version == CURRENT_SETTINGS_VERSION
    assert dto.voice_interval == 20
    assert not hasattr(dto, "unknown_key")


def test_invalid_values_are_replaced_by_defaults() -> None:
    dto = json_dict_to_dto(
        {
            "voice_interval": 0,
            "beep_interval": "not-a-number",
            "restore_time": "yes",
        }
    )
    defaults = default_dto()

    assert dto.voice_interval == defaults.voice_interval
    assert dto.beep_interval == defaults.beep_interval
    assert dto.restore_time == defaults.restore_time


def test_cycle_fields_are_loaded_from_new_names() -> None:
    dto = json_dict_to_dto(
        {
            "cycle_endlessly": True,
            "cycle_left": 7,
        }
    )

    assert dto.cycle_endlessly is True
    assert dto.cycle_left == 7
