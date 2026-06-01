# Getting started — CICFlowMeter

This guide is for **new users** who want to run the project quickly on Windows (CLI or GUI), understand what they need installed, and know where to read next.

**Students and researchers using the desktop app:** use the full **[USER_GUIDE.md](USER_GUIDE.md)** instead — it is written for non-technical users with step-by-step tasks.

**Time to first CSV:** about 15–30 minutes (including Python setup).

---

## What you are running

CICFlowMeter is a **backend processing tool**: it reads network packets (from a PCAP file or a live network interface) and writes **one row per network flow** with many feature columns (CSV or HTTP JSON).

| You want to… | Best option |
|--------------|-------------|
| Try it once on a PCAP file | CLI (this guide, §5) |
| Click buttons, see live stats | GUI — [BUILD_GUIDE.md](BUILD_GUIDE.md) or pre-built `dist\CICFlowMeter.exe` |
| Automate on a server / pipeline | CLI + [BACKEND_INTEGRATION.md](BACKEND_INTEGRATION.md) |
| No Python on the target PC | Ship `CICFlowMeter.exe` — [BUILD_GUIDE.md](BUILD_GUIDE.md) |
| No internet on the target PC | [Offline_Install.md](Offline_Install.md) |

Deep reference: [DOCUMENTATION.md](DOCUMENTATION.md).

---

## 1. Prerequisites

### All users

| Requirement | Notes |
|-------------|--------|
| **Windows 10/11 64-bit** | Primary platform for GUI and offline guide |
| **Python 3.12.x** | Required for CLI/dev from source ([python.org](https://www.python.org/downloads/)) |
| **Project folder** | Full `cicflowmeter` repo (clone or USB copy) |

During Python install on Windows, enable **“Add python.exe to PATH”**.

### Only for live capture (`-i` / Live Capture tab)

| Requirement | Notes |
|-------------|--------|
| **[Npcap](https://npcap.com/)** | Packet capture driver |
| **Administrator** | Run terminal or GUI as admin |

**Not needed** for converting existing `.pcap` / `.pcapng` files.

---

## 2. Install the project (online)

Open **PowerShell** in the project folder (where `pyproject.toml` is).

### Option A — pip (works everywhere)

```powershell
cd "D:\Arlo\My Own Project\cicflowmeter"

python -m venv .venv
.\.venv\Scripts\Activate.ps1

pip install -e .
```

If script execution is blocked:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

### Option B — uv (if installed)

```powershell
uv sync
.\.venv\Scripts\Activate.ps1
```

### Verify

```powershell
cicflowmeter --help
cicflowmeter-gui
```

You should see CLI help text; the GUI window opens for `cicflowmeter-gui`.

---

## 3. Choose your interface

```text
                    ┌─────────────────────────────────────┐
                    │           CICFlowMeter core          │
                    │   (Scapy capture → flows → features) │
                    └─────────────────────────────────────┘
                           ▲              ▲
                           │              │
              ┌────────────┘              └────────────┐
              │                                      │
       ┌──────┴──────┐                      ┌────────┴────────┐
       │     CLI     │                      │  Desktop GUI   │
       │ cicflowmeter│                      │ cicflowmeter-gui│
       └─────────────┘                      │  or .exe       │
              │                             └────────────────┘
              │
              ▼
       Scripts, Task Scheduler,
       servers, ML pipelines
       (see BACKEND_INTEGRATION.md)
```

| Interface | When to use |
|-----------|-------------|
| **CLI** | Servers, automation, CI, scheduled jobs |
| **GUI** | Interactive use, demos, operators without command line |
| **Python API** | Custom apps embedding `run_sniffer()` — [BACKEND_INTEGRATION.md](BACKEND_INTEGRATION.md) |

---

## 4. First run — PCAP to CSV (CLI)

1. Get a sample PCAP (your own capture or a test file).
2. Activate the virtual environment:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

3. Run:

   ```powershell
   cicflowmeter -f "D:\path\to\capture.pcap" -c "D:\path\to\flows.csv"
   ```

4. Open `flows.csv` in Excel or any text editor. The first row is column names; each following row is one flow.

### Expected behavior

- Runs until the PCAP is fully read, then exits.
- Only **IPv4 TCP/UDP** traffic is included (other packets are ignored).
- If the CSV is empty, the PCAP may have no matching traffic.

### Try verbose mode

```powershell
cicflowmeter -f capture.pcap -c flows.csv -v
```

---

## 5. First run — GUI

**From source** (after install):

```powershell
.\.venv\Scripts\Activate.ps1
cicflowmeter-gui
```

**From executable** (no `.venv` needed):

```powershell
.\dist\CICFlowMeter.exe
```

If the exe does not exist yet, build it: **[BUILD_GUIDE.md](BUILD_GUIDE.md)**.

### Convert tab (quick steps)

1. Select **Single PCAP**.
2. **Browse** → choose your `.pcap` file.
3. **Browse** output → choose `flows.csv`.
4. Click **Start conversion**.
5. Watch the bottom panel (log + counters).

### Live Capture tab

1. Install Npcap; restart the app **as Administrator**.
2. **Refresh** interfaces; pick your adapter.
3. Set output CSV path.
4. **Start capture** → **Stop** when done (flows are flushed on stop).

---

## 6. First run — live capture (CLI)

Only after Npcap + admin:

```powershell
# List interfaces (Python one-liner)
.\.venv\Scripts\python.exe -c "from scapy.all import get_if_list; print('\n'.join(get_if_list()))"
```

Then (replace interface name):

```powershell
cicflowmeter -i "\Device\NPF_{...}" -c live_flows.csv
```

Stop with **Ctrl+C**. Open `live_flows.csv` to see flows written as connections end or time out.

More examples: [CLI_COOKBOOK.md](CLI_COOKBOOK.md).

---

## 7. Common next steps

| Goal | Read |
|------|------|
| More CLI examples (batch, merge, URL) | [CLI_COOKBOOK.md](CLI_COOKBOOK.md) |
| Build or rebuild `CICFlowMeter.exe` | [BUILD_GUIDE.md](BUILD_GUIDE.md) |
| Run on a server, cron, ML API | [BACKEND_INTEGRATION.md](BACKEND_INTEGRATION.md) |
| Install without internet | [Offline_Install.md](Offline_Install.md) |
| All CSV column meanings | [DOCUMENTATION.md §6](DOCUMENTATION.md#6-flow-features-output-columns) |
| How the code works | [DOCUMENTATION.md §7](DOCUMENTATION.md#7-architecture) |

---

## 8. Starter checklist

Copy and check off:

- [ ] Python 3.12 installed with PATH enabled  
- [ ] Project folder on disk  
- [ ] `.venv` created and `pip install -e .` succeeded  
- [ ] `cicflowmeter --help` works  
- [ ] Converted one PCAP to CSV  
- [ ] (Optional) GUI opens (`cicflowmeter-gui` or `.exe`)  
- [ ] (Optional) Npcap + admin + live capture tested  
- [ ] (Optional) Read [BACKEND_INTEGRATION.md](BACKEND_INTEGRATION.md) for server use  

---

## 9. Quick troubleshooting

| Symptom | Fix |
|---------|-----|
| `cicflowmeter` not recognized | Activate `.venv` or reinstall with `pip install -e .` |
| `Activate.ps1` blocked | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| Empty CSV | PCAP has no IPv4 TCP/UDP; try another file |
| Live capture fails | Npcap + Run as administrator + correct interface name |
| GUI exe missing | Follow [BUILD_GUIDE.md](BUILD_GUIDE.md) |
| Deleted `.venv`, exe still works | Normal — exe is standalone |

More detail: [DOCUMENTATION.md §9](DOCUMENTATION.md#9-troubleshooting).
