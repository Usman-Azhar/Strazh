import math
import sys
from collections import Counter

def shannon_entropy(byte_data):
    if not byte_data:
        return 0.0

    counts=Counter(byte_data)
    total=len(byte_data)

    entropy=0.0

    for count in counts.values(): #we didn't do for byte_value in range(256): because it will also add entropy of bytes that are not present, causing log 0 that is undefined
        p=count/total
        entropy-= p*math.log2(p)

    return entropy

def section_entropy(file_data,raw_offset,raw_size):
    section_data=file_data[raw_offset:raw_offset+raw_size]

    return shannon_entropy(section_data)

if __name__ == '__main__':
    from static_features.sections_manual import read_sections

    path = sys.argv[1]
    with open(path, 'rb') as f:
        file_data = f.read()

    print(f"Whole-file entropy: {shannon_entropy(file_data):.4f}")

    for section in read_sections(path):
        e = section_entropy(file_data, section['raw_offset'], section['raw_size'])
        print(f"{section['name']:<10} entropy: {e:.4f}")