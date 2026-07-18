from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from timer_3 import context as context_module
from timer_3.context import Context
from timer_3.param_keys import ParamKeys


class FakeStorage:
    def __init__(self) -> None:
        self.settings_file = Path("C:/settings/user.json")
        self.loaded = object()
        self.saved: list[object] = []
        self.switched_to: Path | None = None

    def load(self) -> object:
        return self.loaded

    def save(self, dto: object) -> None:
        self.saved.append(dto)

    def switch_settings_file(self, path: Path) -> object:
        self.switched_to = path
        return "switched-dto"


@pytest.fixture
def context(monkeypatch: pytest.MonkeyPatch) -> Context:
    monkeypatch.setattr(context_module, "Storage", FakeStorage)
    monkeypatch.setattr(
        context_module,
        "dto_to_model",
        lambda dto: SimpleNamespace(source=dto, set_value=lambda *_args: None),
    )
    return Context()


def test_context_loads_model_and_exposes_settings_file(context: Context) -> None:
    assert context.model.source is context.storage.loaded
    assert context.settings_file == Path("C:/settings/user.json")


def test_save_converts_model_to_dto(
    context: Context,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(context_module, "model_to_dto", lambda model: ("dto", model))

    context.save()

    assert context.storage.saved == [("dto", context.model)]


def test_switch_settings_file_replaces_model(
    context: Context,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        context_module,
        "dto_to_model",
        lambda dto: SimpleNamespace(source=dto),
    )
    new_path = Path("C:/settings/work.json")

    context.switch_settings_file(new_path)

    assert context.storage.switched_to == new_path
    assert context.model.source == "switched-dto"


@pytest.mark.parametrize("save", [False, True])
def test_set_value_saves_only_when_requested(
    context: Context,
    monkeypatch: pytest.MonkeyPatch,
    save: bool,
) -> None:
    set_calls: list[tuple[ParamKeys, int]] = []
    save_calls: list[bool] = []
    context.model.set_value = lambda key, value: set_calls.append((key, value))
    monkeypatch.setattr(context, "save", lambda: save_calls.append(True))

    context.set_value(ParamKeys.MS_S, 15, save=save)

    assert set_calls == [(ParamKeys.MS_S, 15)]
    assert save_calls == ([True] if save else [])
