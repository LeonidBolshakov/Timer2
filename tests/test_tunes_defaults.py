from timer_2.tunes_defaults import default_model
from timer_2.tunes_mapper import default_dto
from timer_2.tunes_schema import CURRENT_SETTINGS_VERSION


def test_default_dto_matches_default_model() -> None:
    model = default_model()
    dto = default_dto()

    assert dto.version == CURRENT_SETTINGS_VERSION
    assert dto.file_melody == model.file_melody
    assert dto.voice_interval == model.voice_interval
    assert dto.beep_interval == model.beep_interval
    assert dto.beep_period_in_final == model.beep_period_in_final
    assert dto.restore_time == model.restore_time
    assert dto.hm_h == model.hm_h
    assert dto.hm_m == model.hm_m
    assert dto.ms_m == model.ms_m
    assert dto.ms_s == model.ms_s
