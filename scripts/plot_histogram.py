import sys
import matplotlib.pyplot as plt
from features.byte_hist import byte_histogram

path = sys.argv[1]
with open(path, "rb") as f:
    data = f.read()

hist = byte_histogram(data)

plt.figure(figsize=(12, 4))
plt.bar(range(256), hist, width=1.0)
plt.xlabel("Byte value (0-255)")
plt.ylabel("Probability")
plt.title(f"Byte histogram: {path}")
plt.tight_layout()
plt.savefig("byte_histogram.png")
print("Saved byte_histogram.png") 