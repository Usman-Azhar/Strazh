# Day 30 - Public Sandbox Report Comparison

Comparison of CAPEv2 output against public reports from Any.Run and Hybrid-Analysis.
Based on browsing public reports (defensive research, view-only).

## Structural Comparison

| Feature                    | CAPEv2                          | Any.Run                              | Hybrid-Analysis                      |
|----------------------------|---------------------------------|--------------------------------------|--------------------------------------|
| API call logging           | Full sequence per process       | Full sequence, interactive replay    | Full sequence                        |
| Process tree               | JSON tree with PIDs             | Visual interactive tree              | JSON + visual tree                   |
| Network capture            | DNS, HTTP, TCP, UDP separately  | Full PCAP + parsed protocols         | Full PCAP + parsed protocols         |
| Dropped files              | Listed with hashes              | Listed with hashes + preview         | Listed with hashes + VT lookup       |
| Screenshots                | Periodic captures               | Real-time video recording            | Periodic captures                    |
| Memory dumps               | Per-process dumps available     | Available (paid tier)                | Available                            |
| YARA matches               | Configurable rule sets          | Community + commercial rules         | CrowdStrike + community rules        |
| MITRE ATT&CK mapping       | Via signatures                  | Automatic, prominent in UI           | Automatic, mapped per behavior       |
| Report format              | JSON (machine-readable)         | JSON API + interactive web report    | JSON API + PDF export                |

## What Public Reports Capture That Our CAPEv2 Setup Doesn't (Yet)

1. **Full PCAP network capture** — Any.Run and Hybrid-Analysis provide raw PCAP
   files, not just parsed protocol summaries. CAPEv2 can do this too (via
   `tcpdump` on the host-only interface) but it's not enabled by default.

2. **VirusTotal integration** — Hybrid-Analysis cross-references dropped files and
   the sample itself against VT detection rates. CAPEv2 can be configured with a
   VT API key but this isn't set up in our install.

3. **Interactive analysis** — Any.Run lets analysts interact with the sample in
   real-time (click dialogs, provide input). CAPEv2 runs headless by default; our
   setup uses `mode = headless` which means no interaction during execution.

4. **Anti-evasion techniques** — Commercial sandboxes actively hide sandbox
   indicators (fake user activity, realistic system profiles). Our CAPEv2 setup
   is a default install, which sophisticated malware can fingerprint via:
   - VM artifacts (VirtualBox guest additions, registry keys)
   - Lack of user activity (no mouse movement, no documents)
   - Low uptime / clean system state

5. **Multi-platform analysis** — Any.Run supports Windows 7/10/11 guests and
   Linux. Our setup has one Windows 10 guest only.

## What Our CAPEv2 Setup Has That Public Reports Don't Expose

1. **Raw report.json** — full programmatic access to every API call and argument,
   not filtered through a web UI. This is what Days 31-32 parse.

2. **Custom YARA rules** — our Day 19 rules can be loaded into CAPEv2's processing
   pipeline, unlike public sandboxes which use their own fixed rule sets.

3. **Reproducibility** — same snapshot, same configuration, every time. Public
   sandbox results vary based on their internal VM pool state.

4. **Privacy** — samples submitted to public sandboxes become public. Our CAPEv2
   instance is local and private.

## Structural Implications for Feature Extraction

The core behavioral data structure is very similar across all three:
- Ordered API call sequences (the basis for Day 31's parser)
- Process trees (Day 32)
- File system and registry modifications (Day 32)
- Network indicators

The main difference is depth of capture, not structure. Our Day 31-32 parsers
work on CAPEv2's JSON schema but the same extraction logic would apply to any
sandbox that exposes ordered API call logs per process.
