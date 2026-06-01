# PyInstaller spec for the CICFlowMeter Windows GUI.
# Build from repo root:
#   uv run pyinstaller packaging/cicflowmeter-gui.spec

import sys
from pathlib import Path

block_cipher = None
root = Path(SPECPATH).resolve().parent
src = root / "src"

a = Analysis(
    [str(src / "cicflowmeter_gui" / "__main__.py")],
    pathex=[str(src)],
    binaries=[],
    datas=[],
    hiddenimports=[
        "scapy",
        "scapy.all",
        "scapy.layers",
        "scapy.layers.inet",
        "scapy.layers.l2",
        "scapy.arch",
        "scapy.arch.windows",
        "scapy.sendrecv",
        "scapy.interfaces",
        "customtkinter",
        "cicflowmeter",
        "cicflowmeter.sniffer",
        "cicflowmeter.flow_session",
        "cicflowmeter.writer",
        "cicflowmeter.flow",
        "cicflowmeter.features.context",
        "cicflowmeter.features.flag_count",
        "cicflowmeter.features.flow_bytes",
        "cicflowmeter.features.packet_count",
        "cicflowmeter.features.packet_length",
        "cicflowmeter.features.packet_time",
        "cicflowmeter.features.response_time",
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
    name="CICFlowMeter",
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
)
