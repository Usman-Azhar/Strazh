import struct, sys

def read_dos_header(file_path):
    with open(file_path, 'rb') as f:
        data = f.read(64)  # Read the first 64 bytes of the file
    e_magic = struct.unpack('<H', data[0:2])[0]  # Read the e_magic field (2 bytes)
    e_lfanew = struct.unpack('<I', data[60:64])[0]  # Read the e_lfanew field (4 bytes)
    return e_magic, e_lfanew

if __name__ == "__main__":
    magic, lfanew = read_dos_header(sys.argv[1])
    print(f"e_magic: {hex(magic)} (expect 0x5a4d for 'MZ')")
    print(f"e_lfanew: {lfanew} (Byte offset where NT header starts)")