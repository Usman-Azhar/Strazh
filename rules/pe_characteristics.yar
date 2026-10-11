import "pe"

rule Suspicious_Section_Count
{
    meta:
        description = "Flags PE files with an unusually high number of sections"
        author = "you"

    condition:
        // Uses YARA's built-in pe module - it parses the PE format for you,
        // same job as pefile in Day 6, just inside YARA's own engine.
        pe.is_pe and
        pe.number_of_sections > 6
}