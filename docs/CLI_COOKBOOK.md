# CLI cookbook — command recipes

Copy-paste examples for **`cicflowmeter`** in scripts, servers, and daily work. Activate your environment first:

```powershell
.\.venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Full option reference: [DOCUMENTATION.md §4](DOCUMENTATION.md#4-command-line-interface-cli).

---

## Offline — single file

```powershell
# Basic PCAP → CSV
cicflowmeter -f capture.pcap -c flows.csv

# PCAPNG
cicflowmeter -f capture.pcapng -c flows.csv

# Absolute paths (Windows)
cicflowmeter -f "D:\Captures\monday.pcap" -c "D:\Output\monday_flows.csv"

# Verbose debug
cicflowmeter -f capture.pcap -c flows.csv -v
```

---

## Offline — folder

```powershell
# One CSV per PCAP in folder
cicflowmeter -d "D:\Captures\week1" -c "D:\Output\week1_csv"

# Merge all PCAPs into one file: merged_output.csv
cicflowmeter -d "D:\Captures\week1" -c "D:\Output" --merge
```

---

## Live capture

```powershell
# Windows (interface from scapy / GUI refresh)
cicflowmeter -i "\Device\NPF_{GUID}" -c live_flows.csv

# Linux
cicflowmeter -i eth0 -c live_flows.csv

# New CSV file every 5 minutes: live.csv → live1.csv → live2.csv …
cicflowmeter -i eth0 -c live.csv --rotate-minutes 5

# Stop with Ctrl+C — remaining flows are flushed
```

List interfaces:

```powershell
python -c "from scapy.all import get_if_list; print('\n'.join(get_if_list()))"
```

---

## HTTP output (backend / ML)

```powershell
# Stream flows to local API
cicflowmeter -i eth0 -u http://127.0.0.1:8080/flows

# PCAP → API (batch POST per flow)
cicflowmeter -f capture.pcap -u http://127.0.0.1:8080/flows

# Smaller JSON payload
cicflowmeter -f capture.pcap -u http://127.0.0.1:8080/predict `
  --fields src_ip,dst_ip,src_port,dst_port,flow_duration,tot_fwd_pkts,tot_bwd_pkts
```

See [BACKEND_INTEGRATION.md](BACKEND_INTEGRATION.md) for a sample receiver.

---

## Column selection

```powershell
# Only endpoint + duration
cicflowmeter -f capture.pcap -c slim.csv `
  --fields src_ip,dst_ip,src_port,dst_port,protocol,flow_duration

# Many IDS-style features
cicflowmeter -f capture.pcap -c ids.csv `
  --fields src_ip,dst_ip,src_port,dst_port,flow_duration,tot_fwd_pkts,tot_bwd_pkts,flow_byts_s,flow_pkts_s,syn_flag_cnt,ack_flag_cnt
```

---

## Scripting patterns

### PowerShell — exit if failed

```powershell
cicflowmeter -f $inPcap -c $outCsv
if ($LASTEXITCODE -ne 0) { throw "cicflowmeter failed" }
```

### PowerShell — loop over PCAPs

```powershell
Get-ChildItem "D:\Captures\*.pcap" | ForEach-Object {
    $out = "D:\Output\$($_.BaseName).csv"
    Write-Host "Processing $($_.Name)..."
    cicflowmeter -f $_.FullName -c $out
}
```

### Bash — loop

```bash
for f in /data/pcap/*.pcap; do
  base=$(basename "$f" .pcap)
  cicflowmeter -f "$f" -c "/data/csv/${base}.csv"
done
```

### Bash — timestamped output

```bash
out="/data/out/flows_$(date +%Y%m%d_%H%M%S).csv"
cicflowmeter -f /data/in/latest.pcap -c "$out"
```

---

## Common mistakes

| Mistake | Fix |
|---------|-----|
| `-d` with output **file** path | Use a **directory** for `-c` output |
| `--merge` without `-d` | `--merge` only works with directory input |
| `-u` with invalid URL | Must start with `http://` or `https://` |
| Live capture without admin/Npcap | Install Npcap; run elevated (Windows) |
| Expecting non-TCP/UDP in CSV | Filter is `ip and (tcp or udp)` only |

---

## Help

```powershell
cicflowmeter --help
```

---

## Related docs

- [GETTING_STARTED.md](GETTING_STARTED.md)  
- [BACKEND_INTEGRATION.md](BACKEND_INTEGRATION.md)  
- [BUILD_GUIDE.md](BUILD_GUIDE.md)  
