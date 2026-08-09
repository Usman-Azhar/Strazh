import sys
import matplotlib.pyplot as plt

from features.byte_hist import byte_histogram


def main():
    path = sys.argv[1]
    with open(path, 'rb') as f:
        file_data = f.read()

    hist = byte_histogram(file_data)

    plt.figure(figsize=(12, 4))
    plt.bar(range(256), hist, width=1.0)
    plt.xlabel("Byte value (0-255)")
    plt.ylabel("Probability")
    plt.title(f"Byte histogram: {path}")
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    main()