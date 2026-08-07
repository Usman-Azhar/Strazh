import struct, sys
from dos_header_manual import read_dos_header
from file_header_manual import read_file_header
from static_features.dos_header_manual import read_dos_header
from static_features.optional_header_manual import read_optional_header

SECTION_HEADER_SIZE = 40  # fixed by spec, no exceptions

def read_sections(path):
    with open(path, 'rb') as f:
        # re-derive everything we need from earlier days' parsers
        _, e_lfanew = read_dos_header(path)
        _, n_sections, _, _ = read_file_header(path)
        magic, _, _, _ = read_optional_header(path)

        is_pe32_plus = (magic == 0x20b)
        optional_header_size = 240 if is_pe32_plus else 224  # matches Day 4's blob sizes

        # section table starts right after: e_lfanew + PE sig(4) + File Header(20) + Optional Header
        section_table_offset = e_lfanew + 4 + 20 + optional_header_size
        f.seek(section_table_offset)

        sections = []
        for _ in range(n_sections):
            raw = f.read(SECTION_HEADER_SIZE)

            (name_bytes, virtual_size, virtual_address,
             size_of_raw_data, pointer_to_raw_data,
             _reloc_ptr, _linenum_ptr,
             _n_relocs, _n_linenums,
             characteristics) = struct.unpack('<8sIIIIIIHHI', raw)

            name = name_bytes.rstrip(b'\x00').decode('utf-8', errors='replace')

            sections.append({
                'name': name,
                'virtual_size': virtual_size,
                'virtual_address': virtual_address,
                'raw_size': size_of_raw_data,
                'raw_offset': pointer_to_raw_data,
                'characteristics': characteristics,
            })
        return sections

if __name__ == '__main__':
    for s in read_sections(sys.argv[1]):
        print(f"{s['name']:<8} "
              f"VA={hex(s['virtual_address']):<10} VSize={hex(s['virtual_size']):<10} "
              f"RawOffset={hex(s['raw_offset']):<10} RawSize={hex(s['raw_size'])}")