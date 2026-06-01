# CICFlowMeter — User Guide

**For students, researchers, and anyone using the application**  
*(not a developer manual)*

This guide explains how to use **CICFlowMeter** on Windows: what it does, how to install it, how to convert capture files, how to record live network traffic, and how to work with the results in Excel or research tools.

---

## Table of contents

1. [What does this application do?](#1-what-does-this-application-do)
2. [What you need before you start](#2-what-you-need-before-you-start)
3. [Installing the application](#3-installing-the-application)
4. [Opening the application](#4-opening-the-application)
5. [Understanding the window](#5-understanding-the-window)
6. [Important ideas (read this once)](#6-important-ideas-read-this-once)
7. [Task A — Convert a PCAP file to CSV](#7-task-a--convert-a-pcap-file-to-csv)
8. [Task B — Convert many PCAP files at once](#8-task-b--convert-many-pcap-files-at-once)
9. [Task C — Record live network traffic](#9-task-c--record-live-network-traffic)
10. [Task D — Split long live captures into smaller files](#10-task-d--split-long-live-captures-into-smaller-files)
11. [Understanding your CSV results](#11-understanding-your-csv-results)
12. [Using results in your research](#12-using-results-in-your-research)
13. [Monitoring panel explained](#13-monitoring-panel-explained)
14. [Troubleshooting](#14-troubleshooting)
15. [Glossary](#15-glossary)
16. [Where to get more help](#16-where-to-get-more-help)

---

## 1. What does this application do?

Networks send data as small units called **packets**. Research and security tools often need a summary of **conversations** (connections) between computers, not every single packet.

**CICFlowMeter** reads network traffic and produces a **spreadsheet-style file (CSV)** where:

- **Each row** = one **flow** (one network conversation, such as a TCP connection).
- **Each column** = a **feature** (numbers describing that conversation: duration, packet counts, speeds, flags, etc.).

### Two ways to provide traffic

| Method | When to use it |
|--------|----------------|
| **PCAP file** | You already captured traffic (Wireshark, tcpdump, lab capture, dataset). |
| **Live capture** | You want to record traffic from your computer’s network adapter **right now**. |

### What this tool is **not**

- It is **not** Wireshark — you do not browse packets one by one in this app.
- It does **not** replace your antivirus or firewall.
- It is **not** a VPN or privacy tool.

It **turns traffic into a feature table** for analysis, machine learning, or coursework — similar in purpose to the well-known [UNB CICFlowMeter](https://www.unb.ca/cic/research/applications.html#CICFlowMeter) used in cybersecurity research.

---

## 2. What you need before you start

### For converting PCAP files only

| Requirement | Details |
|-------------|---------|
| **Windows 10 or 11** (64-bit) | Main supported platform for the desktop app |
| **CICFlowMeter.exe** | The application file (from your instructor, USB, or `dist` folder) |
| **A PCAP or PCAPNG file** | Your captured network data |
| **Disk space** | Enough room for the output CSV (often smaller than the PCAP, but large captures can still produce large CSVs) |

You do **not** need Npcap or administrator rights **only for opening existing PCAP files**.

### For live capture (recording traffic now)

| Requirement | Details |
|-------------|---------|
| Everything above | |
| **[Npcap](https://npcap.com/)** | Free driver; install with default options (restart if asked) |
| **Run as Administrator** | Right-click `CICFlowMeter.exe` → **Run as administrator** |
| **Permission** | Only capture networks you are **allowed** to monitor (your lab, your own machine, with consent) |

---

## 3. Installing the application

### Option 1 — You received `CICFlowMeter.exe` (most common)

1. Copy `CICFlowMeter.exe` to a folder you can find, for example:  
   `Documents\CICFlowMeter\CICFlowMeter.exe`
2. (Live capture only) Install **Npcap** from https://npcap.com/ if it is not already installed.
3. You do **not** need Python or any other install step.

**Note:** Windows may show “Windows protected your PC” for unsigned apps. If your instructor or lab provided the file, choose **More info** → **Run anyway**, or ask your IT department to allowlist the program.

### Option 2 — No internet PC (offline lab)

Follow the separate guide: **[Offline_Install.md](Offline_Install.md)** (for PCs that install from a USB bundle with Python and wheels).

### Option 3 — You are a developer building the exe yourself

See **[BUILD_GUIDE.md](BUILD_GUIDE.md)** — not required for normal users.

---

## 4. Opening the application

### For PCAP conversion (normal use)

1. Double-click **`CICFlowMeter.exe`**.
2. The window title should say **CICFlowMeter**.

### For live capture

1. Install **Npcap** (once per PC).
2. **Right-click** `CICFlowMeter.exe` → **Run as administrator**.
3. Click **Yes** if Windows asks for permission.

If the app opens but live capture fails, see [Section 14 — Troubleshooting](#14-troubleshooting).

---

## 5. Understanding the window

The window has **two tabs** at the top and a **monitoring area** at the bottom.

```text
┌─────────────────────────────────────────────────────────────┐
│  [ Convert PCAP ]  [ Live Capture ]                           │
│                                                             │
│   (settings and buttons for the selected tab)               │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  Status | Packets | Active flows | Flows written            │
│  Output file: ...                                           │
│  Activity log:                                              │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ messages appear here                                 │  │
│  └─────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

| Area | Purpose |
|------|---------|
| **Convert PCAP** tab | Turn saved capture file(s) into CSV |
| **Live Capture** tab | Record traffic from your network adapter into CSV |
| **Monitoring panel** | Shows progress, counts, current output file, and messages |
| **Start** button | Begins the job |
| **Stop** button (red) | Stops the job safely and saves open data |

While a job runs, **Start** is disabled and **Stop** is enabled. Wait until the log says the job finished before closing the app.

---

## 6. Important ideas (read this once)

### What is a “flow”?

A **flow** is one **network conversation** — for example, your browser talking to one web server on one port. Many packets belong to the same flow.

The application:

1. Groups packets into flows **in memory (RAM)**.
2. Calculates statistics (features).
3. Writes **one row per flow** to the CSV — **not** one row per packet.

So the CSV is a **summary table**, not a packet log.

### When does data go to the file?

| Situation | What happens |
|-----------|----------------|
| Converting a PCAP | When the file is fully processed (or when you press **Stop**). |
| Live capture | Rows appear over time as conversations finish or time out (often within about **90 seconds** of activity per chunk). |
| You press **Stop** | All open flows are saved to the current CSV. |
| **CSV rotation** enabled | Every N minutes, the app saves open flows, closes the file, and starts `name1.csv`, `name2.csv`, etc. |

You do **not** have to wait until a connection “closes” in the browser — the tool exports flows periodically during live capture.

### Why RAM matters during live capture

During live capture, busy networks create many open flows in memory. The app is designed to **write flows to disk regularly**, but very heavy traffic can still use a lot of RAM. Use **CSV rotation** (Section 10) for long recordings.

### Legal and ethical use

Only capture traffic you have **permission** to monitor (your own device, lab network, approved research). Unauthorized capture may violate policy or law.

---

## 7. Task A — Convert a PCAP file to CSV

**Goal:** You have `experiment.pcap` and want `experiment_flows.csv` for Excel or Python.

### Step-by-step

1. Open **CICFlowMeter** (double-click the exe).
2. Click the **Convert PCAP** tab (if not already selected).
3. Under **Input mode**, select **Single PCAP**.
4. Click **Browse…** next to **Input** and choose your `.pcap` or `.pcapng` file.
5. Click **Browse…** next to **Output** and choose where to save the CSV, for example:  
   `Documents\Results\experiment_flows.csv`
6. Under **Output type**, leave **CSV file** selected.
7. Leave **Fields** empty unless your instructor gave you a specific column list.
8. Leave **Verbose logging** unchecked unless you are debugging.
9. Click **Start conversion**.
10. Watch the bottom panel:
    - **Status** should show **Running**, then return to **Idle**.
    - The **Activity log** should show progress messages.
11. Open the CSV in Excel or LibreOffice Calc.

### Example settings (summary)

| Setting | Value |
|---------|--------|
| Input mode | Single PCAP |
| Input | `D:\Lab\captures\monday.pcap` |
| Output | `D:\Lab\results\monday_flows.csv` |
| Output type | CSV file |
| Merge | (unchecked) |

### If the CSV is empty or very small

- The PCAP may contain no **TCP/UDP over IPv4** traffic (the tool ignores other traffic).
- Try another capture file or ask your lab instructor to verify the PCAP.

### If conversion seems stuck

- Large PCAPs can take **many minutes** — watch **Packets** in the monitoring panel; if the number increases, it is working.
- Click **Stop** only if you need to cancel; partial results may be incomplete.

---

## 8. Task B — Convert many PCAP files at once

**Goal:** You have a folder with many `.pcap` files and want CSVs for each (or one combined file).

### B1 — One CSV per PCAP file

1. **Convert PCAP** tab.
2. **Input mode:** **Folder of PCAPs**.
3. **Browse** **Input** → select the folder with PCAP files.
4. **Browse** **Output** → select an **empty folder** where CSVs will be created.
5. Leave **Merge** **unchecked**.
6. Click **Start conversion**.

**Result:** For `trace1.pcap` you get `trace1.csv`, for `trace2.pcap` you get `trace2.csv`, and so on.

### B2 — One combined CSV for the whole folder

1. Same as B1, but check **Merge folder into single CSV (merged_output.csv)**.
2. Click **Start conversion**.

**Result:** One file: `merged_output.csv` in your output folder, containing flows from **all** PCAPs in the folder.

### Tips

- Only files ending in `.pcap` or `.pcapng` in that folder are processed (not subfolders).
- Use a dedicated output folder so you do not mix CSVs with PCAPs.

---

## 9. Task C — Record live network traffic

**Goal:** Record traffic from your Wi‑Fi or Ethernet adapter into a CSV while you run an experiment.

### Before you start (checklist)

- [ ] Npcap installed  
- [ ] App started **as Administrator**  
- [ ] You have permission to capture on this network  
- [ ] You know which adapter to use (often “Wi‑Fi” or “Ethernet”, not “Loopback”)

### Step-by-step

1. **Right-click** `CICFlowMeter.exe` → **Run as administrator**.
2. Open the **Live Capture** tab.
3. Read the **yellow warning** at the top. If it mentions Npcap or Administrator, fix that first.
4. **Interface:** Open the dropdown. If the list is empty or says “(no interfaces)”, click **Refresh**. If still empty, install Npcap and restart the app as admin.
5. Choose the adapter that matches your active connection (when unsure, ask lab staff).
6. **Output:** Click **Browse…** and choose a CSV path, e.g.  
   `Documents\Captures\live_session.csv`
7. **Output type:** **CSV file**.
8. **Fields:** leave empty unless instructed otherwise.
9. Click **Start capture**.
10. Run your experiment (visit websites, run your program, etc.).
11. When finished, click **Stop**.
12. Open the CSV file.

### What you should see while capturing

| Indicator | Meaning |
|-----------|---------|
| **Status: Running** | Capture is active |
| **Packets** increasing | Traffic is being processed |
| **Active flows** | Conversations still being tracked in memory |
| **Flows written (segment)** | Rows already saved to the current CSV file |
| **Output file** | Which CSV is being written now |
| **Activity log** | Messages (including file rotation if enabled) |

### Stopping safely

Always use **Stop** before closing the window. **Stop** saves flows that are still in memory. Closing the window during a run may ask you to stop first — choose **Yes** to stop and quit.

---

## 10. Task D — Split long live captures into smaller files

**Goal:** Avoid one huge CSV during a 2-hour lab session.

### How it works

You choose a base filename and an interval in **minutes**. Example: file `livepacket.csv`, interval **5** minutes.

| Time | File receiving data |
|------|---------------------|
| 0:00 – 5:00 | `livepacket.csv` |
| 5:00 – 10:00 | `livepacket1.csv` |
| 10:00 – 15:00 | `livepacket2.csv` |
| … | … |

When each interval ends, the app **saves open data**, **closes** the current file, and starts the next numbered file.

### Step-by-step

1. **Live Capture** tab (as administrator).
2. Set **Output** to your base path, e.g. `D:\Lab\livepacket.csv`.
3. **Output type** must be **CSV file** (rotation does not apply to HTTP URL mode).
4. Check **New file every**.
5. Enter minutes in the box, e.g. **5**.
6. Click **Start capture**.
7. The log will show messages when a new file is created.

### Choosing an interval

| Interval | Good for |
|----------|----------|
| **5 minutes** | Typical lab sessions, easier to open in Excel |
| **10–15 minutes** | Longer captures, fewer files |
| **1 minute** | Very careful size control; many files |

Shorter intervals = more files, smaller each. Longer intervals = fewer files, larger each.

---

## 11. Understanding your CSV results

### Opening the file

- **Microsoft Excel:** File → Open → select the `.csv`. If columns look wrong, use Data → From Text/CSV and choose comma separator.
- **LibreOffice Calc:** Open directly; confirm comma separation.
- **Python (pandas):** `pd.read_csv("flows.csv")`

### Structure

| Row 1 | Column names (`src_ip`, `dst_ip`, `flow_duration`, …) |
| Row 2+ | One flow per row |

### Columns you will use most often (plain language)

| Column | Meaning |
|--------|---------|
| `src_ip` | Source IP address |
| `dst_ip` | Destination IP address |
| `src_port` | Source port number |
| `dst_port` | Destination port (e.g. 443 for HTTPS) |
| `protocol` | Protocol number (6 = TCP, 17 = UDP in common captures) |
| `timestamp` | When the flow started (human-readable time) |
| `flow_duration` | How long the flow lasted (seconds) |
| `tot_fwd_pkts` | Packets in forward direction |
| `tot_bwd_pkts` | Packets in backward direction |
| `flow_byts_s` | Bytes per second for the flow |
| `flow_pkts_s` | Packets per second |
| `syn_flag_cnt`, `ack_flag_cnt`, … | TCP flag counts (used in many research papers) |

There are **many more columns** (80+). For coursework, your instructor may only require a subset. Leave **Fields** empty in the app to export **all** columns.

A full column list for advanced users is in **[DOCUMENTATION.md §6](DOCUMENTATION.md#6-flow-features-output-columns)**.

### One connection, multiple rows?

Yes. Long live connections may appear as **several rows** (several flow segments) as the tool exports chunks over time. That is normal.

---

## 12. Using results in your research

### Typical workflow

```text
Capture (Wireshark) → PCAP file → CICFlowMeter → CSV → Excel / Python / WEKA / ML tool
```

### Tips for students

1. **Name files clearly:** `group3_scenarioA_flows.csv`
2. **Keep the PCAP** as raw evidence; use CSV for statistics and plots.
3. **Check row count:** Zero or one row may mean an empty or very quiet capture.
4. **Document settings:** interface name, live vs PCAP, rotation interval, date/time.
5. **Compare fairly:** Same capture length and conditions when comparing experiments.

### Filtering columns in the app (optional)

If you only need a few columns, type them in **Fields (optional)**, comma-separated, for example:

```text
src_ip,dst_ip,src_port,dst_port,flow_duration,tot_fwd_pkts,tot_bwd_pkts
```

Leave empty to export everything.

### HTTP URL output (advanced)

**Output type → HTTP URL** sends each flow to a web address as JSON. This is for labs with a **prediction server**, not for typical spreadsheet work. Use **CSV file** unless your instructor says otherwise.

---

## 13. Monitoring panel explained

Available on both tabs during and after a job.

| Label | Meaning |
|-------|---------|
| **Status: Idle** | Ready to start |
| **Status: Running** | Job in progress |
| **Status: Stopping** | Stop requested; finishing up |
| **Packets** | Total packets processed |
| **Active flows** | Conversations still in memory (not yet written as rows) |
| **Flows written (segment)** | Rows written to the **current** output file since last rotation or start |
| **Output file** | Full path of the CSV being written (live capture / rotation) |
| **Activity log** | Step-by-step messages; read here if something fails |

---

## 14. Troubleshooting

### Application will not start

| Try this |
|----------|
| Right-click → **Run as administrator** |
| Allow the app in Windows Security / antivirus |
| Confirm you have the 64-bit exe on 64-bit Windows |
| Ask IT if the file was blocked |

### “No interfaces” on Live Capture

| Try this |
|----------|
| Install **Npcap** and reboot |
| Run the app **as Administrator** |
| Click **Refresh** |
| Disable and re-enable your Wi‑Fi/Ethernet adapter |

### Live capture runs but CSV stays empty

| Try this |
|----------|
| Generate traffic (open a website) while capturing |
| Confirm you selected the correct **interface** (not Loopback unless you test locally) |
| Wait at least 1–2 minutes; some flows export after activity ends |
| Click **Stop** before checking the file |

### PCAP conversion is very slow

| Try this |
|----------|
| Normal for large files — watch **Packets** increase |
| Close other heavy programs |
| Use **Fields** to export fewer columns if your assignment allows |

### CSV is huge / Excel freezes

| Try this |
|----------|
| Use **CSV rotation** for long live captures |
| Export fewer columns via **Fields** |
| Use Python or LibreOffice for very large files |
| Split work: convert one PCAP at a time |

### Many files: `live.csv`, `live1.csv`, `live2.csv`…

You enabled **New file every** rotation. That is expected. Combine in Python/Excel if you need one table, or disable rotation.

### Deleted `.venv` folder and exe stopped working

The **exe does not need `.venv`**. If the exe fails, rebuild or get a fresh `CICFlowMeter.exe` from your instructor. Deleting `.venv` only affects **developer** Python installs, not a standalone exe.

### Error message in a popup

Read the **Activity log** for details. Note what you clicked before the error and ask your instructor with a screenshot.

---

## 15. Glossary

| Term | Simple meaning |
|------|----------------|
| **Packet** | One small piece of network data |
| **Flow** | One conversation (connection) made of many packets |
| **PCAP** | A file that stores captured packets (from Wireshark, etc.) |
| **CSV** | Comma-separated spreadsheet file |
| **Feature** | A number describing a flow (duration, packet count, …) |
| **Interface** | Your network adapter (Wi‑Fi, Ethernet, …) |
| **Npcap** | Windows driver needed for live capture |
| **Live capture** | Recording traffic in real time |
| **Rotation** | Starting a new CSV file every N minutes during live capture |
| **Flush** | Saving data from memory to disk |

---

## 16. Where to get more help

| Topic | Document |
|-------|----------|
| **This guide** (using the app) | **USER_GUIDE.md** (you are here) |
| Offline Windows install | [Offline_Install.md](Offline_Install.md) |
| Technical / developer reference | [DOCUMENTATION.md](DOCUMENTATION.md) |
| Command-line (advanced) | [CLI_COOKBOOK.md](CLI_COOKBOOK.md) |
| Building the exe | [BUILD_GUIDE.md](BUILD_GUIDE.md) |

**Original CICFlowMeter research tool:**  
https://www.unb.ca/cic/research/applications.html#CICFlowMeter

---

*Guide version: for CICFlowMeter desktop application (Windows), including CSV rotation for live capture.*
