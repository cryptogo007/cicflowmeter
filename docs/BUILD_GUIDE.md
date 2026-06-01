# Build guide — development setup and Windows `.exe`

This guide explains how to **set up a build machine**, install dependencies, run the project from source, and produce **`dist\CICFlowMeter.exe`** with PyInstaller. It expands the short packaging section in [DOCUMENTATION.md](DOCUMENTATION.md#8-packaging-and-deployment).

---

## Table of contents

1. [What you are building](#1-what-you-are-building)
2. [Build machine requirements](#2-build-machine-requirements)
3. [Development environment setup](#3-development-environment-setup)
4. [Run from source (CLI and GUI)](#4-run-from-source-cli-and-gui)
5. [Build the Windows executable](#5-build-the-windows-executable)
6. [Verify the executable](#6-verify-the-executable)
7. [Clean and rebuild](#7-clean-and-rebuild)
8. [Build troubleshooting](#8-build-troubleshooting)
9. [Shipping the build to other PCs](#9-shipping-the-build-to-other-pcs)
10. [Optional: build without uv](#10-optional-build-without-uv)

---

## 1. What you are building

| Output | Description |
|--------|-------------|
| **`dist\CICFlowMeter.exe`** | Single-file, windowed GUI (no console). Bundles Python, Scapy, NumPy, SciPy, CustomTkinter, and project code. |
| **CLI on PATH** | `cicflowmeter` and `cicflowmeter-gui` when installed editable in `.venv` |

The `.exe` is **only the GUI**. The CLI (`cicflowmeter`) is normally run via Python/venv on servers; you can also bundle a CLI exe with a separate PyInstaller spec if needed (not included by default).

**Important:** End users who only run `CICFlowMeter.exe` do **not** need `.venv` or Python installed.

---

## 2. Build machine requirements

| Item | Requirement |
|------|-------------|
| OS | Windows 10/11 **64-bit** (build host) |
| Python | **3.12.x** (same major version as `requires-python` in `pyproject.toml`) |
| Disk | ~500 MB free (venv + build cache + dist) |
| RAM | 4 GB+ recommended for PyInstaller |
| Internet | Required first time to download packages (unless using `offline_wheels/`) |

Tools installed into `.venv` by dev dependencies:

- **PyInstaller** ≥ 6.0  
- **pytest**, **ruff** (development only)

---

## 3. Development environment setup

### Step 1 — Clone or copy the repository

```powershell
cd "D:\Arlo\My Own Project\cicflowmeter"
```

### Step 2 — Create virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Step 3 — Install project + dev tools

**Using pip (recommended if `uv` is not installed):**

```powershell
pip install --upgrade pip
pip install -e .
pip install pyinstaller>=6.0
```

**Using uv:**

```powershell
uv sync --group dev
.\.venv\Scripts\Activate.ps1
```

### Step 4 — Confirm editable install

```powershell
pip show cicflowmeter
cicflowmeter --help
python -c "import cicflowmeter; import cicflowmeter_gui; print('imports OK')"
```

You should see package location under `src/` (editable install).

---

## 4. Run from source (CLI and GUI)

Always activate the venv first:

```powershell
.\.venv\Scripts\Activate.ps1
```

| Command | Purpose |
|---------|---------|
| `cicflowmeter -f test.pcap -c out.csv` | CLI |
| `cicflowmeter-gui` | GUI |
| `python -m cicflowmeter_gui` | GUI (alternate) |

---

## 5. Build the Windows executable

### Method A — build script (uses uv)

```powershell
.\scripts\build-gui.ps1
```

This runs `uv sync --group dev` then `uv run pyinstaller ...`. If `uv` is not on your PATH, use Method B or C.

### Method B — PyInstaller directly (pip)

From project root with `.venv` activated:

```powershell
python -m PyInstaller packaging/cicflowmeter-gui.spec --noconfirm
```

### Method C — manual copy of commands

```powershell
cd "D:\Arlo\My Own Project\cicflowmeter"
.\.venv\Scripts\Activate.ps1
python -m pip install pyinstaller
python -m PyInstaller packaging/cicflowmeter-gui.spec --noconfirm
```

### What the spec file does

File: `packaging/cicflowmeter-gui.spec`

| Setting | Value |
|---------|--------|
| Entry script | `src/cicflowmeter_gui/__main__.py` |
| `pathex` | `src/` (so `cicflowmeter` and `cicflowmeter_gui` import correctly) |
| `hiddenimports` | Scapy submodules, feature modules, CustomTkinter |
| `console` | `False` (GUI app, no terminal window) |
| Output name | `CICFlowMeter.exe` |
| Output dir | `dist/` |

Build artifacts also appear under `build/cicflowmeter-gui/` (safe to delete).

### Typical build time

First build: **1–3 minutes**. Later builds are faster if cache is warm.

---

## 6. Verify the executable

```powershell
Test-Path .\dist\CICFlowMeter.exe
Get-Item .\dist\CICFlowMeter.exe | Select-Object Name, Length, LastWriteTime
```

### Smoke test

1. Double-click `dist\CICFlowMeter.exe` (or run from PowerShell).
2. Confirm the window opens (Convert / Live Capture tabs).
3. Convert a small PCAP → CSV via the UI.
4. (Optional) Live capture with Npcap + admin.

### Test on a clean machine (recommended before release)

Copy **only** `CICFlowMeter.exe` to a PC that does **not** have Python or this repo. Confirm it starts. This validates the bundle.

---

## 7. Clean and rebuild

```powershell
Remove-Item -Recurse -Force build, dist -ErrorAction SilentlyContinue
python -m PyInstaller packaging/cicflowmeter-gui.spec --noconfirm
```

After upgrading dependencies:

```powershell
pip install -e . --upgrade
python -m PyInstaller packaging/cicflowmeter-gui.spec --noconfirm
```

---

## 8. Build troubleshooting

| Problem | Likely cause | What to do |
|---------|--------------|------------|
| `uv` not recognized | uv not installed | Use Method B (pip + PyInstaller) |
| `ModuleNotFoundError: cicflowmeter` | Spec `pathex` wrong or not installed | Run from repo root; `pip install -e .` |
| `ModuleNotFoundError: scapy...` | Hidden import missing | Add module to `hiddenimports` in `.spec`, rebuild |
| Huge exe (>150 MB) | Normal | Includes Python + NumPy + SciPy + Scapy |
| Exe starts then closes | Runtime error | Temporarily set `console=True` in spec to see traceback, rebuild |
| Antivirus blocks exe | False positive | Sign exe or allowlist; build on clean machine |
| `script ... not found` | Wrong `SPECPATH` / root | Run PyInstaller from repo root; spec uses `Path(SPECPATH).parent` as root |
| Old behavior after code change | Stale build | Delete `build/` and `dist/`, rebuild |

### Debug build with console

In `packaging/cicflowmeter-gui.spec`, change:

```python
console=True,
```

Rebuild, run exe from a terminal to see errors. Set back to `False` for release.

---

## 9. Shipping the build to other PCs

### Minimum package for GUI users

```text
CICFlowMeter.exe
README or link to docs/GETTING_STARTED.md
```

Optional:

- Npcap installer (for live capture only)
- Short PDF: “Run as administrator for live capture”

### Do not ship

- `.venv/` (not needed)
- Full source (not needed for exe-only users)

### Version labeling

Record in release notes:

- Git commit or tag  
- Python version used to build  
- Build date  
- File size / hash of `CICFlowMeter.exe`  

---

## 10. Optional: build without uv

Update `scripts/build-gui.ps1` locally or run manually:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -e .
pip install pyinstaller
python -m PyInstaller packaging/cicflowmeter-gui.spec --noconfirm
```

For **offline build machines**, install from `offline_wheels/` first (see [Offline_Install.md](Offline_Install.md)), then install PyInstaller wheel if you included it in the bundle.

---

## Related docs

- [GETTING_STARTED.md](GETTING_STARTED.md) — first-time user path  
- [BACKEND_INTEGRATION.md](BACKEND_INTEGRATION.md) — CLI on servers (no exe required)  
- [DOCUMENTATION.md](DOCUMENTATION.md) — full technical reference  
