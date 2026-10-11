import sys, pefile
from features.imports_manual import parse_imports

def pefile_imports(path):
    pe = pefile.PE(path)
    out = {}
    for entry in pe.DIRECTORY_ENTRY_IMPORT:
        dll = entry.dll.decode('ascii')
        funcs = []
        for imp in entry.imports:
            if imp.name:
                funcs.append(imp.name.decode('ascii'))
            else:
                funcs.append(f"ordinal#{imp.ordinal}")
        out[dll] = funcs
    return out

def compare(path):
    mine = parse_imports(path)
    theirs = pefile_imports(path)

    mine_dlls = set(mine.keys())
    theirs_dlls = set(theirs.keys())

    if mine_dlls != theirs_dlls:
        print(f"[{path}] DLL SET MISMATCH")
        print("  only mine:", mine_dlls - theirs_dlls)
        print("  only pefile:", theirs_dlls - mine_dlls)
        return False

    ok = True
    for dll in mine_dlls:
        if set(mine[dll]) != set(theirs[dll]):
            print(f"[{path}] {dll} function mismatch")
            print("  only mine:", set(mine[dll]) - set(theirs[dll]))
            print("  only pefile:", set(theirs[dll]) - set(mine[dll]))
            ok = False

    if ok:
        print(f"[{path}] MATCH ({len(mine_dlls)} DLLs)")
    return ok

if __name__ == '__main__':
    for path in sys.argv[1:]:
        compare(path)
