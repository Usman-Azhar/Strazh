import struct, sys
from dos_header_manual import read_dos_header

def read_optional_header(file_path):
    with open(file_path, 'rb') as f:
        _, e_lfanew = read_dos_header(file_path) # get offset to NT headers
        f.seek(e_lfanew + 4 + 20)              # skip PE sig (4 bytes) + File Header (20 bytes)
        magic = struct.unpack('<H', f.read(2))[0]   # peek: which layout is this?
        f.seek(e_lfanew + 4 + 20)              # rewind, now read the whole header knowing its size
        is_pe32_plus = (magic == 0x20b) 
        blob = f.read(240 if is_pe32_plus else 224) #read the whole Optional Header, for PE32+ it's 240 bytes, for PE32 it's 224 bytes

    entry_point = struct.unpack('<I', blob[16:20])[0]
    image_base = struct.unpack(
        '<Q' if is_pe32_plus else '<I',
        blob[24:32] if is_pe32_plus else blob[28:32]
    )[0]
    subsystem = struct.unpack('<H', blob[68:70])[0]

    return magic, entry_point, image_base, subsystem
def read_data_directories(file_path):
    with open(file_path, 'rb') as f:
        _, e_lfanew = read_dos_header(file_path)
        f.seek(e_lfanew + 4 + 20)                    # skip PE sig + File Header
        magic = struct.unpack('<H', f.read(2))[0]
        is_pe32_plus = (magic == 0x20b)

        # fixed part of Optional Header ends at a different offset depending on PE32 vs PE32+
        fixed_size = 112 if is_pe32_plus else 96
        f.seek(e_lfanew + 4 + 20 + fixed_size)        # jump to start of Data Directories array

        directories = []
        for i in range(16):                            # always 16 entries, fixed by spec
            rva, size = struct.unpack('<II', f.read(8))  # 4-byte RVA + 4-byte size
            directories.append((rva, size))

    return directories

if __name__ == '__main__':
    magic, ep, base, sub = read_optional_header(sys.argv[1])
    print(f"Magic       : {hex(magic)} (0x10b=PE32, 0x20b=PE32+)")
    print(f"EntryPoint  : {hex(ep)}")
    print(f"ImageBase   : {hex(base)}")
    print(f"Subsystem   : {sub} (2=GUI, 3=console)")