import pefile

path= 'data/raw/Wireshark.exe'
pe=pefile.PE(path)

print("DOS HEADER")
print(f"e_magic      : {hex(pe.DOS_HEADER.e_magic)}")
print(f"e_lfanew     : {hex(pe.DOS_HEADER.e_lfanew)}")

print("\nNT HEADERS")
print(f"Signature    : {hex(pe.NT_HEADERS.Signature)}")

print("\nFILE HEADER")
print(f"Machine              : {hex(pe.FILE_HEADER.Machine)}")
print(f"NumberOfSections     : {pe.FILE_HEADER.NumberOfSections}")
print(f"TimeDateStamp        : {pe.FILE_HEADER.TimeDateStamp}")
print(f"PointerToSymbolTable : {hex(pe.FILE_HEADER.PointerToSymbolTable)}")
print(f"NumberOfSymbols      : {pe.FILE_HEADER.NumberOfSymbols}")
print(f"SizeOfOptionalHeader : {pe.FILE_HEADER.SizeOfOptionalHeader}")
print(f"Characteristics      : {hex(pe.FILE_HEADER.Characteristics)}")

print("\nOPTIONAL HEADER")
print(f"Magic                : {hex(pe.OPTIONAL_HEADER.Magic)}")
print(f"AddressOfEntryPoint  : {hex(pe.OPTIONAL_HEADER.AddressOfEntryPoint)}")
print(f"ImageBase            : {hex(pe.OPTIONAL_HEADER.ImageBase)}")
print(f"SectionAlignment     : {hex(pe.OPTIONAL_HEADER.SectionAlignment)}")
print(f"FileAlignment        : {hex(pe.OPTIONAL_HEADER.FileAlignment)}")
print(f"SizeOfImage          : {hex(pe.OPTIONAL_HEADER.SizeOfImage)}")
print(f"SizeOfHeaders        : {hex(pe.OPTIONAL_HEADER.SizeOfHeaders)}")
print(f"Subsystem            : {pe.OPTIONAL_HEADER.Subsystem}")
print(f"DllCharacteristics   : {hex(pe.OPTIONAL_HEADER.DllCharacteristics)}")
print(f"NumberOfRvaAndSizes  : {pe.OPTIONAL_HEADER.NumberOfRvaAndSizes}")

print("\nDATA DIRECTORIES")

for directory in pe.OPTIONAL_HEADER.DATA_DIRECTORY:
    print(
        f"{directory.name:30} "
        f"RVA = {hex(directory.VirtualAddress):>10} "
        f"Size = {hex(directory.Size)}"
    )

print("\nSECTIONS")

for section in pe.sections:
    print(f"Name                 : {section.Name.decode(errors='ignore').rstrip(chr(0))}")
    print(f"VirtualAddress       : {hex(section.VirtualAddress)}")
    print(f"VirtualSize          : {hex(section.Misc_VirtualSize)}")
    print(f"RawDataSize          : {hex(section.SizeOfRawData)}")
    print(f"PointerToRawData     : {hex(section.PointerToRawData)}")