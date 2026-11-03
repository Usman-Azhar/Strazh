import json
from collections import Counter


def load_report(path):
    with open(path, "r") as f:
        return json.load(f)


def extract_api_sequences(report):
    """
    Pull ordered API call sequences from every process in the report.
    Returns a dict mapping (pid, process_name) -> list of API name strings,
    in the order they were logged.
    """
    sequences = {}
    processes = report.get("behavior", {}).get("processes", [])

    for proc in processes:
        pid = proc["pid"]
        name = proc["process_name"]
        calls = proc.get("calls", [])
        api_names = [call["api"] for call in calls]
        sequences[(pid, name)] = api_names

    return sequences


def extract_flat_sequence(report):
    """
    Merge all processes' API calls into one global sequence, ordered by
    timestamp. This is the input for n-gram and LSTM modeling later.
    """
    all_calls = []
    for proc in report.get("behavior", {}).get("processes", []):
        pid = proc["pid"]
        for call in proc.get("calls", []):
            all_calls.append({
                "timestamp": call["timestamp"],
                "api": call["api"],
                "category": call.get("category", "unknown"),
                "pid": pid,
                "process": proc["process_name"],
            })

    all_calls.sort(key=lambda c: c["timestamp"])
    return [c["api"] for c in all_calls]


def api_ngrams(api_list, n):
    """Build n-grams from an ordered API call list, same logic as opcode_ngrams."""
    return ["_".join(api_list[i:i + n]) for i in range(len(api_list) - n + 1)]


def api_ngram_counts(api_list, ns=(1, 2, 3)):
    """Count all n-grams for the given n values."""
    counts = Counter()
    for n in ns:
        counts.update(api_ngrams(api_list, n))
    return counts


def api_category_counts(report):
    """Count API calls per category (file, registry, process, network, etc.)."""
    counts = Counter()
    for proc in report.get("behavior", {}).get("processes", []):
        for call in proc.get("calls", []):
            counts[call.get("category", "unknown")] += 1
    return dict(counts)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m dynamic_sandbox.api_sequence <report.json>")
        sys.exit(1)

    report = load_report(sys.argv[1])

    print("=== Per-Process API Sequences ===")
    sequences = extract_api_sequences(report)
    for (pid, name), apis in sequences.items():
        print(f"\n[PID {pid}] {name} ({len(apis)} calls)")
        for api in apis:
            print(f"  {api}")

    print("\n=== Global Flat Sequence ===")
    flat = extract_flat_sequence(report)
    print(f"Total calls: {len(flat)}")
    for api in flat:
        print(f"  {api}")

    print("\n=== API Category Counts ===")
    cats = api_category_counts(report)
    for cat, count in sorted(cats.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {count}")

    print("\n=== Top 2-gram Counts ===")
    bigrams = api_ngram_counts(flat, ns=(2,))
    for ng, count in bigrams.most_common(10):
        print(f"  {ng}: {count}")
