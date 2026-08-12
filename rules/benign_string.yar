rule Known_Benign_String
{
    meta:
        description = "Matches a distinctive string pulled from one of my known-benign samples"
        author = "you"

    strings:
        // Replace this with a real string you found in one of your data/raw/ samples
        // (e.g. run `strings data/raw/notepad.exe | less` or reuse your Day 16 extractor)
        $s1 = "NOTEPAD.EXE" nocase
        $s2 = "This program cannot be run in DOS mode"

    condition:
        any of them
}