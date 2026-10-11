import struct, sys
from static_features.dos_header_manual import read_dos_header
from static_features.file_header_manual import read_file_header
from static_features.optional_header_manual import read_optional_header, read_data_directories
from static_features.sections_manual import read_sections

SUSPICIOUS_APIS = {
    "WinExec", "VirtualAlloc", "VirtualAllocEx", "VirtualProtect",
    "CreateRemoteThread", "WriteProcessMemory", "LoadLibraryA",
    "GetProcAddress", "CreateProcessA", "ShellExecuteA",
}

def rva_to_offset(rva, sections):
    # Find which section's virtual range contains this RVA
    for sec in sections:
        va_start = sec['virtual_address']
        va_end = va_start + sec['virtual_size']
        if va_start <= rva < va_end:
            delta = rva - va_start          # how far into the section
            return sec['raw_offset'] + delta # same delta, but from disk start
    raise ValueError(f"RVA {hex(rva)} not inside any section")

def read_cstring(f, offset):
    # Null-terminated ASCII string at a given file offset
    f.seek(offset)
    out = b""
    while True:
        b = f.read(1)
        if b == b"\x00" or b == b"":
            break
        out += b
    return out.decode("ascii", errors="replace")

def get_import_table_rva_size(path):
    # Data Directory entry index 1 = Import Table (from Day 5's work)
    data_dirs = read_data_directories(path)
    import_rva, import_size = data_dirs[1]
    return import_rva, import_size

def parse_imports(path):
    magic, _, _, _ = read_optional_header(path)
    is_pe32_plus_flag = (magic == 0x20b)  # 0x20b = PE32+, need bitness for ILT entry size
    sections = read_sections(path)
    import_rva, _ = get_import_table_rva_size(path)
    import_offset = rva_to_offset(import_rva, sections)

    entry_size = 8 if is_pe32_plus_flag else 4  # ILT entries: 4 bytes on PE32, 8 on PE32+
    imports = {}

    with open(path, 'rb') as f:
        descriptor_offset = import_offset  # tracked separately from f's wandering cursor
        while True:
            f.seek(descriptor_offset)  # always read the descriptor from its own tracked spot
            descriptor = f.read(20)  # each Import Directory entry is 20 bytes
            if descriptor == b'\x00' * 20:
                break  # sentinel: no more DLLs

            orig_first_thunk, timestamp, fwd_chain, name_rva, first_thunk = \
                struct.unpack('<IIIII', descriptor)

            dll_name = read_cstring(f, rva_to_offset(name_rva, sections))

            # Some linkers omit OriginalFirstThunk; fall back to FirstThunk
            ilt_rva = orig_first_thunk if orig_first_thunk else first_thunk
            ilt_offset = rva_to_offset(ilt_rva, sections)

            functions = []
            cursor = ilt_offset
            while True:
                f.seek(cursor)
                thunk = f.read(entry_size)
                value = int.from_bytes(thunk, 'little')
                if value == 0:
                    break  # sentinel: end of this DLL's function list

                ordinal_flag_bit = 0x8000000000000000 if is_pe32_plus_flag else 0x80000000
                if value & ordinal_flag_bit:
                    functions.append(f"ordinal#{value & 0xFFFF}")  # imported by number, no name
                else:
                    hint_name_offset = rva_to_offset(value, sections)
                    fname = read_cstring(f, hint_name_offset + 2)  # skip 2-byte Hint field
                    functions.append(fname)

                cursor += entry_size

            imports[dll_name] = functions
            descriptor_offset += 20  # move to the next 20-byte descriptor, unaffected by name/ILT seeks

    return imports

if __name__ == '__main__':
    path = sys.argv[1]
    imports = parse_imports(path)

    for dll, funcs in imports.items():
        print(f"\n{dll}")
        for fn in funcs:
            flag = "  <-- suspicious-adjacent" if fn in SUSPICIOUS_APIS else ""
            print(f"  {fn}{flag}")