import math
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

def shannon_entropy(byte_data: bytes) -> float:
    """Copied reference from Day 13's entropy.py — same formula, used per-window here."""
    if len(byte_data) == 0:
        return 0.0
    counts = Counter(byte_data)
    total = len(byte_data)
    entropy = 0.0
    for count in counts.values():
        p = count / total
        entropy -= p * math.log2(p)
    return entropy


def windowed_byte_entropy_histogram(
    data: bytes, window_size: int = 2048, step: int = 1024
) -> list[float]:
    """EMBER-style 2D (byte, local-entropy) histogram, flattened to 256 floats."""
    ENTROPY_BINS = 16
    BYTE_BINS = 16

    grid = [[0] * BYTE_BINS for _ in range(ENTROPY_BINS)]  # [entropy_bin][byte_bin]

    if len(data) == 0:
        return [0.0] * (ENTROPY_BINS * BYTE_BINS)

    for start in range(0, len(data), step):
        window = data[start:start + window_size]
        if len(window) == 0:
            continue

        local_entropy = shannon_entropy(window)          # 0.0 to 8.0
        entropy_bin = min(int(local_entropy / 8 * ENTROPY_BINS), ENTROPY_BINS - 1)

        for b in window:
            byte_bin = b >> 4  # top 4 bits of the byte -> 16 coarse groups (0-15)
            grid[entropy_bin][byte_bin] += 1

    flat = [count for row in grid for count in row]  # flatten 16x16 -> 256
    total = sum(flat)
    if total == 0:
        return [0.0] * (ENTROPY_BINS * BYTE_BINS)

    return [c / total for c in flat]  # normalize to probability vector


if __name__ == "__main__":
    import sys
    import matplotlib.pyplot as plt
    import numpy as np  # only used here for reshape, not in the core function

    path = sys.argv[1]
    with open(path, 'rb') as f:
        data = f.read()

    vec = windowed_byte_entropy_histogram(data)
    grid = np.array(vec).reshape(16, 16)

    plt.imshow(grid, aspect='auto', origin='lower', cmap='viridis')
    plt.xlabel("Byte value bucket (0-15, top 4 bits)")
    plt.ylabel("Local entropy bucket (0-15)")
    plt.title(f"Windowed byte-entropy histogram: {path}")
    plt.colorbar(label="Probability")
    plt.show()