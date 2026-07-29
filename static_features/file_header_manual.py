import struct, sys
from dos_header_manual import read_dos_header

def read_file_header(file_path):
    with open(file_path, 'rb') as f:
        _, e_lfanew = read_dos_header(file_path)  # get offset to NT headers
        f.seek(e_lfanew)                          # jump straight to that offset
        sig = f.read(4)                           # should be b'PE\x00\x00'
        assert sig == b'PE\x00\x00', f"Bad PE signature: {sig}"  # confirm it's really PE, not just MZ
        fh = f.read(20)                           # the 20-byte File Header, right after the signature

    # fields packed as: 2 bytes + 2 bytes + 4 bytes = first 8 bytes of fh
    machine, n_sections, timestamp = struct.unpack('<HHI', fh[0:8])
    characteristics = struct.unpack('<H', fh[18:20])[0]  # last 2 bytes of the 20-byte struct

    return machine, n_sections, timestamp, characteristics

if __name__ == '__main__':
    machine, n_sections, ts, chars = read_file_header(sys.argv[1])
    print(f"Machine        : {hex(machine)} (0x14c = x86, 0x8664 = x64)")
    print(f"NumberOfSections: {n_sections}")
    print(f"TimeDateStamp  : {ts}")
    print(f"Characteristics: {hex(chars)}")