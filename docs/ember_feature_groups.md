# EMBER Feature Groups (Anderson & Roth, 2018)

Total vector length: 2381 (feature version 2)

| # | Group                     | Dim  | What it captures                                              | Mechanism           |
|---|----------------------------|------|-----------------------------------------------------------------|----------------------|
| 1 | General file information   | 10   | file size, vsize, has_debug/tls/resources/signature, import/export counts, symbol count | raw scalars |
| 2 | Header information         | 62   | COFF + optional header fields: machine, timestamp, characteristics, subsystem, linker/OS/subsystem versions, code/header/commit sizes | scalars + hashed strings (10 bins each) |
| 3 | Imported functions         | 1280 | which libraries (256 bins) and which lib:function pairs (1024 bins) are imported | feature hashing |
| 4 | Exported functions         | 128  | exported function names                                        | feature hashing |
| 5 | Section information        | 255  | per-section name/size/vsize/entropy/characteristics, hashed    | feature hashing (50 bins x several props) |
| 6 | Byte histogram             | 256  | count of each byte value 0x00-0xFF across the whole file        | histogram |
| 7 | Byte-entropy histogram     | 256  | joint (local entropy, byte value) distribution over sliding windows (16x16 bins) | 2D histogram |
| 8 | String statistics          | 104  | # strings, avg length, printable-char histogram, entropy, counts of C:\, http://, HKEY_, MZ | counts + histogram |
| 9 | Data directories (v2 add)  | 30   | RVA/size pairs for 15 data directory entries (imports, resources, etc.) | scalars |

**Format-agnostic groups (no parsing needed):** #6, #7, #8 — these work even on files LIEF fails to parse.
**Parsed groups (need a working PE parser):** #1-5, #9 — these need the header structures you built Days 2-6.
