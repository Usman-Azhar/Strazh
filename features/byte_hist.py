import sys
from collections import Counter

def byte_histogram(byte_data):
    if not byte_data:
        return [0.0]*256

    counts=Counter(byte_data)
    total=len(byte_data)

    histogram=[]

    for byte_value in range(256):
        probability=counts[byte_value]/total
        histogram.append(probability)

    return histogram

if __name__ == '__main__':
    path = sys.argv[1]
    with open(path, 'rb') as f:
        file_data = f.read()

    hist = byte_histogram(file_data)

    for byte_value, probability in enumerate(hist):
        if probability > 0:  # skip zero bins so output isn't 256 lines long
            print(f"0x{byte_value:02x}: {probability:.6f}")

    print(f"\nSum of all bins: {sum(hist):.6f}")