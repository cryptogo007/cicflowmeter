# CICFlowMeter — full project documentation

> **Using the application (students, researchers):** see **[USER_GUIDE.md](USER_GUIDE.md)** — step-by-step handbook, not a developer manual.

This document describes the **Python CICFlowMeter** project end to end: what it does, how it is organized, how to install and run it (CLI and Windows GUI), which network flow features it exports, and how the code works internally.

---

## Table of contents

1. [Overview](#1-overview)
2. [Project structure](#2-project-structure)
3. [Installation](#3-installation)
4. [Command-line interface (CLI)](#4-command-line-interface-cli)
5. [Desktop GUI (Windows)](#5-desktop-gui-windows)
6. [Flow features (output columns)](#6-flow-features-output-columns)
7. [Architecture](#7-architecture)
8. [Packaging and deployment](#8-packaging-and-deployment)
9. [Troubleshooting](#9-troubleshooting)
10. [References](#10-references)

---

## 1. Overview

### What is CICFlowMeter?

[CICFlowMeter](https://www.unb.ca/cic/research/applications.html#CICFlowMeter) is a tool from the Canadian Institute for Cybersecurity (UNB) that reads network traffic (live or from PCAP files) and groups packets into **flows** (e.g. one TCP connection). For each flow it computes many statistical **features** used in intrusion detection, traffic analysis, and machine learning.

This repository is a **Python implementation** of that idea. It is **not** Cisco NetFlow; it follows the feature set of the original Java CICFlowMeter.

### What this project provides

| Capability | CLI | GUI |
|------------|-----|-----|
| Convert a single PCAP/PCAPNG to CSV | Yes | Yes |
| Convert a folder of PCAPs (one CSV per file) | Yes | Yes |
| Merge a folder of PCAPs into one CSV | Yes | Yes |
| Live capture from a network interface | Yes | Yes |
| Output to CSV file | Yes | Yes |
| Output to HTTP URL (JSON POST per flow) | Yes | Yes |
| Subset of output columns (`--fields`) | Yes | Yes |
| Verbose debug logging | Yes | Yes |
| Live monitoring (packets, flows, log) | — | Yes |
| Standalone Windows `.exe` | — | Yes (PyInstaller) |

### Technology stack

| Component | Role |
|-----------|------|
| **Python 3.12+** | Runtime |
| **Scapy** | Packet capture and parsing (`AsyncSniffer`) |
| **NumPy / SciPy** | Statistics for inter-arrival times and aggregates |
| **requests** | HTTP output mode |
| **CustomTkinter** | Desktop GUI |
| **PyInstaller** | Windows executable build (dev dependency) |

### Version notes (0.4.x)

From version **0.4.0** onward, the project uses a custom `FlowSession` and Scapy’s `prn` callback on `AsyncSniffer` instead of Scapy’s built-in session system. Flow logic, feature extraction, and output are fully owned by this codebase. The **set of CSV columns is unchanged**; only the internal packet routing changed. See [CHANGELOG.md](CHANGELOG.md).

---

## 2. Project structure

### Repository layout

```
cicflowmeter/
├── README.md                 # Short intro and quick start (points here)
├── LICENSE                   # MIT license
├── pyproject.toml            # Package metadata, dependencies, entry points
├── uv.lock                   # Locked dependencies (if using uv)
│
├── docs/                     # All documentation (this folder)
│   ├── README.md             # Documentation index
│   ├── GETTING_STARTED.md    # Beginner setup and first runs
│   ├── BUILD_GUIDE.md        # Build CICFlowMeter.exe
│   ├── BACKEND_INTEGRATION.md# Servers, API mode, automation
│   ├── CLI_COOKBOOK.md       # CLI recipes
│   ├── DOCUMENTATION.md      # This file
│   ├── Offline_Install.md    # Offline Windows install guide
│   └── CHANGELOG.md          # Release history
│
├── examples/
│   └── flow_receiver.py      # Sample HTTP receiver for -u mode
│
├── src/
│   ├── cicflowmeter/         # Core library and CLI
│   │   ├── sniffer.py        # CLI, capture orchestration, batch jobs
│   │   ├── flow_session.py   # Scapy session: flows dict, GC, flush
│   │   ├── flow.py           # Per-flow state and feature assembly
│   │   ├── writer.py         # CSV and HTTP writers
│   │   ├── utils.py          # Logging, statistics helpers
│   │   ├── constants.py      # Timeouts and GC tuning
│   │   └── features/         # Feature calculators
│   │       ├── context/      # Flow keys and packet direction
│   │       ├── flow_bytes.py
│   │       ├── flag_count.py
│   │       ├── packet_count.py
│   │       ├── packet_length.py
│   │       ├── packet_time.py
│   │       └── response_time.py
│   │
│   └── cicflowmeter_gui/     # Windows desktop application
│       ├── __main__.py       # Entry: python -m cicflowmeter_gui
│       ├── app.py            # Main window and tabs
│       ├── worker.py         # Background jobs
│       └── platform_win.py   # Interfaces, admin/Npcap hints
│
├── packaging/
│   └── cicflowmeter-gui.spec # PyInstaller specification
│
├── scripts/
│   └── build-gui.ps1         # Build dist/CICFlowMeter.exe
│
├── offline_wheels/           # Optional: pre-downloaded wheels for offline install
├── build/                    # PyInstaller build artifacts (gitignored)
├── dist/                     # Built CICFlowMeter.exe (gitignored)
└── .venv/                    # Local virtualenv (gitignored, not required for .exe)
```

### Entry points

Defined in `pyproject.toml`:

| Command | Module | Purpose |
|---------|--------|---------|
| `cicflowmeter` | `cicflowmeter.sniffer:main` | Command-line tool |
| `cicflowmeter-gui` | `cicflowmeter_gui.__main__:main` | Desktop GUI |

### Core modules (brief)

| Module | Responsibility |
|--------|----------------|
| `sniffer.py` | Argument parsing; `create_sniffer()`, `run_sniffer()`, `process_directory()`, `process_directory_merged()` |
| `flow_session.py` | Receives each packet via `process()`; maintains `flows` dict; periodic garbage collection; `flush_flows()` at end |
| `flow.py` | `Flow` class: accumulates packets; `get_data()` builds the feature dictionary |
| `writer.py` | `CSVWriter` / `HttpWriter`; factory `output_writer_factory()` |
| `features/*` | Computes counts, lengths, times, flags, bytes, etc. from packet lists |

### GUI modules (brief)

| Module | Responsibility |
|--------|----------------|
| `app.py` | CustomTkinter UI: Convert tab, Live Capture tab, monitoring panel |
| `worker.py` | Runs jobs on a background thread; supports cancel via `threading.Event` |
| `platform_win.py` | Lists interfaces via Scapy; warns about Npcap and administrator rights |

---

## 3. Installation

**Starter guides (recommended before this section):**

- [GETTING_STARTED.md](GETTING_STARTED.md) — first install and first run  
- [BUILD_GUIDE.md](BUILD_GUIDE.md) — build `CICFlowMeter.exe` in detail  
- [BACKEND_INTEGRATION.md](BACKEND_INTEGRATION.md) — servers, APIs, automation  
- [CLI_COOKBOOK.md](CLI_COOKBOOK.md) — command recipes  

### Online install (developer or connected PC)

**Requirements:** Python 3.12+, Windows / Linux / macOS (live capture details vary by OS).

Using **uv** (recommended in upstream README):

```sh
git clone <your-repo-url>
cd cicflowmeter
uv sync
source .venv/bin/activate   # Linux/macOS
# .\.venv\Scripts\Activate.ps1   # Windows PowerShell
```

Using **pip**:

```sh
cd cicflowmeter
python -m venv .venv
.\.venv\Scripts\activate
pip install -e .
```

Verify:

```sh
cicflowmeter --help
cicflowmeter-gui
```

### Offline install (Windows, no internet)

Use the dedicated guide: **[Offline_Install.md](Offline_Install.md)**.

It covers Python 3.12.10, installing from the local `offline_wheels/` folder, verification, optional Npcap for live capture, and troubleshooting.

### GUI-only deployment (no `.venv` on target PC)

Build or copy **`dist/CICFlowMeter.exe`**. The executable is self-contained; **`.venv` is not required** to run it. You only need `.venv` (or another Python environment) to develop or rebuild the exe.

### Live capture prerequisites (Windows)

| Requirement | Why |
|-------------|-----|
| [Npcap](https://npcap.com/) | Kernel driver for packet capture |
| Run as **Administrator** | Usually required for sniffing |
| Correct **interface name** | Use GUI refresh or `scapy` interface list (not always `eth0` on Windows) |

Offline PCAP processing does **not** require Npcap or admin rights.

---

## 4. Command-line interface (CLI)

### Synopsis

```text
cicflowmeter [-h] (-i INTERFACE | -f FILE | -d DIRECTORY) (-c | -u)
             [--fields FIELDS] [--merge] [-v] OUTPUT
```

### Input (exactly one)

| Option | Description |
|--------|-------------|
| `-i`, `--interface` | Live capture on the given interface (e.g. `\Device\NPF_{...}` on Windows) |
| `-f`, `--file` | Offline: single `.pcap` or `.pcapng` file |
| `-d`, `--directory` | Offline: all `.pcap` / `.pcapng` files in a folder |

### Output mode (exactly one)

| Option | Description |
|--------|-------------|
| `-c`, `--csv` | Write flows to a CSV file (or output directory for batch mode) |
| `-u`, `--url` | POST each flow as JSON to the given URL |

### Other options

| Option | Description |
|--------|-------------|
| `OUTPUT` | CSV path, URL, or **output directory** when using `-d` |
| `--fields` | Comma-separated column names to include (default: all) |
| `--merge` | With `-d` only: single `merged_output.csv` for all PCAPs |
| `-v`, `--verbose` | Enable debug logging |
| `--rotate-minutes N` | **Live + CSV only:** new file every N minutes (`out.csv`, `out1.csv`, `out2.csv`, …) |

### Examples

**Single PCAP → CSV**

```sh
cicflowmeter -f capture.pcap -c flows.csv
```

**Folder → one CSV per PCAP**

```sh
cicflowmeter -d ./pcaps/ -c ./csv_out/
```

**Folder → one merged CSV**

```sh
cicflowmeter -d ./pcaps/ -c ./csv_out/ --merge
```

Creates `./csv_out/merged_output.csv`.

**Live capture → HTTP API**

```sh
cicflowmeter -i eth0 -u http://localhost:8080/predict
```

**Live capture — new CSV every 5 minutes**

```sh
cicflowmeter -i eth0 -c livepacket.csv --rotate-minutes 5
```

Creates `livepacket.csv`, then `livepacket1.csv`, `livepacket2.csv`, …

**Subset of columns**

```sh
cicflowmeter -f capture.pcap -c flows.csv --fields src_ip,dst_ip,src_port,dst_port,flow_duration
```

**Stop live capture:** `Ctrl+C` (flushes remaining flows).

### Packet filter

All capture modes use the BPF filter:

```text
ip and (tcp or udp)
```

Only IPv4 TCP/UDP traffic is analyzed. Other traffic is ignored.

---

## 5. Desktop GUI (Windows)

### Purpose

The GUI exposes the same operations as the CLI with a graphical workflow: file/folder pickers, interface dropdown, start/stop, and a live **monitoring** panel.

### Launch

| Method | Command / action |
|--------|------------------|
| Installed package | `cicflowmeter-gui` |
| Module | `python -m cicflowmeter_gui` |
| Standalone | Run `dist\CICFlowMeter.exe` |

### Tabs

#### Convert PCAP

| Control | Maps to CLI |
|---------|-------------|
| Single PCAP / Folder | `-f` / `-d` |
| Input / Output browse | Paths |
| Merge into single CSV | `-d` + `--merge` |
| Output type CSV / URL | `-c` / `-u` |
| Fields (optional) | `--fields` |
| Verbose | `-v` |
| Start conversion / Stop | Runs / cancels job |

#### Live Capture

| Control | Maps to CLI |
|---------|-------------|
| Interface + Refresh | `-i` |
| Output path or URL | `OUTPUT` with `-c` or `-u` |
| **CSV rotation** (minutes) | `--rotate-minutes` (CSV only) |
| Fields, Verbose | Same as CLI |
| Start capture / Stop | `-i` live job |

Warnings appear if Npcap is missing or the app is not elevated (admin).

**CSV rotation:** enable **New file every** and set minutes (e.g. `5`). The first segment uses the path you choose (`livepacket.csv`); after each interval the app flushes flows and continues in `livepacket1.csv`, `livepacket2.csv`, etc.

### Monitoring panel

Shown at the bottom during any job:

| Indicator | Meaning |
|-----------|---------|
| **Status** | Idle / Running / Stopping / Cancelled |
| **Packets** | Packets passed to flow logic (`FlowSession.packets_count`) |
| **Active flows** | Flows still in memory (not yet written) |
| **Flows written (segment)** | Flows written to the **current** CSV since last rotation |
| **Output file** | Path of the active CSV (updates on rotation) |
| **Activity log** | Messages from the job (same as CLI prints) |

Counters update most reliably for **single-file** and **live** jobs where one session is active for the whole run. Batch folder jobs mainly show progress in the log.

### Cancel behavior

**Stop** sets a cancel flag. The engine stops the sniffer, stops periodic garbage collection, and **flushes** remaining flows to the output (same idea as Ctrl+C in the CLI).

---

## 6. Flow features (output columns)

Each row in the CSV (or each HTTP POST body) is one **flow**. Columns are produced by `Flow.get_data()` in `flow.py`, using helper classes under `features/`.

### Column groups

#### Endpoints and protocol

| Column | Description |
|--------|-------------|
| `src_ip`, `dst_ip` | IPv4 addresses (forward direction of the flow) |
| `src_port`, `dst_port` | TCP/UDP ports |
| `protocol` | IP protocol number |

#### Time and duration

| Column | Description |
|--------|-------------|
| `timestamp` | Flow start time |
| `flow_duration` | Duration of the flow |
| `flow_byts_s`, `flow_pkts_s` | Bytes/s and packets/s for the whole flow |
| `fwd_pkts_s`, `bwd_pkts_s` | Forward / backward packets per second |

#### Packet and byte counts

| Column | Description |
|--------|-------------|
| `tot_fwd_pkts`, `tot_bwd_pkts` | Packet counts by direction |
| `totlen_fwd_pkts`, `totlen_bwd_pkts` | Total byte lengths by direction |
| `fwd_act_data_pkts` | Forward packets with payload |

#### Packet length statistics

| Column | Description |
|--------|-------------|
| `fwd_pkt_len_max/min/mean/std` | Forward direction |
| `bwd_pkt_len_max/min/mean/std` | Backward direction |
| `pkt_len_max/min/mean/std/var` | Combined |
| `pkt_size_avg` | Average packet size |
| `fwd_header_len`, `bwd_header_len` | Header bytes |
| `fwd_seg_size_min` | Minimum forward segment size |

#### Inter-arrival times (IAT)

| Column | Description |
|--------|-------------|
| `flow_iat_mean/max/min/std` | Between all packets in the flow |
| `fwd_iat_tot/max/min/mean/std` | Forward direction |
| `bwd_iat_tot/max/min/mean/std` | Backward direction |

#### TCP flags

| Column | Description |
|--------|-------------|
| `fwd_psh_flags`, `bwd_psh_flags` | PSH per direction |
| `fwd_urg_flags`, `bwd_urg_flags` | URG per direction |
| `fin_flag_cnt`, `syn_flag_cnt`, `rst_flag_cnt` | FIN, SYN, RST counts |
| `psh_flag_cnt`, `ack_flag_cnt`, `urg_flag_cnt`, `ece_flag_cnt` | Other flags |

#### Window and activity

| Column | Description |
|--------|-------------|
| `init_fwd_win_byts`, `init_bwd_win_byts` | Initial TCP window sizes |
| `down_up_ratio` | Down/up packet ratio |
| `active_max/min/mean/std` | Active time statistics |
| `idle_max/min/mean/std` | Idle time statistics |

#### Bulk transfer metrics

| Column | Description |
|--------|-------------|
| `fwd_byts_b_avg`, `fwd_pkts_b_avg` | Forward bytes/packets per bulk |
| `bwd_byts_b_avg`, `bwd_pkts_b_avg` | Backward |
| `fwd_blk_rate_avg`, `bwd_blk_rate_avg` | Bulk rates |

#### Aliased / duplicate columns (compatibility)

These mirror other columns for compatibility with the original CICFlowMeter naming:

| Column | Same as |
|--------|---------|
| `fwd_seg_size_avg` | `fwd_pkt_len_mean` |
| `bwd_seg_size_avg` | `bwd_pkt_len_mean` |
| `cwr_flag_count` | `fwd_urg_flags` |
| `subflow_fwd_pkts` | `tot_fwd_pkts` |
| `subflow_bwd_pkts` | `tot_bwd_pkts` |
| `subflow_fwd_byts` | `totlen_fwd_pkts` |
| `subflow_bwd_byts` | `totlen_bwd_pkts` |

### Field filtering

Pass only the names you need:

```sh
--fields src_ip,dst_ip,flow_duration,tot_fwd_pkts
```

The GUI **Fields** box accepts the same comma-separated list. Empty means all columns.

---

## 7. Architecture

### Data flow (high level)

```text
  PCAP file or live interface
           │
           ▼
    Scapy AsyncSniffer
    (filter: ip and (tcp or udp))
           │
           ▼  prn callback
    FlowSession.process(packet)
           │
           ├──► Flow dict keyed by (flow_key, subflow_count)
           │         Flow.add_packet()
           │
           ├──► garbage_collect()  ──► OutputWriter.write(flow features)
           │         (idle/expired/FIN/periodic)
           │
           └──► flush_flows() at end  ──► remaining flows written
```

### Flow identification

`features/context/get_packet_flow_key()` builds a key from `(src_ip, dst_ip, src_port, dest_port)` in the **forward** or **reverse** direction. New flows are created when no matching entry exists. Multiple subflows on the same 4-tuple can appear when the flow is considered expired and restarted (`EXPIRED_UPDATE` in `constants.py`).

### Garbage collection and timeouts

Defined in `constants.py`:

| Constant | Value (seconds) | Role |
|----------|-----------------|------|
| `EXPIRED_UPDATE` | 240 | Gap after which a new subflow may start |
| `ACTIVE_TIMEOUT` | 5 | Active period tracking |
| `CLUMP_TIMEOUT` | 1 | Clumping |
| `PACKETS_PER_GC` | 1000 | Run GC every N packets |
| `GC_INTERVAL` | 1.0 | Background thread interval (`sniffer.py`) |

`garbage_collect()` writes flows that are idle long enough, have long duration, or ended with **FIN**. A background thread also calls `garbage_collect()` periodically during live capture.

### Output writers

| Mode | Class | Behavior |
|------|-------|----------|
| `csv` | `CSVWriter` | Creates file, writes header from first flow’s keys, appends rows, flushes after each row |
| `url` | `HttpWriter` | `POST` JSON body per flow with 5s timeout |

### Threading model

| Context | Threads |
|---------|---------|
| CLI / `run_sniffer()` | Scapy sniffer thread + GC daemon thread |
| GUI | Above + UI thread; `JobWorker` runs capture on a daemon worker thread; UI polls queues every 200 ms |

`FlowSession` uses a lock around the `flows` dictionary to avoid races with the GC thread.

### Programmatic use

You can call the library without the CLI:

```python
from cicflowmeter.sniffer import run_sniffer

run_sniffer(
    input_file="capture.pcap",
    output_mode="csv",
    output="flows.csv",
    verbose=False,
)
```

For cancel/logging, pass `should_cancel` and `log` callbacks (see `sniffer.py`).

---

## 8. Packaging and deployment

**Full build instructions:** [BUILD_GUIDE.md](BUILD_GUIDE.md) (prerequisites, pip vs uv, verify exe, troubleshooting, shipping).

### Build the Windows executable (summary)

From the project root (with dev dependencies installed):

```powershell
.\scripts\build-gui.ps1
```

Or:

```powershell
.\.venv\Scripts\python.exe -m PyInstaller packaging/cicflowmeter-gui.spec --noconfirm
```

Output: **`dist/CICFlowMeter.exe`** (single-file, windowed — no console).

### What to ship to end users

| Artifact | Needed? |
|----------|---------|
| `CICFlowMeter.exe` | Yes |
| Npcap installer | Only for live capture |
| Documentation | Optional: `docs/` or a PDF export |

Do **not** require `.venv`, Python, or source code on the target machine for exe-only deployment.

### Rebuilding after code changes

1. Recreate or use `.venv` and `pip install -e ".[dev]"` (or `uv sync --group dev`).
2. Run the build script again.
3. Replace the old `dist/CICFlowMeter.exe`.

---

## 9. Troubleshooting

### CLI / general

| Problem | Things to check |
|---------|------------------|
| Empty CSV | PCAP has no TCP/UDP over IPv4; check filter |
| Permission denied (live) | Run as admin; install Npcap (Windows) |
| Wrong interface | List interfaces in GUI or with Scapy |
| Partial CSV after stop | Expected: Stop/Ctrl+C flushes open flows |
| `--merge` error | Only valid with `-d` |

### GUI / exe

| Problem | Things to check |
|---------|------------------|
| Exe won’t start | Antivirus quarantine; build on same arch (64-bit) |
| Exe error after deleting `.venv` | Unrelated — exe is standalone; rebuild if exe itself is broken |
| No interfaces in dropdown | Install Npcap, click Refresh |
| Live capture fails | Admin + Npcap + correct interface |
| GUI frozen | Long job on worker thread should not freeze UI; report if it does |

### Offline install

See **[Offline_Install.md](Offline_Install.md)** § Troubleshooting.

---

## 10. References

1. UNB CICFlowMeter: https://www.unb.ca/cic/research/applications.html#CICFlowMeter  
2. Original Java implementation: https://github.com/ahlashkari/CICFlowMeter  
3. Npcap: https://npcap.com/  
4. Scapy documentation: https://scapy.readthedocs.io/

---

*Document version: matches project 0.4.2 (core) + GUI package 0.1.0. For release history see [CHANGELOG.md](CHANGELOG.md).*
