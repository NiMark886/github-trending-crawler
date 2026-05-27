# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for TrendingCrawler
"""

import sys
import os
from pathlib import Path

spec_dir = os.path.dirname(os.path.abspath(SPEC))

datas = [
    ('requirements.txt', '.'),
    ('LICENSE', '.'),
    ('README.md', '.'),
]

hiddenimports = [
    'requests',
    'bs4',
    'beautifulsoup4',
    'lxml',
    'deep_translator',
    'deep_translator.google_translator',
    'customtkinter',
    'json',
    'threading',
    'pathlib',
    'datetime',
    'typing',
]

a = Analysis(
    ['gui.py'],
    pathex=[spec_dir],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'test',
        'tests',
        'unittest',
        'pydoc',
        'doctest',
    ],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='TrendingCrawler',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',
)
