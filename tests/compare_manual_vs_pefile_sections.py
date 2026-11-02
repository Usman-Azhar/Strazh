import pefile, sys
sys.path.append('static_features')
from sections_manual import read_sections

def compare(path):
    manual = read_sections(path)
    pe = pefile.PE(path)

    assert len(manual) == len(pe.sections), "Section count mismatch"

    for m, p in zip(manual, pe.sections):
        p_name = p.Name.rstrip(b'\x00').decode('utf-8', errors='replace')
        assert m['name'] == p_name, f"Name mismatch: {m['name']} vs {p_name}"
        assert m['virtual_address'] == p.VirtualAddress, f"{m['name']}: VA mismatch"
        assert m['virtual_size'] == p.Misc_VirtualSize, f"{m['name']}: VSize mismatch"
        assert m['raw_size'] == p.SizeOfRawData, f"{m['name']}: RawSize mismatch"
        assert m['raw_offset'] == p.PointerToRawData, f"{m['name']}: RawOffset mismatch"
        print(f"{m['name']:<8} OK")

    print("All sections match pefile output.")

if __name__ == '__main__':
    compare(sys.argv[1])