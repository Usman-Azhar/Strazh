import sys
import pefile
from capstone import Cs, CS_ARCH_X86, CS_MODE_32, CS_MODE_64

def disassemble_text_section(file_path, max_instructions=40):
    pe = pefile.PE(file_path)  # reuse Day 6's tool instead of re-deriving offsets by hand

    # pick 32 vs 64-bit decode mode the same way Day 4 picked struct format
    is_64bit = pe.FILE_HEADER.Machine == 0x8664
    mode = CS_MODE_64 if is_64bit else CS_MODE_32

    # find the .text section among all sections
    text_section = None
    for section in pe.sections:
        name = section.Name.decode(errors="ignore").rstrip('\x00')
        if name == '.text':
            text_section = section
            break

    if text_section is None:
        print("No .text section found")
        return

    code_bytes = text_section.get_data()          # raw machine code bytes
    start_addr = pe.OPTIONAL_HEADER.ImageBase + text_section.VirtualAddress

    md = Cs(CS_ARCH_X86, mode)                     # create the disassembly engine
    count = 0
    for instr in md.disasm(code_bytes, start_addr):
        print(f"0x{instr.address:x}:\t{instr.mnemonic}\t{instr.op_str}")
        count += 1
        if count >= max_instructions:              # crackmes can be huge; cap output
            break

if __name__ == '__main__':
    disassemble_text_section(sys.argv[1])