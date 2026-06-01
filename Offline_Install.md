# Offline installation guide — CICFlowMeter (Windows)

This guide is for a **Windows PC with no internet**. Follow each step in order. Do not skip steps.

You will install **Python**, then **cicflowmeter** and its libraries using files already included in this folder. **No download or online steps are required on this PC.**

---

## What you need before you start

Make sure you already have these items on this PC (for example, copied from a USB drive):

| Item | Description |
|------|-------------|
| **This project folder** | The full `cicflowmeter` folder, including `offline_wheels` and `src` |
| **Python installer** | `python-3.12.10-amd64.exe` (only if Python is not installed yet) |
| **Optional: Npcap installer** | Only if you need **live** network capture (`-i`). Not needed for `.pcap` files |

### Folder layout you should see

Open the project folder in File Explorer. It should look like this:

```
cicflowmeter/
├── Offline_Install.md       ← this guide
├── pyproject.toml
├── src/
│   └── cicflowmeter/
└── offline_wheels/          ← 18 files ending in .whl
    ├── numpy-2.4.6-cp312-cp312-win_amd64.whl
    ├── scipy-1.17.1-cp312-cp312-win_amd64.whl
    ├── cicflowmeter-0.4.2-py3-none-any.whl
    └── ... (15 more .whl files — see Appendix)
```

### Check the wheel folder (important)

1. Open the `offline_wheels` folder.
2. Count files ending in `.whl`.
3. You must have **exactly 18** files.
4. If you have fewer than 18, do not continue — ask whoever prepared the USB to provide a complete copy.

### System requirements

| Requirement | Value |
|-------------|--------|
| Windows | **10 or 11**, 64-bit |
| Python | **3.12.x** (this guide uses **3.12.10**) |
| Disk space | About **200 MB** free (Python + packages) |
| Internet | **Not required** on this PC |

---

## Table of contents

1. [Step 1 — Copy the project to your PC (if it is on USB)](#step-1--copy-the-project-to-your-pc-if-it-is-on-usb)
2. [Step 2 — Install Python 3.12.10](#step-2--install-python-31210)
3. [Step 3 — Open PowerShell in the project folder](#step-3--open-powershell-in-the-project-folder)
4. [Step 4 — Create a virtual environment](#step-4--create-a-virtual-environment)
5. [Step 5 — Activate the virtual environment](#step-5--activate-the-virtual-environment)
6. [Step 6 — Install packages from local wheels](#step-6--install-packages-from-local-wheels)
7. [Step 7 — Verify the installation](#step-7--verify-the-installation)
8. [Step 8 — Run cicflowmeter](#step-8--run-cicflowmeter)
9. [Optional — Npcap for live network capture](#optional--npcap-for-live-network-capture)
10. [Optional — Editable install (advanced)](#optional--editable-install-advanced)
11. [Troubleshooting](#troubleshooting)
12. [Appendix](#appendix)
13. [Summary checklist](#summary-checklist)

---

## Step 1 — Copy the project to your PC (if it is on USB)

Skip this step if the project is already on your hard drive (for example `D:\Tools\cicflowmeter`).

1. Insert the USB drive into the PC.
2. Press **Win + E** to open **File Explorer**.
3. Click the USB drive in the left panel (for example `USB Drive (E:)`).
4. Find the folder named `cicflowmeter`.
5. Right-click the `cicflowmeter` folder → **Copy**.
6. Go to where you want to keep the project (for example `D:\Tools\`).
7. Right-click empty space → **Paste**.
8. Wait until copying finishes (about **55–60 MB**).
9. If you need Python, also copy `python-3.12.10-amd64.exe` to the same PC (for example `D:\Installers\`).
10. Safely eject the USB if you are done.

**Write down your project path.** You will use it often. Example:

```
D:\Tools\cicflowmeter
```

---

## Step 2 — Install Python 3.12.10

Skip this step only if Python 3.12 is already installed and the command `python --version` works (see Step 2.5).

### Step 2.1 — Run the Python installer

1. Open **File Explorer**.
2. Go to the folder where `python-3.12.10-amd64.exe` is saved.
3. **Double-click** `python-3.12.10-amd64.exe`.
4. If Windows shows a security warning and you trust this file, click **More info** → **Run anyway**.

### Step 2.2 — Turn on “Add to PATH”

On the first installer window:

1. At the bottom, check the box **“Add python.exe to PATH”**.  
   This is required so you can type `python` in PowerShell later.
2. Click **“Customize installation”** (recommended).

### Step 2.3 — Optional features

1. Leave the default options checked (including **pip**).
2. Click **Next**.

### Step 2.4 — Advanced options and install

1. On **Advanced Options**, leave defaults or enable:
   - **Add Python to environment variables** (if shown)
   - **pip**
2. Click **Install**.
3. If Windows asks **“Do you want to allow this app to make changes?”**, click **Yes**.
4. Wait until you see **“Setup was successful”**.
5. Click **Close**.

### Step 2.5 — Open a new PowerShell window

You must use a **new** window so Windows picks up PATH changes.

1. Press **Win + X** on the keyboard.
2. Click **Terminal** or **Windows PowerShell**.

### Step 2.6 — Check that Python works

Type this command and press **Enter**:

```powershell
python --version
```

**Expected result:**

```
Python 3.12.10
```

**If you see** `'python' is not recognized`:

1. Close PowerShell.
2. **Restart the PC** once.
3. Open PowerShell again and run `python --version` again.

**If it still fails:**

1. Run the Python installer again.
2. Choose **Modify** or reinstall.
3. Ensure **“Add python.exe to PATH”** is checked.
4. Restart the PC and try again.

### Step 2.7 — Check that pip works

Type:

```powershell
python -m pip --version
```

You should see text that includes `pip` and a version number.  
This does **not** need internet.

---

## Step 3 — Open PowerShell in the project folder

All remaining steps run from the **project folder** (where `offline_wheels` lives).

### Step 3.1 — Open the project in File Explorer

1. Press **Win + E**.
2. Navigate to your project folder, for example:

   `D:\Tools\cicflowmeter`

### Step 3.2 — Confirm required files exist

In that folder, you should see:

| Name | Type |
|------|------|
| `offline_wheels` | Folder |
| `src` | Folder |
| `pyproject.toml` | File |
| `Offline_Install.md` | File |

Open `offline_wheels` and confirm there are **18** `.whl` files.

### Step 3.3 — Open PowerShell in this folder

1. Click the **address bar** at the top of File Explorer (where the path is shown).
2. Type: `powershell`
3. Press **Enter**.

A PowerShell window opens. The title bar or prompt should show your project path.

### Step 3.4 — Confirm the current directory

Type:

```powershell
Get-Location
```

Press **Enter**.

**Example output:**

```
Path
----
D:\Tools\cicflowmeter
```

If the path is wrong:

1. Type `cd` followed by your path in quotes, for example:

```powershell
cd "D:\Tools\cicflowmeter"
```

2. Press **Enter**.

### Step 3.5 — List the wheel files

Type:

```powershell
dir offline_wheels\*.whl
```

Press **Enter**. You should see **18** files listed.

---

## Step 4 — Create a virtual environment

A **virtual environment** is a private Python space for this project. It keeps cicflowmeter separate from other programs.

### Step 4.1 — Create the environment

Make sure PowerShell is still in the project folder (Step 3).

Type:

```powershell
python -m venv .venv
```

Press **Enter**.

Wait a few seconds. Usually there is no message — that is normal.

### Step 4.2 — Confirm it was created

Type:

```powershell
Test-Path .venv\Scripts\python.exe
```

Press **Enter**.

**Expected output:**

```
True
```

**If you see `False`:**

1. Check you are in the correct folder (`Get-Location`).
2. Run Step 4.1 again.
3. If it still fails, see [Troubleshooting](#troubleshooting).

---

## Step 5 — Activate the virtual environment

You must **activate** the environment before installing or running cicflowmeter.

You need to do this **every time** you open a new PowerShell window for this project.

### Step 5.1 — Allow PowerShell scripts (first time only)

If you have never run local scripts on this PC, type:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Press **Enter**.

If asked **“Do you want to change the execution policy?”**, type **Y** and press **Enter**.

If you get an error that you are not allowed to change policy, ask your system administrator, or skip to Step 5.2 and see [Troubleshooting](#troubleshooting) if activation fails.

### Step 5.2 — Activate the environment

Type:

```powershell
.\.venv\Scripts\Activate.ps1
```

Press **Enter**.

**Success looks like this** — the start of the line shows `(.venv)`:

```
(.venv) PS D:\Tools\cicflowmeter>
```

### Step 5.3 — Confirm you are using the virtual environment Python

Type:

```powershell
Get-Command python | Format-List Source
```

Press **Enter**.

The path should contain:

```
.venv\Scripts\python.exe
```

---

## Step 6 — Install packages from local wheels

These commands install everything **only from the `offline_wheels` folder**. They do **not** use the internet.

**Before each command below, check:**

- [ ] PowerShell is in the project folder  
- [ ] The prompt shows `(.venv)` at the beginning  

### Step 6.1 — Install pip tools from local wheels

Type this **entire line** and press **Enter**:

```powershell
python -m pip install --no-index --find-links=offline_wheels pip setuptools wheel
```

**What this means:**

- `--no-index` — do not look on the internet  
- `--find-links=offline_wheels` — use only files in the `offline_wheels` folder  

You may see `Requirement already satisfied` for pip. That is OK.

### Step 6.2 — Install cicflowmeter and all libraries

Type:

```powershell
python -m pip install --no-index --find-links=offline_wheels cicflowmeter
```

Press **Enter**.

**Wait 1–3 minutes.** The `scipy` package is large.

**Success looks like:**

```
Successfully installed ... cicflowmeter-0.4.2 ...
```

This installs:

- cicflowmeter (the program)
- numpy, scipy, scapy, requests
- Supporting packages: certifi, charset-normalizer, idna, urllib3

### Step 6.3 — List installed packages

Type:

```powershell
python -m pip list
```

Press **Enter**.

You should see at least these names:

- cicflowmeter  
- numpy  
- scipy  
- scapy  
- requests  

---

## Step 7 — Verify the installation

Run these checks **in order**. Each should work without internet.

### Step 7.1 — Show help

Type:

```powershell
cicflowmeter -h
```

Press **Enter**.

You should see help text with options such as `-f`, `-c`, `-d`, `-i`, `-u`.

### Step 7.2 — Test Python imports

Type:

```powershell
python -c "import numpy, scipy, scapy, requests; from cicflowmeter.sniffer import main; print('All imports OK')"
```

Press **Enter**.

**Expected:**

```
All imports OK
```

### Step 7.3 — About the Scapy warning

You might see:

```
WARNING: No libpcap provider available ! pcap won't be used
```

| Situation | What it means |
|-----------|----------------|
| You only use **`.pcap` files** (`-f`) | You can **ignore** this warning. |
| You want **live capture** (`-i`) | Install **Npcap** — see [Optional — Npcap](#optional--npcap-for-live-network-capture). |

### Step 7.4 — Show installed version

Type:

```powershell
python -m pip show cicflowmeter
```

Press **Enter**.

Look for:

```
Version: 0.4.2
```

If all checks pass, installation is complete.

---

## Step 8 — Run cicflowmeter

Every time you use cicflowmeter in a **new** PowerShell window:

1. Go to the project folder (Step 3).  
2. Activate the environment (Step 5): `.\.venv\Scripts\Activate.ps1`  
3. Confirm `(.venv)` appears in the prompt.  
4. Run a command below.

### Example A — Convert one PCAP file to CSV

1. Put your capture file in a known place, for example:

   `D:\Data\capture.pcap`

2. Run (change paths to match your files):

```powershell
cicflowmeter -f "D:\Data\capture.pcap" -c "D:\Data\flows.csv"
```

3. Open `D:\Data\flows.csv` in Excel or Notepad to confirm it was created.

**If the PCAP is in the project folder:**

```powershell
cicflowmeter -f example.pcap -c flows.csv
```

### Example B — Convert every PCAP in a folder

1. Create two folders, for example:
   - Input: `D:\pcaps\` (put `.pcap` files here)
   - Output: `D:\csv_out\` (empty folder)

2. Run:

```powershell
cicflowmeter -d "D:\pcaps" -c "D:\csv_out"
```

Each PCAP becomes one CSV in `D:\csv_out\`.

### Example C — Merge all PCAPs into one CSV

```powershell
cicflowmeter -d "D:\pcaps" -c "D:\csv_out" --merge
```

Output file: `D:\csv_out\merged_output.csv`

### Example D — Only some columns in the CSV

```powershell
cicflowmeter -f "D:\Data\capture.pcap" -c "D:\Data\flows.csv" --fields src_ip,dst_ip,src_port,dst_port,protocol
```

### Example E — More detailed logs

```powershell
cicflowmeter -f "D:\Data\capture.pcap" -c "D:\Data\flows.csv" -v
```

### Example F — Send results to a local web server (optional)

Only use this if you already have a server running on this PC:

```powershell
cicflowmeter -f "D:\Data\capture.pcap" -u http://127.0.0.1:8080/flows
```

---

## Optional — Npcap for live network capture

| Mode | Npcap needed? |
|------|----------------|
| Read `.pcap` / `.pcapng` files (`-f`) | **No** |
| Read a folder of PCAPs (`-d`) | **No** |
| Capture live traffic (`-i`) | **Yes** |

### Before you start

You need the **Npcap installer** (`.exe`) on this PC, copied on the same USB as this project.  
This guide does not download anything — use the installer file you already have.

### Install Npcap

1. Locate the Npcap installer file (for example `npcap-1.xx.exe`).
2. Right-click it → **Run as administrator**.
3. Click **Yes** if Windows asks for permission.
4. During setup, enable **Install Npcap in WinPcap API-compatible Mode** (recommended).
5. Finish the installer.
6. **Restart the PC** if the installer asks you to.

### List Npcap paths (quick)

1. Open PowerShell in the project folder.
2. Activate the virtual environment: `.\.venv\Scripts\Activate.ps1`
3. Run:

```powershell
python -c "from scapy.all import get_if_list; print(get_if_list())"
```

4. Each line is an Npcap path (for example `\Device\NPF_{...}`).

**Note:** If Python prints a **list** with `\\Device\\NPF_...`, that is normal — Python shows one backslash as `\\`. When you copy a path into `cicflowmeter -i`, use **one** backslash before `Device`, for example:

```text
\Device\NPF_{YOUR-GUID-HERE}
```

Do **not** copy `Device\NPF_...` without the leading `\`.

The list order is **not** “best interface first.” Names like `Local Area Connection* 4` are often **WAN Miniport** adapters with little or no traffic. Use the methods below to find the right path.

---

### Map each Npcap path to a Windows adapter name

This shows **which Windows adapter** each `\Device\NPF_{...}` path belongs to, and the **IPv4 address** (if any).

1. Activate the venv: `.\.venv\Scripts\Activate.ps1`
2. Run (copy the whole block, including the first and last lines):

```powershell
@'
from scapy.all import IFACES
for iface in IFACES.values():
    ip = getattr(iface, "ip", None) or "(none)"
    print(iface.network_name)
    print("    ->", iface.name, "  IP:", ip)
'@ | python
```

**Example output (yours will differ):**

```text
\Device\NPF_{7AA6BF30-DB8B-4B9C-9CC0-23511D4309F7}
    -> Local Area Connection* 5  IP: (none)
\Device\NPF_{D68FFFB6-3D04-4F1A-AD2A-F7576144CCAE}
    -> Ethernet 2  IP: 192.168.1.50
```

| What you see | Meaning |
|--------------|---------|
| **Ethernet** / **Wi‑Fi** with your real LAN or internet IP | Usually the adapter to use for live capture |
| **Local Area Connection\*** (no IP) | Often WAN Miniport — usually **not** where browser traffic goes |
| **VMware**, **vEthernet**, **WSL**, **Hyper-V** | Only traffic for those tools |
| **Loopback** / `\Device\NPF_Loopback` | Only `127.0.0.1` traffic |

**Alternative — table with MAC and IPv4:**

```powershell
python -c "from scapy.all import show_interfaces; show_interfaces()"
```

---

### Match your IP with `ipconfig` (pick the right adapter)

1. In PowerShell, run:

```powershell
ipconfig
```

2. Find the adapter you use for the internet or LAN (for example **Ethernet** or **Wi‑Fi**) and note its **IPv4 Address** (for example `192.168.1.50`).
3. In the **Map each Npcap path** output above, pick the `\Device\NPF_{...}` line whose **IP** matches that address.
4. Use **that** path in `cicflowmeter -i`.

---

### Test whether an interface receives packets

Use this when you are not sure which path sees traffic, or `live_flows.csv` stays empty.

1. Open PowerShell **as Administrator**.
2. Go to the project folder and activate the venv.
3. Run the test (copy the whole block; about **5 seconds per interface**; skip loopback):

```powershell
@'
from scapy.all import sniff, get_if_list
for iface in get_if_list():
    if "Loopback" in iface:
        continue
    print("Testing:", iface, flush=True)
    try:
        pkts = sniff(iface=iface, timeout=5, store=True)
        print("  ->", len(pkts), "packets in 5 seconds")
    except Exception as e:
        print("  -> ERROR:", e)
    print()
'@ | python
```

4. **While each “Testing: …” line runs**, generate traffic on the PC you care about:
   - Open a website in the browser, or  
   - Run: `ping 8.8.8.8`
5. When the script finishes, use the path with the **highest packet count** (often your Ethernet or Wi‑Fi adapter).

| Packet count | Meaning |
|--------------|---------|
| **0** | Little or no traffic on that adapter (wrong choice for general capture) |
| **Low** (1–20) | Some background traffic only |
| **High** (hundreds+) while you browse/ping | Good candidate for `cicflowmeter -i` |

---

### Run live capture

1. Open PowerShell **as Administrator** (right-click → Run as administrator).
2. Go to the project folder and activate the venv:

```powershell
cd "D:\Tools\cicflowmeter"
.\.venv\Scripts\Activate.ps1
```

3. Run with the **path you chose** from the steps above (example — replace with your path):

```powershell
cicflowmeter -i "\Device\NPF_{YOUR-GUID-HERE}" -c live_flows.csv
```

In **Command Prompt (cmd)**, use the same path in quotes:

```cmd
cicflowmeter -i "\Device\NPF_{YOUR-GUID-HERE}" -c live_flows.csv
```

4. While capture is running, generate traffic (browse the web or `ping 8.8.8.8`).
5. Wait at least **10–20 seconds**, then press **Ctrl+C** to stop. Flow rows are written when flows end or when you stop capture.
6. Open `live_flows.csv` and confirm it has data.

**Reminder:** cicflowmeter live mode only records **IP over TCP or UDP**. Pure ARP or short ICMP may not appear as flows immediately.

---

## Optional — Editable install (advanced)

Use this **only** if you will **edit** source code under `src\` and want changes to apply without reinstalling.

Complete **Steps 1–7** first using the normal install (Step 6.2).

Then run:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install --no-index --find-links=offline_wheels hatchling editables setuptools wheel packaging pathspec pluggy trove-classifiers
python -m pip install --no-index --find-links=offline_wheels -e .
cicflowmeter -h
```

The `.` at the end means “this project folder.”

---

## Troubleshooting

### `'python' is not recognized`

1. Install Python with **Add python.exe to PATH** checked (Step 2.2).  
2. Restart the PC.  
3. Open a **new** PowerShell window.  
4. Try again: `python --version`

### `Activate.ps1` cannot be loaded

Run once:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then:

```powershell
.\.venv\Scripts\Activate.ps1
```

### `ERROR: Could not find a version that satisfies the requirement`

1. Confirm the prompt shows `(.venv)`.  
2. Confirm you are in the project folder (`Get-Location`).  
3. Confirm `offline_wheels` has **18** `.whl` files.  
4. Always use **both** flags together:

```powershell
python -m pip install --no-index --find-links=offline_wheels <package-name>
```

### `No matching distribution found for numpy` or `scipy`

This bundle only works on:

- **Windows 64-bit**  
- **Python 3.12.x**  

If your PC is 32-bit or uses Python 3.11 or older, this wheel set will not work. You need a matching bundle prepared for your system.

### `cicflowmeter` is not recognized

1. Activate the virtual environment first: `.\.venv\Scripts\Activate.ps1`  
2. Or run:

```powershell
python -m cicflowmeter.sniffer -h
```

### Live capture: `Interface '...' not found`

1. Use the exact path from **Map each Npcap path** or **Test whether an interface receives packets** — not a shortened name.
2. The path must start with `\Device\` (leading backslash), not `Device\`.
3. In cmd, wrap the path in double quotes: `"\Device\NPF_{...}"`.
4. If you copied from a Python **list**, remove extra backslashes — use `\Device\NPF_{...}`, not `\\Device\\NPF_{...}` in the shell command.

### Live capture: `live_flows.csv` is empty

1. Confirm you used the adapter that had **traffic** in the packet test (see [Test whether an interface receives packets](#test-whether-an-interface-receives-packets)).
2. Run PowerShell **as Administrator**.
3. Generate traffic while capture is running (browser or `ping 8.8.8.8`).
4. Wait, then press **Ctrl+C** — do not close the window without stopping capture.
5. Avoid the first entries in `get_if_list()` if they are WAN Miniports with no IP; use **Ethernet** / **Wi‑Fi** with your `ipconfig` IPv4 address instead.

### Install is very slow

Normal. The `scipy` file is about 36 MB. Wait until you see `Successfully installed`.

### Start over from scratch

In the project folder, with no venv active:

```powershell
deactivate
Remove-Item -Recurse -Force .venv
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --no-index --find-links=offline_wheels pip setuptools wheel
python -m pip install --no-index --find-links=offline_wheels cicflowmeter
cicflowmeter -h
```

If `deactivate` says it is not recognized, close PowerShell, open a new window, and continue from `Remove-Item`.

---

## Appendix

### All 18 files in `offline_wheels`

| File | Purpose |
|------|---------|
| `numpy-2.4.6-cp312-cp312-win_amd64.whl` | Numerical library |
| `scipy-1.17.1-cp312-cp312-win_amd64.whl` | Statistics |
| `scapy-2.7.0-py3-none-any.whl` | Packet handling |
| `requests-2.34.2-py3-none-any.whl` | HTTP output mode |
| `certifi-2026.5.20-py3-none-any.whl` | SSL certificates |
| `charset_normalizer-3.4.7-cp312-cp312-win_amd64.whl` | Text encoding |
| `idna-3.16-py3-none-any.whl` | Domain names |
| `urllib3-2.7.0-py3-none-any.whl` | HTTP client |
| `cicflowmeter-0.4.2-py3-none-any.whl` | This application |
| `pip-26.1.1-py3-none-any.whl` | Package installer |
| `setuptools-82.0.1-py3-none-any.whl` | Install tools |
| `wheel-0.47.0-py3-none-any.whl` | Wheel support |
| `hatchling-1.29.0-py3-none-any.whl` | Build tool |
| `packaging-26.2-py3-none-any.whl` | Version handling |
| `pathspec-1.1.1-py3-none-any.whl` | Path matching |
| `pluggy-1.6.0-py3-none-any.whl` | Plugin system |
| `trove_classifiers-2026.5.22.10-py3-none-any.whl` | Package metadata |
| `editables-0.6-py3-none-any.whl` | Editable install only |

### Quick command reference (after setup)

Open PowerShell in the project folder, then:

```powershell
.\.venv\Scripts\Activate.ps1
cicflowmeter -f "D:\Data\capture.pcap" -c "D:\Data\flows.csv"
```

### First-time full install (copy-paste block)

Use this only **after** Python 3.12 is installed and you are in the project folder:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --no-index --find-links=offline_wheels pip setuptools wheel
python -m pip install --no-index --find-links=offline_wheels cicflowmeter
cicflowmeter -h
```

---

## Summary checklist

Print or save this list. Check each box as you finish.

- [ ] Project folder is on this PC (with `offline_wheels` — 18 `.whl` files)  
- [ ] Python 3.12.10 installed; `python --version` shows 3.12.x  
- [ ] `python -m pip --version` works  
- [ ] PowerShell opened **inside** the project folder  
- [ ] `python -m venv .venv` completed; `Test-Path .venv\Scripts\python.exe` is `True`  
- [ ] `.\.venv\Scripts\Activate.ps1` — prompt shows `(.venv)`  
- [ ] `pip install --no-index --find-links=offline_wheels pip setuptools wheel`  
- [ ] `pip install --no-index --find-links=offline_wheels cicflowmeter`  
- [ ] `cicflowmeter -h` shows help  
- [ ] `All imports OK` from Step 7.2  
- [ ] (Only for live capture) Npcap installed  
- [ ] (Only for live capture) Mapped Npcap path to adapter name and tested packet count on the correct interface  

**You are ready to use cicflowmeter offline.**
