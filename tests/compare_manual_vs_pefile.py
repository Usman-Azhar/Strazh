import sys, os
import pefile

# make static_features/ importable from tests/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'static_features'))
from dos_header_manual import read_dos_header
from file_header_manual import read_file_header
from optional_header_manual import read_optional_header

def compare(path):
    # --- your manual results (Days 2-4) ---
    m_magic, m_lfanew = read_dos_header(path)
    m_machine, m_nsec, m_ts, m_chars = read_file_header(path)
    m_opt_magic, m_ep, m_base, m_sub = read_optional_header(path)

    # --- pefile's results ---
    pe = pefile.PE(path)
    p_magic, p_lfanew = pe.DOS_HEADER.e_magic, pe.DOS_HEADER.e_lfanew
    p_machine  = pe.FILE_HEADER.Machine
    p_nsec     = pe.FILE_HEADER.NumberOfSections
    p_ts       = pe.FILE_HEADER.TimeDateStamp
    p_chars    = pe.FILE_HEADER.Characteristics
    p_opt_magic = pe.OPTIONAL_HEADER.Magic
    p_ep       = pe.OPTIONAL_HEADER.AddressOfEntryPoint
    p_base     = pe.OPTIONAL_HEADER.ImageBase
    p_sub      = pe.OPTIONAL_HEADER.Subsystem
    pe.close()

    checks = [
        ("e_magic", m_magic, p_magic), ("e_lfanew", m_lfanew, p_lfanew),
        ("Machine", m_machine, p_machine), ("NumberOfSections", m_nsec, p_nsec),
        ("TimeDateStamp", m_ts, p_ts), ("Characteristics", m_chars, p_chars),
        ("OptMagic", m_opt_magic, p_opt_magic), ("EntryPoint", m_ep, p_ep),
        ("ImageBase", m_base, p_base), ("Subsystem", m_sub, p_sub),
    ]

    print(f"\n--- {os.path.basename(path)} ---")
    all_ok = True
    for name, mine, theirs in checks:
        ok = mine == theirs
        all_ok &= ok
        print(f"{name:<18} manual={mine}  pefile={theirs}  [{'OK' if ok else 'MISMATCH'}]")

    assert all_ok, f"Mismatch found in {path}"

if __name__ == '__main__':
    sample_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')
    samples = [os.path.join(sample_dir, f) for f in os.listdir(sample_dir)
               if f.lower().endswith('.exe')]

    for s in samples:
        compare(s)

    print("\nAll samples match between manual parser and pefile.")