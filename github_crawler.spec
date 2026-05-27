# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for GitHub Trending Crawler
"""

import sys
import os
from pathlib import Path

# Get the directory containing this spec file
spec_dir = os.path.dirname(os.path.abspath(SPEC))

# Define data files to include
datas = [
    ('github_trending_crawler.py', '.'),
    ('downloader.py', '.'),
    ('search.py', '.'),
    ('config.py', '.'),
    ('logger.py', '.'),
    ('proxy.py', '.'),
    ('database.py', '.'),
    ('display.py', '.'),
    ('visualization.py', '.'),
    ('interactive.py', '.'),
    ('cli.py', '.'),
    ('requirements.txt', '.'),
    ('LICENSE', '.'),
    ('README.md', '.'),
]

# Define hidden imports
hiddenimports = [
    'requests',
    'bs4',
    'beautifulsoup4',
    'lxml',
    'tqdm',
    'rich',
    'rich.console',
    'rich.table',
    'rich.progress',
    'rich.panel',
    'matplotlib',
    'matplotlib.pyplot',
    'matplotlib.dates',
    'json',
    'sqlite3',
    'threading',
    'pathlib',
    'datetime',
    'typing',
    'deep_translator',
    'deep_translator.google_translator',
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
    name='GitHub Trending Crawler',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon file path here if you have one
)
