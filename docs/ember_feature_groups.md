# EMBER Feature Groups (Anderson & Roth, 2018)

Reading notes for Strazh Day 10. Ground truth: `EMBER: An Open Dataset for Training Static PE
Machine Learning Models`, Anderson & Roth, arXiv:1804.04637.

## Feature group table

| # | Feature group | Type | Dimensionality | Source within PE file |
|---|----------------|------|-----------------|------------------------|
| 1 | General file information | Parsed | 10 | File size, virtual size, import/export counts, debug/TLS/resource/relocation/signature flags, symbol count |
| 2 | Header information | Parsed | 62 | COFF header (timestamp, machine, characteristics) + Optional header (subsystem, DLL characteristics, magic, linker/OS/subsystem versions, code/header/commit sizes) — string fields hashed at 10 bins each |
| 3 | Imported functions | Parsed | 1280 | Import Address Table: libraries hashed into 256 bins, `library:FunctionName` pairs hashed into 1024 bins |
| 4 | Exported functions | Parsed | 128 | Export table, hashed into 128 bins |
| 5 | Section information | Parsed | 255 | Section name/size/entropy/virtual-size hashed (50 bins × 5 sub-features) + entry-point section characteristics |
| 6 | Byte histogram | Format-agnostic | 256 | Normalized count of each of the 256 possible byte values across the whole file |
| 7 | Byte-entropy histogram | Format-agnostic | 256 | 2D joint distribution of local Shannon entropy × byte value, 2048-byte sliding window, 1024-byte step, 16×16 bins |
| 8 | String information | Format-agnostic | 104 | Printable-string stats (count, avg length, char histogram, entropy) + counts of `C:\`, `http(s)://`, `HKEY_`, `MZ` occurrences |
| | **Total** | | **2351** | |