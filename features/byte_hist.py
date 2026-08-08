from collections import Counter

def byte_histogram(data: bytes) -> list[float]:
    """
    Compute a 256-bin normalized histogram of byte values in `data`.
    Returns a list of 256 floats that sum to 1.0.
    """
    if len(data) == 0:
        raise ValueError("Cannot compute histogram of empty data")

    total = len(data)
    counts = Counter(data)  # data is bytes -> iterating gives ints 0-255

    # Build a fixed-length 256-slot vector, defaulting to 0 for byte values
    # that never appeared (Counter only has entries for values that showed up)
    histogram = [0.0] * 256
    for byte_value, count in counts.items():
        histogram[byte_value] = count / total

    return histogram


if __name__ == "__main__":
    import sys

    path = sys.argv[1]
    with open(path, "rb") as f:
        data = f.read()

    hist = byte_histogram(data)
    print(f"File: {path}")
    print(f"Sum of histogram: {sum(hist):.6f}")  # sanity check, should be ~1.0
    print(f"Top 5 most common byte values:")
    ranked = sorted(range(256), key=lambda b: hist[b], reverse=True)
    for b in ranked[:5]:
        print(f"  0x{b:02x}: {hist[b]:.4f}")