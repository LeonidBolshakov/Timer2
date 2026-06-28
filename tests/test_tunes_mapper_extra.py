from timer_2.tunes_dto import TunesDTO
from timer_2.tunes_mapper import (
    default_dto,
    dto_to_json_dict,
    dto_to_model,
    json_dict_to_dto,
    model_to_dto,
)
from timer_2.tunes_schema import CURRENT_SETTINGS_VERSION


def test_dto_to_model_and_back_preserves_values() -> None:
    dto = TunesDTO(
        version=CURRENT_SETTINGS_VERSION,
        file_melody="custom.mp3",
        voice_interval=15,
        beep_interval=4,
        beep_period_in_final=12,
        restore_time=True,
        hm_h=1,
        hm_m=2,
        ms_m=3,
        ms_s=4,
    )

    model = dto_to_model(dto)
    result = model_to_dto(model)

    assert result == dto


def test_dto_to_json_dict_contains_only_json_fields() -> None:
    dto = default_dto()

    result = dto_to_json_dict(dto)

    assert result == {
        "version": CURRENT_SETTINGS_VERSION,
        "file_melody": dto.file_melody,
        "voice_interval": dto.voice_interval,
        "beep_interval": dto.beep_interval,
        "beep_period_in_final": dto.beep_period_in_final,
        "restore_time": dto.restore_time,
        "hm_h": dto.hm_h,
        "hm_m": dto.hm_m,
        "ms_m": dto.ms_m,
        "ms_s": dto.ms_s,
    }


def test_json_dict_to_dto_accepts_numeric_strings() -> None:
    dto = json_dict_to_dto(
        {
            "voice_interval": "17",
            "beep_interval": "5",
            "beep_period_in_final": "13",
            "hm_h": "2",
            "hm_m": "30",
            "ms_m": "4",
            "ms_s": "45",
        }
    )

    assert dto.voice_interval == 17
    assert dto.beep_interval == 5
    assert dto.beep_period_in_final == 13
    assert dto.hm_h == 2
    assert dto.hm_m == 30
    assert dto.ms_m == 4
    assert dto.ms_s == 45


def test_json_dict_to_dto_rejects_bool_for_numeric_fields() -> None:
    defaults = default_dto()

    dto = json_dict_to_dto(
        {
            "voice_interval": True,
            "hm_h": False,
        }
    )

    assert dto.voice_interval == defaults.voice_interval
    assert dto.hm_h == defaults.hm_h


def test_json_dict_to_dto_rejects_out_of_range_values() -> None:
    defaults = default_dto()

    dto = json_dict_to_dto(
        {
            "voice_interval": 60,
            "beep_interval": 0,
            "hm_h": 24,
            "hm_m": 60,
            "ms_m": -1,
            "ms_s": 60,
        }
    )

    assert dto.voice_interval == defaults.voice_interval
    assert dto.beep_interval == defaults.beep_interval
    assert dto.hm_h == defaults.hm_h
    assert dto.hm_m == defaults.hm_m
    assert dto.ms_m == defaults.ms_m
    assert dto.ms_s == defaults.ms_s


def test_json_dict_to_dto_rejects_non_string_file_melody() -> None:
    defaults = default_dto()

    dto = json_dict_to_dto({"file_melody": 123})

    assert dto.file_melody == defaults.file_melody
