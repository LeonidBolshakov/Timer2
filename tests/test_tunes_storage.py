from __future__ import annotations

import json
from pathlib import Path

import pytest

from timer_3.tunes_mapper import default_dto, dto_to_json_dict
from timer_3.tunes_storage import (
    ACTIVE_SETTINGS_FILE_NAME,
    ACTIVE_SETTINGS_KEY,
    TunesStorage,
)


@pytest.fixture(autouse=True)
def isolated_appdata(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setenv("APPDATA", str(tmp_path))
    return tmp_path


def test_load_missing_user_file_returns_defaults_and_creates_file() -> None:
    storage = TunesStorage()

    dto = storage.load()

    assert dto == default_dto()
    assert storage.settings_file.exists()

    saved_text = storage.settings_file.read_text(encoding="utf-8")
    saved_data = json.loads(saved_text)
    assert saved_data == dto_to_json_dict(default_dto())

    assert storage.pop_warnings()


def test_save_writes_current_settings_file() -> None:
    storage = TunesStorage()
    dto = default_dto()
    dto.voice_interval = 22

    storage.save(dto)

    data = json.loads(storage.settings_file.read_text(encoding="utf-8"))
    assert data["voice_interval"] == 22
    assert data["version"] == dto.version


def test_load_existing_valid_settings_file() -> None:
    storage = TunesStorage()
    dto = default_dto()
    dto.beep_interval = 7
    storage.save(dto)

    reloaded = TunesStorage().load()

    assert reloaded.beep_interval == 7


def test_load_invalid_json_returns_defaults_and_warning() -> None:
    storage = TunesStorage()
    storage.settings_file.parent.mkdir(parents=True, exist_ok=True)
    storage.settings_file.write_text("{broken json", encoding="utf-8")

    dto = storage.load()

    assert dto == default_dto()
    assert any("повреждён" in warning for warning in storage.pop_warnings())


def test_load_non_dict_json_returns_defaults_and_warning() -> None:
    storage = TunesStorage()
    storage.settings_file.parent.mkdir(parents=True, exist_ok=True)
    storage.settings_file.write_text("[]", encoding="utf-8")

    dto = storage.load()

    assert dto == default_dto()

    warnings = storage.pop_warnings()
    assert any("некорректную структуру" in warning for warning in warnings)


def test_switch_settings_file_updates_registry_and_saves_selected_file(
    tmp_path: Path,
) -> None:
    storage = TunesStorage()
    new_settings_file = tmp_path / "custom" / "profile.json"

    dto = storage.switch_settings_file(new_settings_file)

    registry_file = tmp_path / "Timer_3" / ACTIVE_SETTINGS_FILE_NAME
    registry = json.loads(registry_file.read_text(encoding="utf-8"))

    assert dto == default_dto()
    assert storage.settings_file == new_settings_file.resolve()
    assert registry[ACTIVE_SETTINGS_KEY] == str(new_settings_file.resolve())
    assert new_settings_file.exists()


def test_broken_active_registry_falls_back_to_default(
    tmp_path: Path,
) -> None:
    app_dir = tmp_path / "Timer_3"
    app_dir.mkdir(parents=True)
    (app_dir / ACTIVE_SETTINGS_FILE_NAME).write_text("[]", encoding="utf-8")

    storage = TunesStorage()

    assert storage.settings_file.name == "user.json"
