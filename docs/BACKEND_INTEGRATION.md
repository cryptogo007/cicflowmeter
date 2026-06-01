# Backend integration guide

CICFlowMeter is designed to run as a **backend processor**: headless CLI on servers, scheduled jobs, PCAP pipelines, or **streaming flows to your API** in real time. This guide covers production-style usage without the desktop GUI.

GUI and exe packaging: [GETTING_STARTED.md](GETTING_STARTED.md), [BUILD_GUIDE.md](BUILD_GUIDE.md).

---

## Table of contents

1. [Backend deployment models](#1-backend-deployment-models)
2. [CLI in production](#2-cli-in-production)
3. [HTTP URL mode (push flows to your API)](#3-http-url-mode-push-flows-to-your-api)
4. [Example flow receiver (Python)](#4-example-flow-receiver-python)
5. [Python API (embed in your app)](#5-python-api-embed-in-your-app)
6. [Batch and folder pipelines](#6-batch-and-folder-pipelines)
7. [Windows Task Scheduler](#7-windows-task-scheduler)
8. [Linux systemd service (live capture)](#8-linux-systemd-service-live-capture)
9. [Operational notes](#9-operational-notes)
10. [Security checklist](#10-security-checklist)

---

## 1. Backend deployment models

```text
  ┌──────────────┐     ┌─────────────────┐     ┌──────────────────┐
  │ PCAP files   │────►│  cicflowmeter   │────►│  flows.csv       │
  │ (storage)    │     │  (CLI / API)    │     │  or HTTP POST    │
  └──────────────┘     └─────────────────┘     └──────────────────┘
                              │
                              │ live -i
                              ▼
                       ┌──────────────┐
                       │ Network tap  │
                       │ (Npcap etc.) │
                       └──────────────┘
```

| Model | Input | Output | Typical use |
|-------|--------|--------|-------------|
| **Batch file** | Single PCAP | One CSV | Forensics, one-off analysis |
| **Batch folder** | Directory of PCAPs | Many CSVs or one merged CSV | Dataset preparation for ML |
| **Live stream** | Network interface | CSV append or HTTP per flow | IDS features, real-time scoring |
| **Embedded** | Your app supplies capture | Callbacks / writers | Custom platform integration |

The **core engine** is the same for CLI and GUI: `FlowSession` + `AsyncSniffer` in `cicflowmeter.sniffer`.

---

## 2. CLI in production

### Recommended install on a server

```bash
cd /opt/cicflowmeter
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e .
which cicflowmeter
```

On Windows Server:

```powershell
python -m venv C:\Apps\cicflowmeter\.venv
C:\Apps\cicflowmeter\.venv\Scripts\pip install -e C:\Apps\cicflowmeter
```

### Run headless (no GUI)

Only install the package; do not run `cicflowmeter-gui`. The CLI has no GUI dependency at runtime beyond what pip resolves (CustomTkinter is listed in main deps but unused by CLI).

### Exit codes and logging

- Successful completion: process exits **0**.
- Errors (missing file, bad args): Scapy/Python traceback, non-zero exit.
- Use **`-v`** for debug logs on stderr.
- Redirect output for cron:

  ```bash
  cicflowmeter -f /data/in/capture.pcap -c /data/out/flows.csv -v 2>>/var/log/cicflowmeter.log
  ```

### Idempotency

Each run **overwrites** the target CSV (writer opens with `"w"`). For pipelines, use unique output paths:

```text
/data/out/flows_20250601_120000.csv
```

---

## 3. HTTP URL mode (push flows to your API)

When you pass **`-u`** / `--url`, each completed flow is sent as:

- **Method:** `POST`
- **Body:** JSON object (keys = feature names, values = numbers/strings)
- **Timeout:** 5 seconds per request (`writer.py`)

### CLI example

```bash
cicflowmeter -i eth0 -u http://127.0.0.1:8080/v1/flows
```

Offline PCAP to API (processes file then posts each flow as it is garbage-collected):

```bash
cicflowmeter -f capture.pcap -u http://ml-service:8080/v1/flows
```

### What your API should implement

| Expectation | Detail |
|-------------|--------|
| Endpoint | Accept `POST` with `Content-Type: application/json` |
| Response | HTTP **2xx** (otherwise errors are logged, flow may be lost) |
| Rate | Can be high during busy capture; scale receiver or batch |
| Schema | One object per flow; fields match [DOCUMENTATION.md §6](DOCUMENTATION.md#6-flow-features-output-columns) |

### Field subset for ML

Reduce payload size:

```bash
cicflowmeter -i eth0 -u http://127.0.0.1:8080/predict \
  --fields src_ip,dst_ip,src_port,dst_port,flow_duration,tot_fwd_pkts,tot_bwd_pkts
```

---

## 4. Example flow receiver (Python)

Minimal receiver for testing URL mode. **Do not expose on the public internet without auth.**

Save as `examples/flow_receiver.py` (or run inline):

```python
"""Minimal HTTP receiver for cicflowmeter -u URL mode.
Run: python flow_receiver.py
Then: cicflowmeter -f sample.pcap -u http://127.0.0.1:8080/flows
"""
from http.server import BaseHTTPRequestHandler, HTTPServer
import json


class FlowHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        flow = json.loads(body)
        # TODO: enqueue to Kafka, write DB, call model, etc.
        print(f"flow {flow.get('src_ip')}:{flow.get('src_port')} -> "
              f"{flow.get('dst_ip')}:{flow.get('dst_port')} "
              f"duration={flow.get('flow_duration')}")
        self.send_response(200)
        self.end_headers()

    def log_message(self, format, *args):
        pass  # quiet


if __name__ == "__main__":
    HTTPServer(("127.0.0.1", 8080), FlowHandler).serve_forever()
```

### FastAPI variant (async-friendly)

```python
from fastapi import FastAPI, Request

app = FastAPI()

@app.post("/v1/flows")
async def ingest_flow(request: Request):
    flow = await request.json()
    # await queue.put(flow)
    return {"status": "ok"}
```

Run with `uvicorn` on the same host as cicflowmeter, then:

```bash
cicflowmeter -i eth0 -u http://127.0.0.1:8000/v1/flows
```

---

## 5. Python API (embed in your app)

Import the library from an installed package (`pip install -e .`):

```python
from cicflowmeter.sniffer import run_sniffer, process_directory, process_directory_merged

# Offline single file
run_sniffer(
    input_file="/data/capture.pcap",
    output_mode="csv",
    output="/data/flows.csv",
    verbose=False,
)

# With cancel + logging (long jobs)
cancelled = {"stop": False}

def should_cancel():
    return cancelled["stop"]

def log(msg: str):
    print(msg, flush=True)

run_sniffer(
    input_interface=r"\Device\NPF_{...}",
    output_mode="url",
    output="http://127.0.0.1:8080/flows",
    should_cancel=should_cancel,
    log=log,
    on_session=lambda s: setattr(store, "session", s),
)
```

### Access live stats

```python
stats = session.get_stats()
# {"packets": int, "active_flows": int, "flows_written": int}
```

### Lower-level control

```python
from cicflowmeter.sniffer import create_sniffer

sniffer, session = create_sniffer(
    input_file="capture.pcap",
    input_interface=None,
    output_mode="csv",
    output="flows.csv",
)
sniffer.start()
sniffer.join()
session.flush_flows()
```

Use `run_sniffer()` in production unless you need custom stop/join logic.

---

## 6. Batch and folder pipelines

### One CSV per PCAP

```bash
cicflowmeter -d /data/pcap_in/ -c /data/csv_out/
```

Output: `/data/csv_out/<stem>.csv` for each `.pcap` / `.pcapng`.

### Single merged dataset

```bash
cicflowmeter -d /data/pcap_in/ -c /data/csv_out/ --merge
```

Output: `/data/csv_out/merged_output.csv`.

### Shell pipeline example (Linux)

```bash
#!/bin/bash
set -euo pipefail
IN=/data/pcap
OUT=/data/flows
mkdir -p "$OUT"
source /opt/cicflowmeter/.venv/bin/activate
cicflowmeter -d "$IN" -c "$OUT" --merge
# Next: python train_model.py --input "$OUT/merged_output.csv"
```

### Python batch with logging

```python
from cicflowmeter.sniffer import process_directory

process_directory(
    "/data/pcap_in",
    "/data/csv_out",
    fields="src_ip,dst_ip,flow_duration",
    verbose=True,
    log=lambda m: print(m, flush=True),
    should_cancel=lambda: False,
)
```

---

## 7. Windows Task Scheduler

Automate nightly PCAP processing:

1. **Program:** `C:\Apps\cicflowmeter\.venv\Scripts\cicflowmeter.exe`  
   Or: `C:\Apps\cicflowmeter\.venv\Scripts\python.exe`  
2. **Arguments:** `-f D:\pcap\daily.pcap -c D:\out\daily_flows.csv`  
3. **Start in:** `C:\Apps\cicflowmeter`  
4. Run whether user is logged on or not (service account with read access to PCAP folder).

For **live capture**, the task must run elevated and Npcap must be installed; prefer a dedicated service account with admin rights (security tradeoff).

---

## 8. Linux systemd service (live capture)

Example unit (adjust interface and paths):

```ini
[Unit]
Description=CICFlowMeter live export
After=network.target

[Service]
Type=simple
User=netcap
WorkingDirectory=/opt/cicflowmeter
ExecStart=/opt/cicflowmeter/.venv/bin/cicflowmeter -i eth0 -c /var/lib/cicflowmeter/live.csv
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Notes:

- `User=` needs permission to capture (capabilities `CAP_NET_RAW` or run as root).
- Stopping the service should flush flows (SIGINT handling in `run_sniffer` / CLI).

---

## 9. Operational notes

### Performance

| Factor | Impact |
|--------|--------|
| PCAP size | Linear in packet count |
| Live traffic rate | CPU for Scapy dissection + feature math |
| HTTP mode | Network latency per flow; can bottleneck |
| `--fields` | Smaller CSV/JSON, slightly less work |

### Disk

- CSV grows with number of **flows**, not packets.
- `CSVWriter` flushes after each row (durable but I/O heavy).

### Monitoring

| Signal | How |
|--------|-----|
| Job finished | Process exit / Task Scheduler last run result |
| Row count | `wc -l flows.csv` (minus header) |
| Errors | `-v` logs, HTTP writer exceptions in stderr |
| Live throughput | Poll `session.get_stats()` if using Python API |

### .venv on production servers

**Keep `.venv`** on servers that run CLI from source. It is **not** required on machines that only run `CICFlowMeter.exe`.

---

## 10. Security checklist

| Topic | Guidance |
|-------|----------|
| Live capture | Requires privileged access; isolate capture hosts |
| HTTP URL mode | Bind receiver to `127.0.0.1` or internal VPC; use TLS + auth in production |
| PCAP paths | Restrict read access; PCAPs may contain sensitive data |
| CSV output | Treat as sensitive; encrypt at rest if needed |
| GUI exe | Distribute only from trusted build; scan for AV false positives |

---

## Related docs

- [CLI_COOKBOOK.md](CLI_COOKBOOK.md) — copy-paste command recipes  
- [GETTING_STARTED.md](GETTING_STARTED.md) — first-time setup  
- [DOCUMENTATION.md](DOCUMENTATION.md) — architecture and column reference  
