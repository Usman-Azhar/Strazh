import sys
import pefile

def dump_pefile_headers(path):
    pe = pefile.PE(path)  # one call does DOS + File + Optional + Data Dirs

    print(f"e_magic         : {hex(pe.DOS_HEADER.e_magic)}")
    print(f"e_lfanew        : {hex(pe.DOS_HEADER.e_lfanew)}")

    print(f"Machine         : {hex(pe.FILE_HEADER.Machine)}")
    print(f"NumberOfSections: {pe.FILE_HEADER.NumberOfSections}")
    print(f"TimeDateStamp   : {pe.FILE_HEADER.TimeDateStamp}")
    print(f"Characteristics : {hex(pe.FILE_HEADER.Characteristics)}")

    print(f"OptMagic        : {hex(pe.OPTIONAL_HEADER.Magic)}")
    print(f"EntryPoint      : {hex(pe.OPTIONAL_HEADER.AddressOfEntryPoint)}")
    print(f"ImageBase       : {hex(pe.OPTIONAL_HEADER.ImageBase)}")
    print(f"Subsystem       : {pe.OPTIONAL_HEADER.Subsystem}")

    # same 16 entries you parsed by hand on Day 5, now with resolved names
    for i, entry in enumerate(pe.OPTIONAL_HEADER.DATA_DIRECTORY):
        print(f"  [{i}] {entry.name:<25} RVA={hex(entry.VirtualAddress)} Size={entry.Size}")

    pe.close()

if __name__ == '__main__':
    dump_pefile_headers(sys.argv[1])