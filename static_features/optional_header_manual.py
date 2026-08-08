import struct,sys
from dos_header_manual import read_dos_header

def read_optional_header(path):
    with open(path,'rb') as f:
        _,e_lfanew=read_dos_header(path)
        f.seek(e_lfanew+4+20) #this skips PE signature and file header
        magic=struct.unpack('<H',f.read(2))[0]
        f.seek(e_lfanew+4+20)
        is_pe32_plus = (magic==0x20b)
        blob=f.read(240 if is_pe32_plus else 224)

    entry_point=struct.unpack('<I',blob[16:20])[0]
    image_base=struct.unpack('<Q' if is_pe32_plus else '<I', blob[24:32] if is_pe32_plus else blob[28:32])[0]
    subsystem=struct.unpack('<H',blob[68:70])[0]

    #adding data directories functionality
    dd_offset=112 if is_pe32_plus else 96
    directories=[]

    for i in range(16): #since teher are at max 16 directories, if a certain directory is not there, so its RVA and size will say zero
        start=dd_offset+(i*8)
        rva,size=struct.unpack('<II',blob[start:start+8])
        directories.append((rva,size))

    return magic,entry_point,image_base,subsystem,directories


#if __name__=='__main__':
    #magic, ep, base, sub,directories = read_optional_header(sys.argv[1])
    #print(f"Magic : {hex(magic)}") #(0x10b=PE32, 0x20b=PE32+)
    #print(f"EntryPoint : {hex(ep)}")
    #print(f"ImageBase : {hex(base)}")
    #print(f"Subsystem : {sub}") #(2=GUI, 3=console)

    #printing directories
    #names = [
    #    "Export Table",
    #    "Import Table",
    #    "Resource Table",
    #    "Exception Table",
    #    "Certificate Table",
    #    "Base Relocation Table",
    #    "Debug Directory",
    #    "Architecture",
    #    "Global Ptr",
    #    "TLS Table",
    #    "Load Config Table",
    #    "Bound Import",
    #    "Import Address Table",
    #    "Delay Import",
    #    "CLR Runtime Header",
    #    "Reserved"
    #]
    #print("Data Directories")
    #for i, (rva,size) in enumerate(directories):
        #print(f"[{i:2}] {names[i]:2} RVA = {hex(rva):>10} Size = {hex(size)}")