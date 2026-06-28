# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['timer_2.py'],
    pathex=[],
    binaries=[
	('_internal\\default.mp3', '.'),
	('_internal\\glass.jpg', '.'),
],
    datas=[
	('_internal\\timer_2.ui', '.'),
	('_internal\\tunes.ui', '.'),
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
    name='timer_2',
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
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='timer_2',
)
