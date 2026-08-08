import sys, pefile
from capstone import Cs,CS_ARCH_X86,CS_MODE_32,CS_MODE_64

def disassemble_text(path):
    pe=pefile.PE(path) #this opens pe file

    #now we will check if the pe is 32 bit or 64 bit using pefile magic
    if pe.PE_TYPE==pefile.OPTIONAL_HEADER_MAGIC_PE_PLUS:
        mode= CS_MODE_64
        print("PE type: 64-bit")
    else:
        mode= CS_MODE_32
        print("PE type: 32-bit")

    #now we will find .text section 
    for section in pe.sections:
        name=section.Name.rstrip(b'\x00') #this removes trailing null bytes after a section's name

        if name==b'.text':
            code=section.get_data() #we will get raw bytes through this

            section_virtual_address=pe.OPTIONAL_HEADER.ImageBase + section.VirtualAddress #calculates virtual address

            break

        else:
           print(".text section not found") 
           return

    md = Cs(CS_ARCH_X86, mode) #this creates capstone disassembler

    print("\nAddress              Bytes                 Instruction")

    for instruction in md.disasm(code,section_virtual_address):
        print(
            f"0x{instruction.address:016x}  "
            f"{instruction.bytes.hex():<20} "
            f"{instruction.mnemonic:<8} "
            f"{instruction.op_str}"
        )


if __name__ == "__main__":
      disassemble_text(sys.argv[1])  