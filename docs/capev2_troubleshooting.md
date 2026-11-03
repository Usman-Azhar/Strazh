# Day 27 - CAPEv2 Troubleshooting

Common issues encountered during CAPEv2 setup and their fixes.
The checkpoint for this day is: "it works twice in a row."

## Issue 1: Guest agent not reachable

**Symptom:** Task stays in "pending" forever.

**Check:**
```bash
# From the host
ping 192.168.56.101          # guest must respond
curl http://192.168.56.101:8000  # agent must be listening
```

**Fixes:**
- Verify host-only adapter exists: `VBoxManage list hostonlyifs`
- Verify guest has static IP 192.168.56.101 (not DHCP)
- Verify Windows Firewall inside the guest allows inbound on port 8000
- Verify agent.py is actually running inside the guest

## Issue 2: Result server connection refused

**Symptom:** Report generated but `behavior` section is empty.

**Check:**
```bash
# On the host
netstat -tlnp | grep 2042   # result server must be listening
```

**Fixes:**
- Confirm `resultserver_ip = 192.168.56.1` in virtualbox.conf (host's IP on vboxnet0)
- Confirm `resultserver_port = 2042` matches the running result server
- Restart CAPEv2 services: `sudo systemctl restart cape cape-processor cape-rooter`

## Issue 3: Snapshot restore fails

**Symptom:** `VBoxManage: error: Machine 'Strazh-Win10' is not currently running`

**Fixes:**
- The snapshot must exist: `VBoxManage snapshot "Strazh-Win10" list`
- The snapshot name in virtualbox.conf must match exactly (case-sensitive)
- If the VM is stuck in "saved" state: `VBoxManage controlvm "Strazh-Win10" poweroff`

## Issue 4: Analysis completes but no API calls captured

**Symptom:** `behavior.processes[0].calls` is an empty list.

**Possible causes:**
- The CAPE monitor DLLs weren't injected (check CAPEv2 logs for injection errors)
- The sample crashed before making any API calls
- Anti-analysis in the sample detected the sandbox and exited early
- Wrong architecture: 32-bit monitor for a 64-bit sample or vice versa

**Check:** Look at `analyzer.log` inside the analysis storage directory.

## Issue 5: Permission errors on CAPEv2 directories

**Symptom:** `PermissionError` in CAPEv2 logs.

**Fix:**
```bash
sudo chown -R cape:cape /opt/CAPEv2/storage
sudo chmod -R 755 /opt/CAPEv2/storage
```

## Verification: "Works Twice in a Row"

```bash
# Run 1
python scripts/submit_sample.py data/raw/notepad.exe
# Confirm report saved successfully

# Run 2 (immediately after)
python scripts/submit_sample.py data/raw/calc.exe
# Confirm report saved successfully

# Both reports must have non-empty behavior.processes
python -c "
import json
for i in [1, 2]:
    r = json.load(open(f'data/raw/cape_reports/report_{i}.json'))
    procs = r.get('behavior', {}).get('processes', [])
    calls = sum(len(p.get('calls', [])) for p in procs)
    print(f'Report {i}: {len(procs)} processes, {calls} API calls')
"
```
