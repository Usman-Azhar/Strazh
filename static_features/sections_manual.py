import struct,sys

def read_sections(path):
    with open(path,'rb') as f:
        f.seek(60) #this gets to e_lfanew
        e_lfanew=struct.unpack('<I',f.read(4))[0]

        f.seek(e_lfanew+4) #gets us to file header
        file_header=f.read(20)
        number_of_sections=struct.unpack('<H',file_header[2:4])[0]

        size_of_optional_header=struct.unpack('<H',file_header[16:18])[0]

        #now section table starts (section headers)
        section_table_offset=(e_lfanew+4+20+size_of_optional_header)
        f.seek(section_table_offset)

        sections=[]

        for _ in range(number_of_sections):
            header=f.read(40) #since every section header is of 40 bytes

            name=header[0:8].rstrip(b'\x00').decode('ascii',errors='replace')
            virtual_size=struct.unpack('<I',header[8:12])[0]
            virtual_address=struct.unpack('<I',header[12:16])[0]
            raw_size=struct.unpack('<I',header[16:20])[0]
            raw_offset=struct.unpack('<I',header[20:24])[0]

            sections.append({
                'name': name,
                'virtual_size': virtual_size,
                'virtual_address': virtual_address,
                'raw_size': raw_size,
                'raw_offset': raw_offset
            })

    return sections

if __name__=='__main__':
    sections=[]
    sections=read_sections(sys.argv[1])
    for s in sections:
        print(f"Name           : {s['name']}")
        print(f"VirtualSize    : {hex(s['virtual_size'])} ({s['virtual_size']})")
        print(f"VirtualAddress : {hex(s['virtual_address'])}")
        print(f"RawSize        : {hex(s['raw_size'])} ({s['raw_size']})")
        print(f"RawOffset      : {hex(s['raw_offset'])}")
        print("-" * 40)