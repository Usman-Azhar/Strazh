import struct, sys

def read_dos_header(path):
    with open(path,'rb') as f:
        data=f.read(64) #64 indicates 64 butes hsould be read and since dos header is exactly 64 bytes

    e_magic=struct.unpack('<H',data[0:2])[0] #the unpack returns a tuple so [0] only gets first value
    e_lfanew=struct.unpack('<I',data[60:64])[0] #last four bytes: this is where PE header starts 
    return e_magic,e_lfanew

#if __name__=='__main__':
    #magic,lfanew=read_dos_header(sys.argv[1])
    #print(f"e_magic : {hex(magic)}")
    #print(f"e_lfanew : {hex(lfanew)}")