# Day 42 — Static vs Dynamic Model Comparison

Precision, recall, F1, and AUC-ROC for all models built so far.
Direct comparison of what each approach can and cannot see.

## Model Summary

| Model | Type | Input | Features | Days |
|-------|------|-------|----------|------|
| XGBoost (EMBER) | Static | PE metadata | 2381-dim EMBER vector | 21 |
| LSTM | Dynamic | API sequences | Tokenized API calls (up to 2048) | 40 |
| Transformer | Dynamic | API sequences | Same tokenized API calls | 41 |
| XGBoost (dynamic tabular) | Dynamic | CAPEv2 report | 23-dim behavioral vector | 34 |

## Performance Comparison

Results will be populated with real numbers after Day 35 (full corpus run).
The table below shows the expected structure and synthetic-data baselines.

| Model | Accuracy | Precision | Recall | F1 | AUC-ROC | Notes |
|-------|:--------:|:---------:|:------:|:--:|:-------:|-------|
| XGBoost (EMBER static) | 0.99 | 0.99 | 0.99 | 0.99 | 0.999 | Day 21 result on EMBER test set |
| XGBoost (dynamic tabular) | TBD | TBD | TBD | TBD | TBD | Needs Day 35 corpus |
| LSTM (dynamic seq) | TBD | TBD | TBD | TBD | TBD | Needs Day 35 corpus |
| Transformer (dynamic seq) | TBD | TBD | TBD | TBD | TBD | Needs Day 35 corpus |

**On synthetic data (fixture-based augmentation):**

| Model | Test Accuracy | Notes |
|-------|:---:|-------|
| LSTM | ~0.95-1.00 | Synthetic benign/malicious APIs are nearly disjoint |
| Transformer | ~0.95-1.00 | Same synthetic data, similar performance |

## Where Dynamic Outperforms Static

| Scenario | Static Sees | Dynamic Sees | Winner |
|----------|-------------|-------------|--------|
| Packed/obfuscated PE | Distorted headers, high entropy | Real runtime behavior after unpacking | Dynamic |
| Process injection | Nothing (no PE indicator) | NtAllocateVirtualMemory → NtWriteVirtualMemory → CreateRemoteThread | Dynamic |
| Fileless malware | Minimal PE footprint | Full API trace of in-memory operations | Dynamic |
| Living-off-the-land (LOLBins) | Clean system binary (cmd.exe, powershell.exe) | Suspicious command chains + network callbacks | Dynamic |
| Multi-stage payloads | Only stage-1 PE features | Full behavioral chain across all stages | Dynamic |

## Where Static Outperforms Dynamic

| Scenario | Static Sees | Dynamic Sees | Winner |
|----------|-------------|-------------|--------|
| Known PE anomalies | Malformed headers, suspicious section names, import patterns | May not trigger if not executed properly | Static |
| Evasion-aware malware | PE structure is fixed at compile time | Detects sandbox → alters behavior | Static |
| Analysis failures | Always produces features from the file | Empty/minimal trace on crash/timeout | Static |
| Speed | Milliseconds (no execution needed) | Minutes (requires full sandbox run) | Static |
| Scalability | Can scan millions of files | Limited by sandbox throughput (~50-100/day) | Static |
| Novel import patterns | Unusual DLL combinations are a strong signal | Same DLLs look normal at runtime | Static |

## Why Hybrid Makes Sense

Neither approach alone is sufficient:

1. **Static catches what dynamic misses:** sandbox-aware malware that behaves
   benignly during analysis, but whose PE structure reveals anomalies.

2. **Dynamic catches what static misses:** packed/obfuscated samples where the
   PE metadata is deliberately distorted, but runtime behavior exposes the payload.

3. **The overlap strengthens both:** when both agree on a classification, confidence
   is very high. When they disagree, the disagreement itself is an informative signal.

This is why Track 4b (Days 43-47) explores fusion strategies:
- **Early fusion:** concatenate static + dynamic feature vectors → single model
- **Late fusion:** ensemble the scores from independent models
- **Learned fusion:** neural network that learns to weight both representations

## Checkpoint Questions (Day 42)

> Where does dynamic outperform static, and where does it not — and why does
> that make sense given what each approach can see?

**Dynamic wins** on runtime-dependent behavior (injection, C2 callbacks, multi-stage
payloads, fileless techniques) because those produce no PE artifacts — they only
exist in the API call trace.

**Static wins** on pre-execution signals (PE anomalies, import patterns, section
characteristics) and on operational constraints (speed, scalability, resistance
to sandbox evasion). A packed sample's PE metadata is always available; its runtime
behavior may not be, if it detects the sandbox.

**Neither alone is enough** because sophisticated malware optimizes for one detection
axis (e.g., packing defeats static, sandbox detection defeats dynamic). Hybrid
detection forces attackers to evade both simultaneously, which is significantly harder.
