"""
Day 36 — Data Cleaning for Dynamic Features

Handles failed/incomplete analyses, normalizes sequence lengths,
and applies padding/truncation strategy per dynamic_feature_spec.md v1.0.

Operates on the outputs of build_dynamic_matrix.py:
  - dynamic_features.csv  (tabular 23-dim)
  - api_sequences.json    (variable-length sequences)
"""

import csv
import json
import os
import sys

MAX_SEQ_LEN = 2048
MIN_SEQ_LEN = 3
PAD_TOKEN = "<PAD>"
UNK_TOKEN = "<UNK>"


def load_tabular(csv_path):
    with open(csv_path, "r") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    for row in rows:
        for key in row:
            if key != "sample_name":
                row[key] = int(row[key])
    return rows


def load_sequences(json_path):
    with open(json_path, "r") as f:
        return json.load(f)


def is_failed_analysis(row, sequence):
    if sequence is None or len(sequence) < MIN_SEQ_LEN:
        return True
    total_calls = sum(
        row.get(f"cat_{c}", 0)
        for c in ["file", "registry", "process", "network", "system", "ui", "other"]
    )
    if total_calls == 0:
        return True
    return False


def truncate_sequence(seq, max_len=MAX_SEQ_LEN):
    return seq[:max_len]


def pad_sequence(seq, target_len, pad_value=PAD_TOKEN):
    if len(seq) >= target_len:
        return seq
    return seq + [pad_value] * (target_len - len(seq))


def normalize_tabular_row(row):
    cleaned = dict(row)
    for key in cleaned:
        if key == "sample_name":
            continue
        val = cleaned[key]
        if val < 0:
            cleaned[key] = 0
    return cleaned


def clean_dataset(tabular_rows, sequences, max_seq_len=MAX_SEQ_LEN):
    cleaned_rows = []
    cleaned_seqs = {}
    removed = []

    for row in tabular_rows:
        name = row["sample_name"]
        seq = sequences.get(name, [])

        if is_failed_analysis(row, seq):
            removed.append(name)
            continue

        cleaned_row = normalize_tabular_row(row)
        cleaned_seq = truncate_sequence(seq, max_seq_len)

        cleaned_rows.append(cleaned_row)
        cleaned_seqs[name] = cleaned_seq

    return cleaned_rows, cleaned_seqs, removed


def compute_sequence_stats(sequences):
    if not sequences:
        return {"count": 0, "min_len": 0, "max_len": 0, "mean_len": 0, "median_len": 0}

    lengths = [len(seq) for seq in sequences.values()]
    lengths.sort()
    n = len(lengths)

    return {
        "count": n,
        "min_len": lengths[0],
        "max_len": lengths[-1],
        "mean_len": round(sum(lengths) / n, 1),
        "median_len": lengths[n // 2],
    }


def save_cleaned(rows, sequences, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    if rows:
        csv_path = os.path.join(output_dir, "dynamic_features_clean.csv")
        fieldnames = list(rows[0].keys())
        with open(csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        print(f"Wrote {len(rows)} clean rows to {csv_path}")

    seq_path = os.path.join(output_dir, "api_sequences_clean.json")
    with open(seq_path, "w") as f:
        json.dump(sequences, f, indent=2)
    print(f"Wrote {len(sequences)} clean sequences to {seq_path}")


if __name__ == "__main__":
    data_dir = sys.argv[1] if len(sys.argv) > 1 else "data/processed"
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "data/processed"

    csv_path = os.path.join(data_dir, "dynamic_features.csv")
    seq_path = os.path.join(data_dir, "api_sequences.json")

    if not os.path.exists(csv_path) or not os.path.exists(seq_path):
        print(f"Missing input files in {data_dir}. Run build_dynamic_matrix.py first.")
        sys.exit(1)

    tabular = load_tabular(csv_path)
    sequences = load_sequences(seq_path)

    print(f"Loaded {len(tabular)} tabular rows, {len(sequences)} sequences\n")

    before_stats = compute_sequence_stats(sequences)
    print(f"Before cleaning — {before_stats}")

    cleaned_rows, cleaned_seqs, removed = clean_dataset(tabular, sequences)

    if removed:
        print(f"\nRemoved {len(removed)} failed analyses:")
        for name in removed:
            print(f"  - {name}")

    after_stats = compute_sequence_stats(cleaned_seqs)
    print(f"\nAfter cleaning — {after_stats}")

    save_cleaned(cleaned_rows, cleaned_seqs, output_dir)
