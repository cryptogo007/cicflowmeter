# Changelog

## [0.4.2] - 2026-06-01

### Added

- Windows desktop GUI (`cicflowmeter-gui`) with PCAP conversion, batch/merge, live capture, and monitoring panel.
- PyInstaller packaging (`dist/CICFlowMeter.exe`) and `scripts/build-gui.ps1`.
- Full project documentation under `docs/` (see `docs/DOCUMENTATION.md`).
- Starter docs: `GETTING_STARTED.md`, `BUILD_GUIDE.md`, `BACKEND_INTEGRATION.md`, `CLI_COOKBOOK.md`.
- End-user manual: `USER_GUIDE.md` for students and researchers (GUI, PCAP, live capture, CSV rotation).
- Example `examples/flow_receiver.py` for HTTP URL output mode.

### Changed

- `FlowSession` exposes `get_stats()` and `flows_written` for GUI monitoring.
- `sniffer.py` refactored with `run_sniffer()`, optional cancel/log callbacks for GUI jobs.
- Live CSV capture: optional rotation interval (`--rotate-minutes` / GUI) splits output into `base.csv`, `base1.csv`, `base2.csv`, …

## [0.4.0] - 2025-06-08
### Changed
- Major refactor: Now uses a custom FlowSession and the prn callback of AsyncSniffer for all flow processing, instead of relying on Scapy's DefaultSession/session system.
- All flow logic, feature extraction, and output are now fully managed by the project code, not by Scapy internals.
- The process method always returns None, preventing unwanted packet printing by Scapy.
- Logging is robust: only shows debug output if -v is set.
- All flows are always flushed at the end, even for small pcaps.

### Notes
- This project is a CICFlowMeter-like tool (see https://www.unb.ca/cic/research/applications.html#CICFlowMeter), not Cisco NetFlow. It extracts custom flow features as in the original Java CICFlowMeter.
- The refactor does not change the set of features/fields extracted, only how packets are routed to your logic.
