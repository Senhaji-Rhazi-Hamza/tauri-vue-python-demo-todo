# python_backend.spec
# ----------------------------------------
# PyInstaller spec for Sanic-based Tauri side-car backend
# ----------------------------------------

import sys
from pathlib import Path
from PyInstaller.utils.hooks import collect_all

app_name = "python_backend"          # final exe name
entry    = "main.py"                 # your backend entry script

# ---------------------------------------------------------
# Collect Sanic + Tracerite (code + data = css/templates…)
# ---------------------------------------------------------
sanic_pkg        = collect_all("sanic")
sanic_routing_pkg = collect_all("sanic_routing")
tracerite_pkg    = collect_all("tracerite")   # <- contains style.css

# -- Extra pkgs that do dynamic imports? add like this:
# other_pkg = collect_all("some_other")

# ---------------------------------------------------------
# Build
# ---------------------------------------------------------
block_cipher = None

a = Analysis(
    [str(Path(__file__).with_name(entry))],
    pathex=[str(Path(__file__).parent.resolve())],
    binaries=[],
    datas=(
        sanic_pkg.datas
        + sanic_routing_pkg.datas
        + tracerite_pkg.datas
        # + other_pkg.datas
    ),
    hiddenimports=(
        sanic_pkg.submodules
        + sanic_routing_pkg.submodules
        + tracerite_pkg.submodules
        # + other_pkg.submodules
    ),
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
    [],
    exclude_binaries=True,
    name=app_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,     # turn off if UPX unavailable
    console=True, # set False if you don’t want a console window
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=app_name,
)
