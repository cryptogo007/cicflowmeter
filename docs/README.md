# CICFlowMeter documentation

All project documentation lives in this folder. Choose a path by role:

---

## Start here (pick one)

| I am… | Start with |
|-------|------------|
| **Student / researcher** — using the app (GUI or exe) | **[USER_GUIDE.md](USER_GUIDE.md)** ← main handbook |
| **New user** — quick technical setup | **[GETTING_STARTED.md](GETTING_STARTED.md)** |
| **Operator** — build or ship `CICFlowMeter.exe` | **[BUILD_GUIDE.md](BUILD_GUIDE.md)** |
| **Backend / DevOps** — servers, APIs, automation | **[BACKEND_INTEGRATION.md](BACKEND_INTEGRATION.md)** |
| **Need a CLI command quickly** | **[CLI_COOKBOOK.md](CLI_COOKBOOK.md)** |
| **No internet on target PC** | **[Offline_Install.md](Offline_Install.md)** |
| **Want everything in one place** | **[DOCUMENTATION.md](DOCUMENTATION.md)** |

---

## Document index

### For application users

| Document | Description |
|----------|-------------|
| **[USER_GUIDE.md](USER_GUIDE.md)** | **Full user manual** — install, GUI walkthrough, PCAP & live capture, CSV results, troubleshooting (non-developers) |

### Starter and operations

| Document | Description |
|----------|-------------|
| **[GETTING_STARTED.md](GETTING_STARTED.md)** | Prerequisites, install, first PCAP, first GUI, first live capture, checklist |
| **[BUILD_GUIDE.md](BUILD_GUIDE.md)** | Dev setup, PyInstaller, build/verify/troubleshoot `CICFlowMeter.exe`, shipping |
| **[CLI_COOKBOOK.md](CLI_COOKBOOK.md)** | Copy-paste CLI recipes for scripts and servers |
| **[BACKEND_INTEGRATION.md](BACKEND_INTEGRATION.md)** | Headless CLI, HTTP URL mode, Python API, batch pipelines, Task Scheduler, systemd |
| **[Offline_Install.md](Offline_Install.md)** | Windows offline install from `offline_wheels/` |

### Reference

| Document | Description |
|----------|-------------|
| **[DOCUMENTATION.md](DOCUMENTATION.md)** | Full reference: structure, architecture, CLI/GUI, all flow columns |
| **[CHANGELOG.md](CHANGELOG.md)** | Version history |

### Code examples

| Path | Description |
|------|-------------|
| **[../examples/flow_receiver.py](../examples/flow_receiver.py)** | Minimal HTTP server for `-u` URL mode testing |

---

## Suggested reading order

### Path A — Student / researcher (GUI)

1. [USER_GUIDE.md](USER_GUIDE.md) (complete)  
2. [Offline_Install.md](Offline_Install.md) (if no internet)

### Path B — Analyst / quick technical start

1. [GETTING_STARTED.md](GETTING_STARTED.md) §1–5  
2. [BUILD_GUIDE.md](BUILD_GUIDE.md) §5–6 (if you need `.exe`)  
3. [DOCUMENTATION.md](DOCUMENTATION.md) §5 (GUI details)

### Path C — Backend / ML engineer

1. [GETTING_STARTED.md](GETTING_STARTED.md) §2, §4  
2. [CLI_COOKBOOK.md](CLI_COOKBOOK.md)  
3. [BACKEND_INTEGRATION.md](BACKEND_INTEGRATION.md)  
4. [DOCUMENTATION.md](DOCUMENTATION.md) §6–7 (features + architecture)

### Path D — Packager / IT

1. [BUILD_GUIDE.md](BUILD_GUIDE.md)  
2. [Offline_Install.md](Offline_Install.md) (air-gapped sites)  
3. [GETTING_STARTED.md](GETTING_STARTED.md) §9 (troubleshooting)

---

## Quick links (reference)

- [Project overview](DOCUMENTATION.md#1-overview)
- [Project structure](DOCUMENTATION.md#2-project-structure)
- [Flow features (CSV columns)](DOCUMENTATION.md#6-flow-features-output-columns)
- [Architecture](DOCUMENTATION.md#7-architecture)

Root [README.md](../README.md) — short project intro and quick commands.
