# Day 33 - Dynamic Feature Vector Specification

Locked schema for the dynamic (behavioral) feature vector extracted from CAPEv2
reports. Every downstream module (batch extractor, cleaning, LSTM, Transformer,
fusion) references this spec as the single source of truth.

## Feature Groups

### Group A — API Call Sequence Features (variable-length)

These feed the LSTM / Transformer models (Days 39-41).

| Field | Type | Source |
|-------|------|--------|
| `api_sequence` | `list[str]` | Flat, timestamp-sorted API call names across all processes |
| `api_bigrams` | `Counter` | 2-gram counts over the flat sequence |
| `api_trigrams` | `Counter` | 3-gram counts over the flat sequence |

**Tokenizer contract (Day 39):** `api_sequence` is tokenized into integer IDs
using a vocabulary built from the training corpus. `<PAD>=0`, `<UNK>=1`,
real tokens start at 2. Max sequence length: 2048 (truncate from the right,
pad from the right).

### Group B — Behavioral Numeric Features (fixed-length, 10 dims)

These feed XGBoost / MLP tabular models and the fusion pipeline.

| # | Feature | Type | Extraction Module |
|---|---------|------|-------------------|
| 0 | `file_creates` | int | `behavior_draft.extract_file_operations` |
| 1 | `file_writes` | int | `behavior_draft.extract_file_operations` |
| 2 | `dropped_count` | int | `behavior_draft.extract_file_operations` |
| 3 | `dropped_pe_count` | int | `behavior_draft.extract_file_operations` |
| 4 | `registry_reads` | int | `behavior_draft.extract_registry_operations` |
| 5 | `registry_writes` | int | `behavior_draft.extract_registry_operations` |
| 6 | `persistence_writes` | int | `behavior_draft.extract_registry_operations` |
| 7 | `tree_depth` | int | `behavior_draft.extract_process_tree` |
| 8 | `tree_breadth` | int | `behavior_draft.extract_process_tree` |
| 9 | `total_processes` | int | `behavior_draft.extract_process_tree` |

### Group C — API Category Counts (fixed-length, 7 dims)

Normalized counts of API calls by category.

| # | Feature | Category Key |
|---|---------|-------------|
| 0 | `cat_file` | `file` |
| 1 | `cat_registry` | `registry` |
| 2 | `cat_process` | `process` |
| 3 | `cat_network` | `network` |
| 4 | `cat_system` | `system` |
| 5 | `cat_ui` | `ui` |
| 6 | `cat_other` | everything else |

### Group D — Network Indicator Flags (fixed-length, 4 dims)

Binary flags derived from the `network` section.

| # | Feature | Logic |
|---|---------|-------|
| 0 | `has_dns` | 1 if `network.dns` is non-empty |
| 1 | `has_http` | 1 if `network.http` is non-empty |
| 2 | `has_tcp` | 1 if `network.tcp` is non-empty |
| 3 | `has_udp` | 1 if `network.udp` is non-empty |

### Group E — Signature-Based Features (fixed-length, 2 dims)

| # | Feature | Logic |
|---|---------|-------|
| 0 | `signature_count` | total number of triggered signatures |
| 1 | `max_severity` | highest severity among triggered signatures (0 if none) |

## Combined Feature Vector

**Tabular vector** (Groups B + C + D + E): 23 dimensions, all numeric.
Used for XGBoost/MLP models and as the "dynamic side" in early fusion.

**Sequence vector** (Group A): variable-length list of API names → tokenized
to integer IDs. Used for LSTM/Transformer models and as the "dynamic side"
in learned fusion.

## Report-to-Feature Mapping

```
report.json
├── behavior.processes[].calls[]
│   ├── .api           → api_sequence, api_bigrams, api_trigrams
│   ├── .category      → cat_file ... cat_other
│   ├── file ops       → file_creates, file_writes
│   └── registry ops   → registry_reads, registry_writes, persistence_writes
├── behavior.processtree[]
│   └── recursive      → tree_depth, tree_breadth, total_processes
├── dropped[]
│   └── .type          → dropped_count, dropped_pe_count
├── network
│   ├── .dns           → has_dns
│   ├── .http          → has_http
│   ├── .tcp           → has_tcp
│   └── .udp           → has_udp
└── signatures[]
    ├── len()          → signature_count
    └── max(.severity) → max_severity
```

## Versioning

- **v1.0** (Day 33): initial lock — 23-dim tabular + variable-length sequence.
- Changes require a version bump and re-extraction of the full matrix.
