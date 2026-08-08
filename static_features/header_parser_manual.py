import sys
from dos_header_manual import read_dos_header
from file_header_manual import read_file_header
from optional_header_manual import read_optional_header

if __name__=="__main__":
    magic,lfanew=read_dos_header(sys.argv[1])
    print(f"e_magic : {hex(magic)}")
    print(f"e_lfanew : {hex(lfanew)}")

    machine,n_sections,ts,chars=read_file_header(sys.argv[1])
    print(f"Machine : {hex(machine)}") #(0x14c = x86, 0x8664 = x64)
    print(f"Number of sections : {n_sections}")
    print(f"TimeDateStamp : {ts}")
    print(f"Characteristics : {hex(chars)}")

    magic, ep, base, sub,directories = read_optional_header(sys.argv[1])
    print(f"Magic : {hex(magic)}") #(0x10b=PE32, 0x20b=PE32+)
    print(f"EntryPoint : {hex(ep)}")
    print(f"ImageBase : {hex(base)}")
    print(f"Subsystem : {sub}") #(2=GUI, 3=console)

    #printing directories
    names = [
        "Export Table",
        "Import Table",
        "Resource Table",
        "Exception Table",
        "Certificate Table",
        "Base Relocation Table",
        "Debug Directory",
        "Architecture",
        "Global Ptr",
        "TLS Table",
        "Load Config Table",
        "Bound Import",
        "Import Address Table",
        "Delay Import",
        "CLR Runtime Header",
        "Reserved"
    ]
    print("Data Directories")
    for i, (rva,size) in enumerate(directories):
        print(f"[{i:2}] {names[i]:22} RVA = {hex(rva):10} Size = {hex(size)}")    