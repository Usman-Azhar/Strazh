"""
Day 34 — Batch Dynamic Feature Extractor

Reads a folder of CAPEv2 report JSONs and produces:
  1. dynamic_features.csv  — 23-dim tabular feature matrix (Groups B+C+D+E)
  2. api_sequences.json    — per-sample API call sequences (Group A)

Both outputs follow the schema locked in docs/dynamic_feature_spec.md v1.0.
"""

import csv
import glob
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from dynamic_sandbox.api_sequence import (
    extract_flat_sequence,
    api_category_counts,
)
from dynamic_sandbox.behavior_draft import extract_all_behavior_features


KNOWN_CATEGORIES = ["file", "registry", "process", "network", "system", "ui"]

TABULAR_COLUMNS = [
    "sample_name",
    "file_creates", "file_writes", "dropped_count", "dropped_pe_count",
    "registry_reads", "registry_writes", "persistence_writes",
    "tree_depth", "tree_breadth", "total_processes",
    "cat_file", "cat_registry", "cat_process", "cat_network",
    "cat_system", "cat_ui", "cat_other",
    "has_dns", "has_http", "has_tcp", "has_udp",
    "signature_count", "max_severity",
]


def extract_network_flags(report):
    net = report.get("network", {})
    return {
        "has_dns": 1 if net.get("dns") else 0,
        "has_http": 1 if net.get("http") else 0,
        "has_tcp": 1 if net.get("tcp") else 0,
        "has_udp": 1 if net.get("udp") else 0,
    }


def extract_signature_features(report):
    sigs = report.get("signatures", [])
    return {
        "signature_count": len(sigs),
        "max_severity": max((s.get("severity", 0) for s in sigs), default=0),
    }


def extract_category_counts(report):
    raw = api_category_counts(report)
    result = {}
    other = 0
    for cat, count in raw.items():
        if cat in KNOWN_CATEGORIES:
            result[f"cat_{cat}"] = count
        else:
            other += count
    for cat in KNOWN_CATEGORIES:
        result.setdefault(f"cat_{cat}", 0)
    result["cat_other"] = other
    return result


def extract_all_features(report):
    behavior = extract_all_behavior_features(report)
    categories = extract_category_counts(report)
    network = extract_network_flags(report)
    signatures = extract_signature_features(report)
    return {**behavior, **categories, **network, **signatures}


def build_matrix(reports_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    report_files = sorted(
        glob.glob(os.path.join(reports_dir, "*.json"))
    )

    if not report_files:
        print(f"No JSON reports found in {reports_dir}")
        return 0

    csv_path = os.path.join(output_dir, "dynamic_features.csv")
    seq_path = os.path.join(output_dir, "api_sequences.json")

    sequences = {}
    rows = []

    for path in report_files:
        name = os.path.basename(path)
        try:
            with open(path, "r") as f:
                report = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            print(f"  SKIP {name}: {e}")
            continue

        features = extract_all_features(report)
        features["sample_name"] = name

        flat_seq = extract_flat_sequence(report)
        sequences[name] = flat_seq

        rows.append(features)
        print(f"  OK {name}: {len(flat_seq)} API calls, "
              f"{features['total_processes']} processes")

    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=TABULAR_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow({col: row.get(col, 0) for col in TABULAR_COLUMNS})

    with open(seq_path, "w") as f:
        json.dump(sequences, f, indent=2)

    print(f"\nWrote {len(rows)} rows to {csv_path}")
    print(f"Wrote {len(sequences)} sequences to {seq_path}")
    return len(rows)


if __name__ == "__main__":
    reports = sys.argv[1] if len(sys.argv) > 1 else "data/raw/cape_reports"
    output = sys.argv[2] if len(sys.argv) > 2 else "data/processed"
    print(f"Building dynamic feature matrix from {reports}...\n")
    build_matrix(reports, output)
