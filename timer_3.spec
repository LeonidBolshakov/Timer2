from pathlib import Path

project_root = Path.cwd()
src_dir = project_root / "src"

a = Analysis(
    ["run_timer.py"],
    pathex=[str(src_dir)],
    binaries=[],
    datas=[
        ("_internal\\default.mp3", "_internal"),
        ("_internal\\glass.jpg", "_internal"),
        ("_internal\\timer_3.ui", "_internal"),
        ("_internal\\tunes.ui", "_internal"),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="timer_3",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon="_internal\\glass.ico",
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="timer_3",
)