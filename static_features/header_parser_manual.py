import sys
from dos_header_manual import read_dos_header 
from file_header_manual import read_file_header
from optional_header_manual import read_optional_header, read_data_directories

def parse_all(file_path):
    magic_dos, e_lfanew = read_dos_header(file_path)
    machine, n_sections, ts, chars = read_file_header(file_path)
    magic_opt, entry_point, image_base, subsystem = read_optional_header(file_path)
    directories = read_data_directories(file_path)

    print(f"--- {file_path} ---")
    print(f"DOS e_magic      : {hex(magic_dos)}")
    print(f"e_lfanew         : {hex(e_lfanew)}")
    print(f"Machine          : {hex(machine)}")
    print(f"NumberOfSections : {n_sections}")
    print(f"TimeDateStamp    : {ts}")
    print(f"Characteristics  : {hex(chars)}")
    print(f"Optional Magic   : {hex(magic_opt)}")
    print(f"EntryPoint       : {hex(entry_point)}")
    print(f"ImageBase        : {hex(image_base)}")
    print(f"Subsystem        : {subsystem}")
    print(f"Import Table RVA : {hex(directories[1][0])}, size: {directories[1][1]}")  # index 1 = imports

if __name__ == '__main__':
    parse_all(sys.argv[1])