# -*- mode: python ; coding: utf-8 -*-

datas = [
    ('Splash.jpg', '.'),
    ('VPN-Gui.ico', '.'),
    ('style.qss', '.'),
]

binaries = []
hiddenimports = ['psutil']

a = Analysis(
    ['ui_main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'customtkinter', 'pystray'],
    noarchive=False,
)

pyz = PYZ(a.pure)

splash = Splash(
    'Splash.jpg',
    binaries=a.binaries,
    datas=a.datas,
    text_pos=None,
    text_size=12,
    minify_script=True,
)

exe = EXE(
    pyz,
    a.scripts,
    splash,
    [],
    exclude_binaries=True,
    name='OpenVPN_UI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon='VPN-Gui.ico',
)

coll = COLLECT(
    exe,
    splash.binaries,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='OpenVPN_UI',
)