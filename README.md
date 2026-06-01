# Python CICFlowMeter

A Python implementation of [CICFlowMeter](https://www.unb.ca/cic/research/applications.html#CICFlowMeter): convert PCAP files or live network traffic into per-flow feature CSVs (or HTTP JSON), compatible with the original Java tool’s feature set.

**Current version:** 0.4.2 (core) · includes CLI, Windows desktop GUI, and standalone `.exe` build.

---

## Quick start

### Install (online)

```sh
git clone <repository-url>
cd cicflowmeter
python -m venv .venv
.\.venv\Scripts\activate          # Windows
pip install -e .
```

### CLI examples

```sh
# Single PCAP → CSV
cicflowmeter -f example.pcap -c flows.csv

# Folder of PCAPs → separate CSVs
cicflowmeter -d ./pcaps/ -c ./csv_output/

# Folder → one merged CSV
cicflowmeter -d ./pcaps/ -c ./csv_output/ --merge

# Live capture (admin + Npcap on Windows)
cicflowmeter -i <interface> -c live_flows.csv
```

### Desktop GUI (Windows)

```sh
cicflowmeter-gui
```

Or run **`dist/CICFlowMeter.exe`** after building (see below). Live capture needs [Npcap](https://npcap.com/) and usually **Run as administrator**.

### Build the `.exe`

```powershell
.\scripts\build-gui.ps1
```

Output: `dist/CICFlowMeter.exe` — does **not** require `.venv` on the machine where you only run the exe.

---

## Documentation

All documentation lives in **[docs/](docs/)**.

| Document | Description |
|----------|-------------|
| **[docs/USER_GUIDE.md](docs/USER_GUIDE.md)** | **User manual** for students & researchers (detailed, non-technical) |
| **[docs/GETTING_STARTED.md](docs/GETTING_STARTED.md)** | Quick install, first PCAP, GUI, checklist |
| **[docs/BUILD_GUIDE.md](docs/BUILD_GUIDE.md)** | Build `CICFlowMeter.exe` (PyInstaller, step-by-step) |
| **[docs/BACKEND_INTEGRATION.md](docs/BACKEND_INTEGRATION.md)** | Servers, HTTP API mode, Python API, automation |
| **[docs/CLI_COOKBOOK.md](docs/CLI_COOKBOOK.md)** | CLI command recipes |
| **[docs/DOCUMENTATION.md](docs/DOCUMENTATION.md)** | Full technical reference |
| **[docs/Offline_Install.md](docs/Offline_Install.md)** | Windows offline installation |
| **[docs/README.md](docs/README.md)** | Documentation index and reading paths |

---

## Highlights (v0.4.x)

- Custom `FlowSession` + Scapy `AsyncSniffer` `prn` callback (not Scapy’s default session)
- Offline PCAP, batch folder, merge mode, live interface capture
- CSV or HTTP URL output; optional `--fields` column filter
- Windows GUI with live monitoring and PyInstaller packaging

---

## References

1. https://www.unb.ca/cic/research/applications.html#CICFlowMeter  
2. https://github.com/ahlashkari/CICFlowMeter  

## License

MIT — see [LICENSE](LICENSE).
