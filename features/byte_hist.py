import sys
from collections import Counter
from features.entropy import shannon_entropy

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

def byte_entropy_histogram(byte_data,window_size=2048,step_size=1024):
    histogram=[[0 for _ in range(16)] for _ in range(16)]

    if not byte_data:
        return [0.0]*256

    for start in range(0,len(byte_data)-window_size+1,step_size):
        end=start+window_size
        window=byte_data[start:end]

        entropy=shannon_entropy(window)

        entropy_bin=int(entropy/8 *16)

        if entropy_bin>=16:
            entropy_bin=15

        for byte_value in window:
            byte_bin=byte_value//16

            histogram[entropy_bin][byte_bin] +=1

    flattened=[]

    for row in histogram:
        flattened.extend(row)

        #now normalising
    total=sum(flattened)
    if total==0:
        return [0.0]*256

    return [value/total for value in flattened]

if __name__ == '__main__':
    path = sys.argv[1]
    with open(path, 'rb') as f:
        file_data = f.read()

    hist = byte_histogram(file_data)
    beh = byte_entropy_histogram(file_data)

    print("Byte histogram")
    for byte_value, probability in enumerate(hist):
        if probability > 0:  # skip zero bins so output isn't 256 lines long
            print(f"0x{byte_value:02x}: {probability:.6f}")

    print("Byte Entropy Histogram")
    for i, probability in enumerate(beh):
        if probability > 0:
            entropy_bin, byte_bin = divmod(i, 16)
            print(f"entropy_bin={entropy_bin:2d} byte_bin={byte_bin:2d}: {probability:.6f}")
            
    print(f"\nSum of all bins: {sum(hist):.6f}")