# Malware Taxonomy Cheatsheet

Quick reference: malware category → what it does → ATT&CK tactic/technique it maps to.

## Malware Categories

| Type | Main Goal | Self-Spreads? | Installs Other Malware? | Needs User Action? |
|---|---|:---:|:---:|:---:|
| **Trojan** | Trick user into running it | No | Sometimes | Yes |
| **Worm** | Spread automatically | Yes | Sometimes | No |
| **Dropper** | Deliver/install a payload | No | Yes | Usually |
| **Ransomware** | Encrypt files for extortion | Usually No | Sometimes | Usually |
| **Spyware** | Covertly collect user data | No | No | Usually |
| **Rootkit** | Hide presence / maintain access | No | No | No |
| **Bot** | Act as remote-controlled node | Sometimes | No | No |
| **Adware** | Force unwanted ads | No | No | Usually |

## Behavior → ATT&CK Technique ID

| Observed Behavior | ATT&CK Tactic | Technique ID | Technique Name |
|---|---|---|---|
| Malicious Office macro runs code | Execution (TA0002) | T1059.005 | Command and Scripting Interpreter: Visual Basic |
| PowerShell used to run payload | Execution (TA0002) | T1059.001 | Command and Scripting Interpreter: PowerShell |
| `cmd.exe` runs attacker commands | Execution (TA0002) | T1059.003 | Command and Scripting Interpreter: Windows Command Shell |
| WMI used to launch code | Execution (TA0002) | T1047 | Windows Management Instrumentation |
| User double-clicks disguised file | Execution (TA0002) | T1204 | User Execution |
| Phishing email delivers dropper | Initial Access (TA0001) | T1566 | Phishing |
| Registry Run key added | Persistence (TA0003) | T1547.001 | Boot or Logon Autostart Execution: Registry Run Keys / Startup Folder |
| New Windows service created | Persistence (TA0003) | T1543.003 | Create or Modify System Process: Windows Service |
| Scheduled task/job created | Persistence (TA0003) | T1053.005 | Scheduled Task/Job: Scheduled Task |
| DLL search-order hijack | Persistence (TA0003) | T1574.001 | Hijack Execution Flow: DLL Search Order Hijacking |
| Beaconing over HTTP/HTTPS | Command and Control (TA0011) | T1071.001 | Application Layer Protocol: Web Protocols |
| Commands hidden in DNS queries | Command and Control (TA0011) | T1071.004 | Application Layer Protocol: DNS |
| Malware downloads more tools | Command and Control (TA0011) | T1105 | Ingress Tool Transfer |
| C2 via public cloud/social service | Command and Control (TA0011) | T1102 | Web Service |
| P2P C2 channel | Command and Control (TA0011) | T1090.002 | Proxy: External Proxy |
| Packed/obfuscated binary on disk | Defense Evasion (TA0005) | T1027 | Obfuscated Files or Information |
| Stolen files exfiltrated before encryption | Exfiltration (TA0010) | T1041 | Exfiltration Over C2 Channel |
| Files encrypted and held for ransom | Impact (TA0040) | T1486 | Data Encrypted for Impact |
| Backups deleted / shadow copies removed | Impact (TA0040) | T1490 | Inhibit System Recovery |
| Security tooling disabled | Defense Evasion (TA0005) | T1562.001 | Impair Defenses: Disable or Modify Tools |

## C2 Communication Patterns

| Pattern | Why Attackers Use It | Typical ATT&CK Mapping |
|---|---|---|
| HTTP/HTTPS | Blends in with normal web traffic | T1071.001 |
| DNS | Almost always allowed through firewalls | T1071.004 |
| TCP reverse shell | Direct interactive control | T1219 (Remote Access Software) / T1071 |
| IRC | Legacy botnet standard | T1071 |
| Social media / cloud (GitHub, Telegram, Pastebin) | Trusted domains, traffic blends in | T1102 |
| Peer-to-peer (P2P) | No single point of failure | T1090.002 |

## Key Terms

| Term | Meaning |
|---|---|
| **Taxonomy** | Classifying malware by behavior/purpose, not implementation |
| **C2 (Command & Control)** | Channel malware uses to talk to attacker infrastructure |
| **Beaconing** | Periodic malware check-in with its C2 server |
| **Botnet** | Group of infected machines under shared C2 |
| **Tactic** | The attacker's *goal* (e.g. Persistence) |
| **Technique** | The *method* used to achieve that goal (e.g. Registry Run Key) |

---
*A single malware sample often spans multiple categories and tactics — e.g. a trojan can drop a payload, establish persistence, beacon to C2, and deploy ransomware, all in one execution chain.*
