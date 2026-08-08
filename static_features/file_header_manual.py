import struct,sys
from dos_header_manual import read_dos_header

def read_file_header(path):
    with open(path,'rb') as f:
        f.seek(0) # this set the cursor to the beginning of the file
        _,e_lfanew=read_dos_header(path)
        f.seek(e_lfanew) #this sets the cursor the byte where PE header starts
        sig=f.read(4) #reading first 4 bytes will give us signature that is 'PE\0\0'
        assert sig==b'PE\x00\x00',f"A bad PE signature: {sig}"
        fh=f.read(20) #read next 20 bytes

    machine_type,section_count,timestamp=struct.unpack('<HHI',fh[0:8]) #H is for short i.e. two bytes
    characteristics=struct.unpack('<H',fh[18:20])[0]

    return machine_type,section_count,timestamp,characteristics

#if __name__=='__main__':
    #machine,n_sections,ts,chars=read_file_header(sys.argv[1])
    #print(f"Machine : {hex(machine)}") #(0x14c = x86, 0x8664 = x64)
    #print(f"Number of sections : {n_sections}")
    #print(f"TimeDateStamp : {ts}")
    #print(f"Characteristics : {hex(chars)}")

