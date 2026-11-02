# Malware Taxonomy Cheatsheet

## Categories (delivery/intent, not mutually exclusive)
| Type       | What it does                                                 |
|------------|--------------------------------------------------------------|
| Dropper    | Fetches/unpacks and runs a second-stage payload              |
| Trojan     | Disguised as legitimate software; behavior can be anything   |
| Ransomware | Mass-encrypts files, demands payment for the key             |
| Worm       | Self-propagates across systems without human re-execution    |
| C2         | Channel back to attacker for instructions / exfiltration     |

## Behavior -> ATT&CK Technique
| Behavior                                      | Tactic                      | Technique ID |
|-----------------------------------------------|-----------------------------|--------------|
| Fetch/download a second-stage payload         | Execution                   | T1105        |
| Trick user into manually running payload      | Execution                   | T1204        |
| Run commands via PowerShell                   | Execution                   | T1059.001    |
| Inject code into another process              | Defense Evasion / Execution | T1055        |
| Persist via Registry Run key                  | Persistence                 | T1547.001    |
| Persist via Scheduled Task                    | Persistence                 | T1053        |
| Encrypt victim files for ransom               | Impact                      | T1486        |
| Dump OS credentials                           | Credential Access           | T1003        |
| C2 over HTTP/HTTPS                            | Command and Control         | T1071.001    |
| C2 over DNS                                   | Command and Control         | T1071.004    |
| Self-propagate via remote service exploit     | Lateral Movement            | T1210        |