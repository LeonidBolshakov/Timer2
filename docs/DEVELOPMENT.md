# Разработка Timer 3

## Окружение

Основная среда проекта:

- Windows;
- Python 3.13;
- виртуальное окружение .venv;
- исходники в каталоге src;
- PyQt6 UI-файлы в _internal.

CI также использует Windows и Python 3.13.

## Подготовка проекта

    git clone https://github.com/LeonidBolshakov/Timer3.git
    cd Timer3
    py -3.13 -m venv .venv
    .venv\Scripts\python.exe -m pip install -U pip
    .venv\Scripts\python.exe -m pip install -r requirements-dev.txt
    .venv\Scripts\python.exe -m pip install -e .

requirements-dev.txt включает runtime-зависимости через ссылку на requirements.txt.

Проверка среды:

    .venv\Scripts\python.exe --version
    .venv\Scripts\python.exe -c "import PyQt6, pygame, pyttsx3"

## Запуск

Как установленный editable-пакет:

    .venv\Scripts\python.exe -m timer_3.main

Через вспомогательную точку входа:

    .venv\Scripts\python.exe run_timer.py

При отладке звука запускайте приложение в обычной пользовательской сессии Windows, а не в headless-окружении.

## Основные каталоги

| Каталог | Назначение |
| --- | --- |
| src/timer_3 | Код приложения |
| tests | Автоматические тесты |
| _internal | Qt UI, иконка, изображение и встроенная мелодия |
| docs | Документация и скриншоты |
| examples | Пример профиля настроек |
| .github/workflows | GitHub Actions |

Описание компонентов: [ARCHITECTURE.md](ARCHITECTURE.md).

## Ежедневные проверки

### Тесты

    run_tests.bat

или:

    .venv\Scripts\python.exe -m pytest -q tests --basetemp=.pytest_tmp

### Ruff

    .venv\Scripts\python.exe -m ruff check src tests

Безопасное автоматическое исправление части замечаний:

    .venv\Scripts\python.exe -m ruff check src tests --fix

### Форматирование

Проект хранит конфигурации Black и Ruff с длиной строки 88.

    .venv\Scripts\python.exe -m black --check src tests
    .venv\Scripts\python.exe -m black src tests

### Mypy

    .venv\Scripts\python.exe -m mypy src tests

### Компиляция

    .venv\Scripts\python.exe -m compileall src tests

Перед коммитом рекомендуется выполнить все четыре группы проверок.

## Покрытие

Coverage.py устанавливается отдельно:

    .venv\Scripts\python.exe -m pip install coverage
    .venv\Scripts\python.exe -m coverage run --source=timer_3 -m pytest
    .venv\Scripts\python.exe -m coverage report -m
    .venv\Scripts\python.exe -m coverage html

HTML-отчёт создаётся в htmlcov/index.html. Подробности: [TESTING.md](TESTING.md).

## Работа с UI

Файлы _internal/timer_3.ui и _internal/tunes.ui редактируются в Qt Designer.

После изменения objectName:

1. обновите аннотации виджетов в Timer_3 или TunesWindow;
2. обновите обращения в configurator и controller;
3. проверьте схемы FocusTransition;
4. обновите тестовые fake-виджеты;
5. запустите приложение и вручную проверьте Tab-порядок.

UI загружается динамически через PyQt6.uic.loadUi, поэтому компиляция .ui в Python не требуется.

## Работа с настройками

Единственный источник значений по умолчанию — defaults.default_model.

При изменении схемы синхронно обновляются:

- Model;
- DTO;
- ParamKeys для редактируемых полей;
- mapper в обоих направлениях;
- settings_schema;
- пример examples/settings.example.json;
- docs/SETTINGS.md;
- тесты модели, mapper и storage.

Не используйте абсолютные локальные пути как значения по умолчанию и не добавляйте рабочие пользовательские профили в репозиторий.

## Работа с ресурсами

Новый встроенный ресурс должен быть:

1. помещён в _internal;
2. указан относительным путём;
3. добавлен в timer_3.spec;
4. проверен через functions.resource_path;
5. проверен в собранном приложении.

Пользовательские абсолютные пути не включаются в сборку.

## Сборка

    build_exe.bat

Сценарий:

1. проверяет наличие .venv и timer_3.spec;
2. удаляет старые build и dist;
3. запускает PyInstaller с параметром --clean;
4. выводит путь к исполняемому файлу.

Результат:

    dist\timer_3\timer_3.exe

После сборки вручную проверьте:

- запуск без установленного Python;
- обе вкладки таймера;
- встроенную мелодию;
- пользовательский MP3;
- голосовое сообщение;
- чтение и запись профиля в %APPDATA%;
- повторный запуск и восстановление настроек.

## CI

Workflow .github/workflows/ci.yml запускается при push и pull request на windows-latest.

Этапы:

1. checkout;
2. установка Python 3.13;
3. установка requirements-dev.txt;
4. compileall;
5. pytest;
6. Ruff.

Mypy и сборка PyInstaller пока не выполняются в CI. Их следует проверять локально перед релизом.

## Правила изменений

- бизнес-логику размещайте в controller/model/storage, а не в классе окна;
- Qt-сигналы подключайте в configurator;
- файловые ошибки преобразуйте в предупреждения Storage;
- фатальные ошибки используйте только для нарушения внутреннего контракта;
- не выполняйте реальные аудиооперации в unit-тестах;
- для исправления регрессии сначала добавляйте воспроизводящий тест;
- документацию обновляйте вместе с поведением.

## Чек-лист pull request

- [ ] Новый сценарий покрыт тестами.
- [ ] Полный pytest проходит.
- [ ] Ruff, Black и mypy проходят.
- [ ] Не добавлены пользовательские JSON-файлы и абсолютные пути.
- [ ] Изменения UI проверены вручную.
- [ ] При изменении настроек обновлены пример и SETTINGS.md.
- [ ] README и профильные страницы docs не противоречат коду.
