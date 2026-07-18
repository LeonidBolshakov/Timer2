from __future__ import annotations

import json
from pathlib import Path

import pytest

from timer_3.mapper import default_dto
from timer_3.storage import (
    ACTIVE_SETTINGS_FILE_NAME,
    ACTIVE_SETTINGS_KEY,
    Storage,
)


def test_pop_warnings_returns_copy_and_clears_storage(tmp_path: Path) -> None:
    storage = Storage(app_dir=tmp_path)
    storage.warnings.extend(["one", "two"])

    result = storage.pop_warnings()

    assert result[-2:] == ["one", "two"]
    assert storage.warnings == []


def test_switch_to_directory_keeps_current_settings_file(tmp_path: Path) -> None:
    storage = Storage(app_dir=tmp_path / "app")
    current = storage.settings_file
    directory = tmp_path / "not-a-file"
    directory.mkdir()

    dto = storage.switch_settings_file(directory)

    assert dto == default_dto()
    assert storage.settings_file == current
    assert any("не является файлом" in item for item in storage.pop_warnings())


def test_load_directory_path_falls_back_to_user_profile(tmp_path: Path) -> None:
    app_dir = tmp_path / "app"
    invalid = tmp_path / "directory"
    invalid.mkdir()
    storage = Storage(app_dir=app_dir)
    storage.settings_file = invalid

    dto = storage.load()

    assert dto == default_dto()
    assert storage.settings_file.name == "user.json"
    assert storage.settings_file.exists()
    registry = json.loads(
        (app_dir / ACTIVE_SETTINGS_FILE_NAME).read_text(encoding="utf-8")
    )
    assert registry[ACTIVE_SETTINGS_KEY] == str(storage.settings_file)


def test_save_records_warning_when_write_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    storage = Storage(app_dir=tmp_path)
    monkeypatch.setattr(storage, "_write_dto_to_file", lambda *_args: False)

    storage.save(default_dto())

    assert any("Не удалось сохранить файл" in item for item in storage.pop_warnings())


def test_registry_save_records_warning_when_write_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    storage = Storage(app_dir=tmp_path)
    monkeypatch.setattr(storage, "_write_json_file", lambda *_args: False)

    storage._save_active_settings_file(tmp_path / "profile.json")

    assert any("указатель активного файла" in item for item in storage.pop_warnings())


def test_write_json_rejects_directory_and_non_serializable_data(
    tmp_path: Path,
) -> None:
    storage = Storage(app_dir=tmp_path / "app")
    directory = tmp_path / "directory"
    directory.mkdir()

    assert storage._write_json_file({}, directory) is False
    assert storage._write_json_file({"bad": {1}}, tmp_path / "bad.json") is False


@pytest.mark.parametrize(
    ("registry_content", "warning_text"),
    [
        ("{broken", "повреждён"),
        ("[]", "некорректную структуру"),
        ("{}", None),
        (json.dumps({ACTIVE_SETTINGS_KEY: ""}), None),
    ],
)
def test_invalid_registry_falls_back_to_user_profile(
    tmp_path: Path,
    registry_content: str,
    warning_text: str | None,
) -> None:
    app_dir = tmp_path / "app"
    app_dir.mkdir()
    (app_dir / ACTIVE_SETTINGS_FILE_NAME).write_text(
        registry_content,
        encoding="utf-8",
    )

    storage = Storage(app_dir=app_dir)

    assert storage.settings_file.name == "user.json"
    warnings = storage.pop_warnings()
    if warning_text:
        assert any(warning_text in item for item in warnings)


def test_registry_directory_falls_back_with_warning(tmp_path: Path) -> None:
    app_dir = tmp_path / "app"
    (app_dir / ACTIVE_SETTINGS_FILE_NAME).mkdir(parents=True)

    storage = Storage(app_dir=app_dir)

    assert storage.settings_file.name == "user.json"
    assert any("не является файлом" in item for item in storage.pop_warnings())


def test_registry_with_invalid_utf8_falls_back_with_warning(tmp_path: Path) -> None:
    app_dir = tmp_path / "app"
    app_dir.mkdir()
    (app_dir / ACTIVE_SETTINGS_FILE_NAME).write_bytes(b"\xff\xfe")

    storage = Storage(app_dir=app_dir)

    assert storage.settings_file.name == "user.json"
    assert any("недоступен" in item for item in storage.pop_warnings())


def test_registry_uses_valid_custom_file(tmp_path: Path) -> None:
    app_dir = tmp_path / "app"
    app_dir.mkdir()
    custom = tmp_path / "custom.json"
    custom.write_text("{}", encoding="utf-8")
    (app_dir / ACTIVE_SETTINGS_FILE_NAME).write_text(
        json.dumps({ACTIVE_SETTINGS_KEY: str(custom)}),
        encoding="utf-8",
    )

    storage = Storage(app_dir=app_dir)

    assert storage.settings_file == custom.resolve()
