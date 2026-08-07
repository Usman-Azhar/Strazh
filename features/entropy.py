import math
from collections import Counter

def shannon_entropy(byte_data: bytes) -> float:
    """Compute Shannon entropy (in bits) of a byte sequence."""
    if len(byte_data) == 0:
        return 0.0  # no data, no uncertainty

    total = len(byte_data)
    counts = Counter(byte_data)  # {byte_value: occurrences}

    entropy = 0.0
    for count in counts.values():
        p = count / total          # probability of this byte value
        entropy -= p * math.log2(p)  # accumulate -p*log2(p)

    return entropy


def section_entropies(file_path: str, sections: list[dict]) -> dict:
    """
    Compute entropy per section using Day 12's section offsets.
    sections: list of dicts with keys 'name', 'raw_offset', 'raw_size'
              (exactly what sections_manual.py already gives you)
    """
    with open(file_path, "rb") as f:
        data = f.read()

    results = {}
    for sec in sections:
        start = sec["raw_offset"]
        end = start + sec["raw_size"]
        chunk = data[start:end]   # slice out just this section's raw bytes
        results[sec["name"]] = shannon_entropy(chunk)

    return results


if __name__ == "__main__":
    import sys
    from static_features.sections_manual import parse_sections  # Day 12's function

    file_path = sys.argv[1]
    sections = parse_sections(file_path)
    ents = section_entropies(file_path, sections)

    for name, ent in ents.items():
        print(f"{name:10s} entropy: {ent:.3f}")