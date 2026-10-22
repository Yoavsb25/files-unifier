# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for macOS build of Files Unifier.
"""

import os
from pathlib import Path

block_cipher = None

# Get project root from current working directory (build script changes to project root before running)
project_root = Path(os.getcwd()).absolute()

# Collect data files (only include if they exist)
# Use absolute path resolution to avoid path issues
datas = []
try:
    # Resolve path relative to project root
    public_key_path = (project_root / 'pdf_merger' / 'licensing' / 'public_key.pem').resolve()
    if public_key_path.exists() and public_key_path.is_file():
        datas.append((str(public_key_path), 'pdf_merger/licensing'))
    else:
        print(f"Warning: Public key not found at {public_key_path}, license verification may not work.")
except Exception as e:
    print(f"Warning: Could not check for public key: {e}. License verification may not work.")

# Brand assets: runtime window/sidebar icon + bundle icon (tools/generate_brand_assets.py)
icon_png_path = (project_root / 'pdf_merger' / 'assets' / 'icon.png').resolve()
if icon_png_path.exists():
    datas.append((str(icon_png_path), 'pdf_merger/assets'))
icon_icns_path = project_root / 'build_config' / 'assets' / 'icon.icns'

# Resolve main.py path relative to project root
main_py_path = (project_root / 'main.py').resolve()
if not main_py_path.exists():
    raise FileNotFoundError(f"main.py not found at {main_py_path}")

a = Analysis(
    [str(main_py_path)],
    pathex=[str(project_root)],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'customtkinter',
        'PIL',
        'PIL.Image',
        'pypdf',
        'pandas',
        'openpyxl',
        'reportlab',
        'cryptography',
        'pdf_merger',
        'pdf_merger.licensing',
        'pdf_merger.ui',
        'pdf_merger.core',
        'pdf_merger.matching',
        'pdf_merger.observability',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Files Unifier',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUI application - no console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(icon_icns_path) if icon_icns_path.exists() else None,
)

app = BUNDLE(
    exe,
    name='Files Unifier.app',
    icon=str(icon_icns_path) if icon_icns_path.exists() else None,
    bundle_identifier='com.pdfmerger.batch',
    version='1.0.0',
    info_plist={
        'NSPrincipalClass': 'NSApplication',
        'NSHighResolutionCapable': 'True',
        'NSRequiresAquaSystemAppearance': 'False',
    },
)
