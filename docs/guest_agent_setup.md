# Day 26 - CAPEv2 Guest Agent + Smoke Test

## Prerequisites

- Day 22: isolated VM with host-only networking (192.168.56.101)
- Day 23: clean-baseline snapshot exists
- Days 24-25: CAPEv2 host services running on the Ubuntu host

## Guest Agent Installation

The CAPE agent is a small Python script that runs inside the Windows guest.
It listens for analysis tasks from the host and orchestrates sample execution.

1. Copy the agent into the guest (from the CAPEv2 host install):
   ```
   # On the host - copy agent.py to a shared location the guest can reach
   # via the host-only network (e.g., a simple HTTP server on the host)
   cd /opt/CAPEv2/agent
   python3 -m http.server 8080 --bind 192.168.56.1
   ```

2. Inside the guest, download and place the agent:
   ```
   # In the guest browser or via PowerShell
   Invoke-WebRequest http://192.168.56.1:8080/agent.py -OutFile C:\agent\agent.py
   ```

3. Configure the agent to start automatically:
   - Create a batch file `C:\agent\start_agent.bat`:
     ```
     @echo off
     cd C:\agent
     python agent.py
     ```
   - Add to startup: place a shortcut in
     `C:\Users\<user>\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\`

4. Verify the agent is listening:
   ```
   # Inside the guest
   netstat -an | findstr 8000
   # Should show LISTENING on port 8000
   ```

## CAPEv2 Host Configuration

Edit `/opt/CAPEv2/conf/virtualbox.conf`:
```ini
[virtualbox]
mode = headless
path = /usr/bin/VBoxManage
machines = Strazh-Win10

[Strazh-Win10]
label = Strazh-Win10
platform = windows
ip = 192.168.56.101
snapshot = clean-baseline
resultserver_ip = 192.168.56.1
resultserver_port = 2042
```

Edit `/opt/CAPEv2/conf/reporting.conf` to enable JSON reports:
```ini
[jsondump]
enabled = yes
indent = 4
calls = yes
```

## Smoke Test

Submit one benign binary from the host:
```bash
# Using the CAPEv2 REST API
curl -F file=@/path/to/notepad.exe http://localhost:8090/apiv2/tasks/create/file/

# Or using the web UI at http://localhost:8000
```

Wait for the analysis to complete (check status via API or web UI):
```bash
curl http://localhost:8090/apiv2/tasks/view/1/
```

## Verification

The smoke test passes when:
1. The task status shows "reported"
2. A report.json exists under `/opt/CAPEv2/storage/analyses/1/reports/report.json`
3. The report contains non-empty `behavior.processes` and `behavior.processtree` sections

## Full Sample Path (trace for checkpoint)

```
submit_sample.py (or web UI)
  → REST API (/apiv2/tasks/create/file/)
    → CAPEv2 scheduler picks up the task
      → VBoxManage restores "clean-baseline" snapshot
        → VBoxManage starts "Strazh-Win10" headless
          → Guest agent (port 8000) receives the sample
            → Agent executes the sample, CAPE monitor DLLs hook API calls
              → Behavioral logs stream back to host's result server (port 2042)
                → VM powers off, reverts to snapshot
                  → CAPEv2 processing pipeline runs (signatures, reporting)
                    → report.json written to storage/analyses/<id>/reports/
```
