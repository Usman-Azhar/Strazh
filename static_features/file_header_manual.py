import struct, sys
from dos_header_manual import read_dos_header

def read_file_header(file_path):
    with open(file_path, 'rb') as f:
        _, e_lfanew = read_dos_header(file_path) #calculate the offset of the NT header
        f.seek(e_lfanew)
        sig = f.read(4) 
        assert sig == b'PE\x00\x00', f"Bad PE signature: {sig}" #check the PE signature
        fh = f.read(20) #Read the 20-byte file header
    machine, n_sections, timestamp = struct.unpack('<HHI', fh[0:8]) #Unpack the machine type, number of sections, and timestamp from the file header
    characteristics = struct.unpack('<H', fh[18:20])[0] #Unpack the characteristics field from the file header
    return machine, n_sections, timestamp, characteristics 

if __name__ == '__main__':
    machine, n_sections, ts, chars = read_file_header(sys.argv[1])
    print(f"Machine        : {hex(machine)} (0x14c = x86, 0x8664 = x64)")
    print(f"NumberOfSections: {n_sections}")
    print(f"TimeDateStamp  : {ts}")
    print(f"Characteristics: {hex(chars)}")