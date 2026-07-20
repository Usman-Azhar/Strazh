# Strazh — Hybrid Static + Dynamic Malware Detection Classifier
### Day-by-Day Build Roadmap (manual-first, no library shortcuts until earned)

**How this file works — read this first, every session:**
1. Check the **File Index** table below — it tells you every file that exists and what it does, as of the most recent finished day.
2. Find "today's" Day section. Its **Builds on** line tells you which earlier files/concepts it needs.
3. Do the day. Append one row to the File Index for any new/modified file.
4. Do not skip the **Checkpoint** questions — if you can't answer them without looking at the code, the day isn't done yet, regardless of whether the script ran.

**Rule for every day:** manual/raw approach first, convenience library second — only once you've built the thing by hand do we swap in the library that does it for you. No day hands you a finished multi-function script to just run.

**Disclaimer:** defensive research only. No malware is authored or weaponized. Only benign samples, public datasets, and public sandbox reports are used.

---

## File Index (append one row per new/modified file — this is your project state)

| Day | File | What it does |
|---|---|---|
| 1 | .gitignore | ignores venv, raw samples, models from git tracking |
| 2 | static_features/dos_header_manual.py | reads raw bytes, extracts MZ signature + e_lfanew offset |

---

## Tech Stack Index (grows as tools get introduced)

| Tool | Introduced | Why |
|---|---|---|
| Python 3.10+, venv, git | Day 1 | base environment |
| `struct`, raw file I/O | Day 2 | manual byte parsing |
| `pefile` | Day 6 | PE parsing shortcut, only after manual version works |
| `capstone` | Day 9, 18 | disassembly |
| `yara-python` | Day 19 | signature scoring |
| `pandas`, `scikit-learn`, `xgboost` | Day 20-21 | ML on tabular features |
| VirtualBox/VMware, Windows guest VM | Day 22 | isolated dynamic analysis |
| CAPEv2 | Day 24-26 | sandbox |
| PyTorch | Day 38+ | sequence modeling |
| SHAP | Day 54 | explainability |

---

# Track 1 — Security Fundamentals (manual-first)

### Day 1 — Repo, environment, and orientation
**Builds on:** nothing — this is the start.
**Learn (20 min):** What a PE file conceptually is (an EXE/DLL container format for Windows). No code theory yet — just enough to know what you're about to build.
**Build:**
```bash
mkdir strazh && cd strazh
git init
python3 -m venv venv
source venv/bin/activate     # Windows: venv\Scripts\activate
mkdir static_features dynamic_sandbox models notebooks scripts tests docs data data/raw data/processed
echo "venv/\ndata/raw/\nmodels/\n__pycache__/" > .gitignore
pip install pandas  # just to confirm pip works — nothing else yet
```
Collect 4-5 small, real, benign Windows EXEs into `data/raw/` for testing all week (e.g. copies of `notepad.exe`, `calc.exe`, a couple of small open-source tool `.exe`s). These are your fixed test set — you'll reuse them constantly.
**Files:** `.gitignore`, empty folder skeleton, `data/raw/*.exe` (not committed — gitignored)
**Test:** `git status` shows a clean init; `ls data/raw` shows your sample EXEs.
**Checkpoint:** Can you say in one sentence what a PE file is, without looking anything up?
**Commit:** `Day 1 — repo skeleton, venv, sample EXEs collected`

---

### Day 2 — Read the DOS header by hand
**Builds on:** Day 1 (sample EXEs in `data/raw/`)
**Learn (30 min):** A file is just bytes on disk. `open(path, 'rb')` gives you raw bytes. `struct.unpack('<H', data)` turns 2 raw bytes into a number, little-endian (`<`). Every PE file's first 2 bytes are literally the ASCII characters `M` `Z` (0x4D, 0x5A).
**Build** (`static_features/dos_header_manual.py`):
```python
import struct, sys

def read_dos_header(path):
    with open(path, 'rb') as f:
        data = f.read(64)  # DOS header is exactly 64 bytes
    e_magic = struct.unpack('<H', data[0:2])[0]
    e_lfanew = struct.unpack('<I', data[60:64])[0]  # last 4 bytes: offset to NT headers
    return e_magic, e_lfanew

if __name__ == '__main__':
    magic, lfanew = read_dos_header(sys.argv[1])
    print(f"e_magic  : {hex(magic)}  (expect 0x5a4d = 'MZ')")
    print(f"e_lfanew : {hex(lfanew)}  (byte offset where NT headers start)")
```
No `pefile` yet — you are reading raw bytes at fixed offsets, by hand.
**Test:** `python static_features/dos_header_manual.py data/raw/notepad.exe` — should print `0x5a4d` and some offset (commonly `0xd8` or similar).
**Checkpoint:** Why is the offset at bytes 60-64 specifically? (Because the DOS header is a fixed 64-byte structure and `e_lfanew` is defined as its last field — it's not "found," it's a fixed position by spec.)
**Commit:** `Day 2 — manual DOS header parser`

---

### Day 3 — Read the NT File Header by hand
**Builds on:** Day 2 (`e_lfanew` tells you where this starts)
**Learn (30 min):** Right at `e_lfanew` sits a 4-byte signature `PE\0\0`, then a 20-byte File Header (machine type, section count, timestamp, characteristics flags).
**Build** (`static_features/file_header_manual.py`, imports from `dos_header_manual.py`):
```python
import struct, sys
from dos_header_manual import read_dos_header

def read_file_header(path):
    with open(path, 'rb') as f:
        f.seek(0)
        _, e_lfanew = read_dos_header(path)
        f.seek(e_lfanew)
        sig = f.read(4)
        assert sig == b'PE\x00\x00', f"Bad PE signature: {sig}"
        fh = f.read(20)
    machine, n_sections, timestamp = struct.unpack('<HHI', fh[0:8])
    characteristics = struct.unpack('<H', fh[18:20])[0]
    return machine, n_sections, timestamp, characteristics

if __name__ == '__main__':
    machine, n_sections, ts, chars = read_file_header(sys.argv[1])
    print(f"Machine        : {hex(machine)} (0x14c = x86, 0x8664 = x64)")
    print(f"NumberOfSections: {n_sections}")
    print(f"TimeDateStamp  : {ts}")
    print(f"Characteristics: {hex(chars)}")
```
**Test:** run against `notepad.exe` and `calc.exe`, compare outputs side by side.
**Checkpoint:** What would happen if the `PE\0\0` assert failed — what kind of file might trigger that?
**Commit:** `Day 3 — manual NT File Header parser, built on Day 2`

---

### Day 4 — Read the Optional Header by hand
**Builds on:** Day 3 (Optional Header sits immediately after the 20-byte File Header)
**Learn (30 min):** Optional Header size varies (32-bit vs 64-bit PE use different layouts) — you'll read the `Magic` field first (2 bytes) to know which struct format to use for the rest.
**Build** (`static_features/optional_header_manual.py`):
```python
import struct, sys
from dos_header_manual import read_dos_header

def read_optional_header(path):
    with open(path, 'rb') as f:
        _, e_lfanew = read_dos_header(path)
        f.seek(e_lfanew + 4 + 20)  # skip PE sig (4) + File Header (20)
        magic = struct.unpack('<H', f.read(2))[0]
        f.seek(e_lfanew + 4 + 20)  # re-read whole optional header from start
        is_pe32_plus = (magic == 0x20b)
        blob = f.read(240 if is_pe32_plus else 224)
    entry_point = struct.unpack('<I', blob[16:20])[0]
    image_base = struct.unpack('<Q' if is_pe32_plus else '<I',
                                blob[24:32] if is_pe32_plus else blob[28:32])[0]
    subsystem = struct.unpack('<H', blob[68:70])[0]
    return magic, entry_point, image_base, subsystem

if __name__ == '__main__':
    magic, ep, base, sub = read_optional_header(sys.argv[1])
    print(f"Magic        : {hex(magic)} (0x10b=PE32, 0x20b=PE32+)")
    print(f"EntryPoint   : {hex(ep)}")
    print(f"ImageBase    : {hex(base)}")
    print(f"Subsystem    : {sub} (2=GUI, 3=console)")
```
**Test:** run on your sample set — both `notepad.exe`/`calc.exe` should show Subsystem 2.
**Checkpoint:** Why did we need to check `Magic` before reading the rest of the struct?
**Commit:** `Day 4 — manual Optional Header parser`

---

### Day 5 — Data Directories by hand, and merge into one parser
**Builds on:** Day 4 (Data Directories array sits right after the fixed Optional Header fields)
**Learn (20 min):** 16 fixed-size (8-byte) entries: 4-byte RVA + 4-byte size. Entry 1 (index 1) is the Import Table — you'll use this exact entry in Day 17.
**Build:** extend `optional_header_manual.py` to also read the Data Directories, then create `static_features/header_parser_manual.py` that imports Days 2-5 and prints everything in one pass — this is your first "complete" manual tool.
**Files:** `optional_header_manual.py` (modified), `static_features/header_parser_manual.py` (new)
**Test:** `python static_features/header_parser_manual.py data/raw/notepad.exe` prints DOS + File + Optional + Data Directories, all from your own code, zero external libraries.
**Checkpoint:** Without looking at code, describe the chain: DOS header → ? → ? → Data Directories. Name what each arrow means (an offset, a fixed skip, etc).
**Commit:** `Day 5 — merged manual header parser, Data Directories added`

---

### Day 6 — Introduce `pefile`, validate against your own parser
**Builds on:** Day 5 (your manual parser is the ground truth to check against)
**Learn (20 min):** `pefile` does exactly what you just built, faster and more completely. You're not learning it blind — you're confirming it agrees with code you already understand.
**Build** (`static_features/header_dump_pefile.py`): use `pefile.PE(path)` to print the same fields your manual parser prints, then a small script `tests/compare_manual_vs_pefile.py` that runs both on the same file and asserts the key fields match.
**Test:** run the comparison script on all 4-5 sample EXEs — all fields should agree.
**Checkpoint:** Name two things `pefile` gives you for free that your manual parser doesn't yet (e.g. section objects, import name resolution).
**Commit:** `Day 6 — pefile introduced, validated against manual parser`

---

### Day 7 — Malware taxonomy (conceptual)
**Builds on:** nothing new technically — context day.
**Learn (45 min):** droppers, ransomware, trojans, worms, C2 patterns. Skim MITRE ATT&CK's Execution, Persistence, and C2 tactic pages.
**Build:** `docs/taxonomy_cheatsheet.md` — a 1-page table: behavior → ATT&CK technique ID.
**Test:** n/a (reading/writing day).
**Checkpoint:** Pick one ATT&CK technique and explain, in your own words, what a static feature extractor could ever hope to detect about it (vs. what only dynamic analysis could catch).
**Commit:** `Day 7 — malware taxonomy notes`

---

### Day 8 — x86 assembly refresher (conceptual)
**Learn (45 min):** registers, stack frames, calling conventions, common opcodes (`mov`, `push`, `call`, `jmp`). Use godbolt.org to compile small C snippets and read the ASM output.
**Build:** `docs/asm_notes.md` — map 10 simple C constructs (a loop, an if, a function call) to the ASM patterns you saw.
**Checkpoint:** Without Godbolt open, hand-write the ASM shape (just the pattern, not exact syntax) for `if (x > 5) { y = 1; }`.
**Commit:** `Day 8 — x86 assembly notes`

---

### Day 9 — Disassembly practice with capstone
**Builds on:** Day 8 (you now recognize opcodes when you see them)
**Learn (30 min):** `capstone` turns raw machine-code bytes into readable assembly text.
**Build:** `static_features/disasm_playground.py` — pick 2 easy crackmes from crackmes.one, disassemble their `.text` bytes (you can grab raw bytes manually the way you did in Day 2-5, or use `pefile`'s section access from Day 6), print the instruction stream.
**Test:** output should show a readable instruction sequence you can recognize from Day 8's notes.
**Checkpoint:** Point to one instruction in your output and explain what it's doing.
**Commit:** `Day 9 — capstone disassembly practice`

---

### Day 10 — EMBER paper
**Learn (60 min):** Read Anderson & Roth (2018) in full. Note the 2381-dim feature groups.
**Build:** `docs/ember_feature_groups.md` — table of each feature group and its dimensionality.
**Checkpoint:** Which EMBER feature group maps to what you built Days 2-6? Which maps to Day 9?
**Commit:** `Day 10 — EMBER paper notes`

---

### Day 11 — Consolidation / review
**Build:** nothing new — redraw the PE structure and EMBER feature groups from memory on paper, then check against your own Day 5/10 docs. Fix any gaps.
**Checkpoint:** Could you explain Days 2-10 to your teammate with zero code open? If not, that's today's actual task — go fix the gap before Day 12.
**Commit:** `Day 11 — review, no new code`

---

# Track 2 — Static Feature Extraction

### Day 12 — Section table, manual first
**Builds on:** Day 5 (`NumberOfSections` from File Header) + Day 6 (`pefile` available as check)
**Learn (20 min):** Right after the Optional Header + Data Directories sits an array of 40-byte section headers — name, virtual size, virtual address, raw size, raw offset.
**Build** (`static_features/sections_manual.py`): loop `NumberOfSections` times reading 40 bytes each, unpack name (8 bytes, strip nulls) + VA + raw size + raw offset. Cross-check against `pe.sections` from `pefile`.
**Test:** print section names for your sample set — should see `.text`, `.data`, `.rsrc` etc.
**Checkpoint:** What's the difference between a section's virtual size and its raw size, and why can they differ?
**Commit:** `Day 12 — manual section table parser, validated vs pefile`

---

### Day 13 — Entropy, from formula up
**Builds on:** Day 12 (need section byte ranges)
**Learn (30 min):** Shannon entropy formula, by hand: for each byte value 0-255, `p = count/total`, entropy `= -sum(p * log2(p))`.
**Build** (`features/entropy.py`): implement `shannon_entropy(byte_data) -> float` with no library shortcuts (just `math.log2` and a `Counter`), plus per-section entropy using Day 12's offsets. Write 3 unit tests (`tests/test_entropy.py`): all-zero bytes → ~0 entropy, uniform random bytes → ~8, a real `.text` section → somewhere in between.
**Test:** `pytest tests/test_entropy.py`; then pack one sample EXE with UPX and compare its `.text` entropy before/after.
**Checkpoint:** Why does entropy approach 8 for random data specifically, not some other number?
**Commit:** `Day 13 — entropy module + tests, UPX before/after comparison`

---

### Day 14 — Byte histogram
**Builds on:** Day 13 (byte counting logic reused)
**Build** (`features/byte_hist.py`): 256-bin raw byte-value histogram over the whole file, normalized to a probability vector.
**Test:** unit test confirming histogram sums to 1.0; visualize one sample's histogram (matplotlib, quick script is fine, not a formal notebook yet).
**Checkpoint:** What would a mostly-zero-padded file's histogram look like, and why?
**Commit:** `Day 14 — byte histogram feature`

---

### Day 15 — Windowed byte-entropy histogram (EMBER-style)
**Builds on:** Day 13 + Day 14
**Build** (`features/byte_hist.py`, extended): slide a fixed-size window across the file, compute (byte value, local entropy) pairs, bin into a 2D histogram, flatten to a feature vector — this is the actual EMBER-style feature from Day 10's notes.
**Checkpoint:** Why is a windowed version more informative than one global entropy number for detecting a partially-packed file?
**Commit:** `Day 15 — windowed byte-entropy histogram`

---

### Day 16 — String extraction
**Build** (`features/strings.py`): manual regex-based ASCII and UTF-16LE string extraction with a min-length filter, then simple categorization (URL, IP, registry path, file path, suspicious keyword list).
**Test:** run on sample set, check categorized output looks right for at least one known string in a test file you create on purpose (embed a fake URL string in a benign file copy — don't test on real malware).
**Checkpoint:** Why do both ASCII and UTF-16LE extraction matter separately?
**Commit:** `Day 16 — string extraction + categorization`

---

### Day 17 — Import table, manual RVA-to-offset walk
**Builds on:** Day 5 (Data Directory entry 1 = Import Table RVA) + Day 12 (section table needed to convert RVA → file offset)
**Learn (30 min):** RVA (virtual address) isn't a file offset — you must find which section contains the RVA, then compute `file_offset = raw_offset + (RVA - section_VA)`. This is the single trickiest manual step so far.
**Build** (`features/imports_manual.py`): write `rva_to_offset(rva, sections)`, then manually walk the Import Directory Table structure to pull DLL names and imported function names.
**Test:** compare your manual import list against `pe.DIRECTORY_ENTRY_IMPORT` from `pefile` on the same file — should match.
**Checkpoint:** Explain RVA-to-offset conversion in your own words, with a concrete number example from one of your sample files.
**Commit:** `Day 17 — manual import table parser with RVA conversion`

---

### Day 18 — Opcode n-grams
**Builds on:** Day 9 (capstone) + Day 12 (`.text` section bytes)
**Build** (`features/opcode_ngrams.py`): disassemble `.text`, extract 1-/2-/3-gram opcode sequences, vectorize top-N by frequency.
**Checkpoint:** Why might opcode n-grams catch something entropy and imports both miss?
**Commit:** `Day 18 — opcode n-gram features`

---

### Day 19 — YARA fundamentals
**Build:** write 3 YARA rules by hand (EICAR test string, a distinctive benign string from one of your samples, a PE-characteristic-based rule), score your sample set with `yara-python`.
**Files:** `rules/*.yar`, `scripts/yara_score.py`
**Checkpoint:** What's the difference between a YARA rule and everything you've built so far (Days 2-18)?
**Commit:** `Day 19 — YARA rules + scoring script`

---

### Day 20 — EMBER dataset EDA
**Build:** download EMBER 2018 pre-extracted features (endersgame/ember GitHub), load into pandas, explore label distribution, feature ranges, missing values.
**Files:** `notebooks/ember_eda.ipynb`
**Checkpoint:** What's the class balance, and why does that matter for Day 21's training?
**Commit:** `Day 20 — EMBER dataset EDA`

---

### Day 21 — Baseline static model
**Build:** train XGBoost on EMBER static features. Compute AUC-ROC, precision/recall/F1.
**Files:** `notebooks/baseline_static_model.ipynb`, `models/baseline_static.json` (gitignored)
**Checkpoint:** Which of your own hand-built features (Days 13-18) correspond to which EMBER columns driving the top feature importances?
**Commit:** `Day 21 — baseline static XGBoost model`

---

# Track 3 — Dynamic Sandboxing

### Day 22 — Isolated VM setup
**Build:** install VirtualBox/VMware, create Windows 10 guest VM, configure host-only networking (no internet from guest).
**Files:** `docs/vm_setup_notes.md`
**Test:** confirm from inside the guest that outbound internet is blocked, but host↔guest communication works.
**Checkpoint:** Why host-only, not NAT or bridged?
**Commit:** `Day 22 — isolated VM, host-only networking`

---

### Day 23 — Snapshot discipline
**Build:** practice snapshot → run → revert repeatedly; script the revert via VBoxManage CLI if possible.
**Files:** `scripts/snapshot_workflow.md`, `scripts/revert_snapshot.sh`
**Checkpoint:** What state must a snapshot capture to make revert actually safe for repeated malware runs?
**Commit:** `Day 23 — snapshot revert workflow`

---

### Day 24 — CAPEv2 host install, part 1 (dependencies + DB)
**Build:** follow kevoreilly/CAPEv2's official Ubuntu install guide through database + core dependency setup only — stop before web/API services.
**Files:** `docs/capev2_install_log.md` (record every command you actually ran and any deviation from the docs)
**Checkpoint:** What is CAPEv2's database actually storing?
**Commit:** `Day 24 — CAPEv2 host deps + DB installed`

---

### Day 25 — CAPEv2 host install, part 2 (web/API services)
**Builds on:** Day 24
**Build:** finish host-side install — web interface + API services running.
**Test:** CAPEv2 web UI loads locally.
**Checkpoint:** What's the API service's role vs the web UI's role?
**Commit:** `Day 25 — CAPEv2 web/API services running`

---

### Day 26 — CAPEv2 guest agent + smoke test
**Builds on:** Day 22 (VM) + Day 25 (host services)
**Build:** install the CAPE agent inside the Windows guest, wire host↔guest networking through the hypervisor only, submit one benign binary as a smoke test.
**Test:** first CAPEv2 report generated successfully.
**Checkpoint:** Trace the full path a submitted sample takes from your submission command to the report file.
**Commit:** `Day 26 — first CAPEv2 report generated`

---

### Day 27 — Debug buffer day
**Build:** whatever's broken from Day 26 — work CAPEv2 troubleshooting docs/GitHub issues until the smoke test is reliably repeatable.
**Checkpoint:** n/a — the checkpoint is "it works twice in a row."
**Commit:** `Day 27 — CAPEv2 stabilized`

---

### Day 28 — Report schema study
**Build:** `docs/cape_report_schema.md` — document `report.json`'s structure: behavior, network, dropped files, signatures sections.
**Checkpoint:** Which of these sections will feed Day 31-32's feature extraction, and which won't be used?
**Commit:** `Day 28 — CAPEv2 report schema notes`

---

### Day 29 — Batch smoke tests
**Build:** submit 3-5 more benign binaries through the full snapshot→run→revert cycle.
**Files:** clean sample reports saved under `data/raw/cape_reports/` (gitignored)
**Checkpoint:** Did any report come back incomplete or malformed? What did you do about it?
**Commit:** `Day 29 — batch benign reports collected`

---

### Day 30 — Public sandbox report comparison
**Build:** browse Any.Run and Hybrid-Analysis public reports (view only, defensive research), compare structure to your own CAPEv2 output.
**Files:** `docs/sandbox_comparison_notes.md`
**Checkpoint:** What's present in public reports that your CAPEv2 setup doesn't currently capture?
**Commit:** `Day 30 — public sandbox report comparison`

---

### Day 31 — API call sequence extraction
**Builds on:** Day 28 (schema) + Day 29 (real reports to parse)
**Build** (`dynamic_sandbox/api_sequence.py`): manual JSON parsing pulling ordered API call sequences out of `report.json`.
**Checkpoint:** Why does call *order* matter here, not just call *counts*?
**Commit:** `Day 31 — API call sequence parser`

---

### Day 32 — Behavior feature draft
**Build** (`dynamic_sandbox/behavior_draft.py`): draft extraction of file writes, registry writes, process tree depth/breadth from the same reports.
**Checkpoint:** Which of these three (file writes, registry writes, process tree) do you expect to be most different between benign software and typical malware, and why?
**Commit:** `Day 32 — behavior feature draft`

---

# Track 4a — Dynamic Feature Pipeline & Sequence Modeling

### Day 33 — Feature schema lock
**Build:** `docs/dynamic_feature_spec.md` — lock the dynamic feature vector spec: API call n-grams, registry-op counts, network indicator flags, process-tree depth/breadth.
**Commit:** `Day 33 — dynamic feature schema locked`

### Day 34 — Batch extractor
**Build** (`dynamic_sandbox/build_dynamic_matrix.py`): turn a folder of CAPEv2 reports into one feature matrix (CSV/parquet).
**Commit:** `Day 34 — batch dynamic feature extractor`

### Day 35 — Full corpus run
**Build:** run your full available sample corpus through CAPEv2, respecting snapshot discipline.
**Commit:** `Day 35 — full corpus dynamic reports collected`

### Day 36 — Data cleaning
**Build:** handle failed/incomplete analyses, normalize sequence lengths, decide padding/truncation strategy.
**Commit:** `Day 36 — cleaned dynamic feature matrix`

### Day 37 — Dynamic EDA
**Build:** `notebooks/dynamic_eda.ipynb` — sequence length distribution, most common API calls, class balance.
**Commit:** `Day 37 — dynamic EDA`

### Day 38 — Sequence modeling refresher
**Build:** PyTorch tutorial: embeddings → LSTM → classification head, on a toy dataset first.
**Commit:** `Day 38 — LSTM refresher notes + toy model`

### Day 39 — Tokenize API sequences
**Build** (`models/tokenizer.py`): vocabulary over API call names, tokenize sequences, embedding layer.
**Commit:** `Day 39 — API sequence tokenizer`

### Day 40 — Baseline LSTM
**Build:** `notebooks/dynamic_lstm_model.ipynb` — train an LSTM classifier on dynamic-only features.
**Commit:** `Day 40 — baseline LSTM model`

### Day 41 — Transformer alternative
**Build:** `notebooks/dynamic_transformer_model.ipynb` — small Transformer encoder, same sequences, compare stability/accuracy to LSTM.
**Commit:** `Day 41 — Transformer alternative model`

### Day 42 — Evaluate & compare
**Build:** precision/recall/F1/AUC for both; direct comparison table against Day 21's static baseline.
**Checkpoint:** Where does dynamic outperform static, and where does it not — and why does that make sense given what each approach can see?
**Commit:** `Day 42 — static vs dynamic comparison`

---

# Track 4b — Feature Fusion

### Day 43 — Fusion theory
**Build:** `docs/fusion_strategy_notes.md` — early vs late vs learned fusion, how EMBER-style and "Eating a Whole EXE" combine signals.
**Commit:** `Day 43 — fusion strategy notes`

### Day 44 — Early fusion
**Build:** `notebooks/fusion_early.ipynb` — concatenate static + dynamic vectors, feed into XGBoost or a small MLP.
**Commit:** `Day 44 — early fusion model`

### Day 45 — Late fusion
**Build:** `notebooks/fusion_late.ipynb` — train static and dynamic models independently, ensemble scores.
**Commit:** `Day 45 — late fusion model`

### Day 46 — Learned fusion
**Build:** `notebooks/fusion_learned.ipynb` — small neural net on top of both models' embeddings/logits.
**Commit:** `Day 46 — learned fusion model`

### Day 47 — Compare fusion strategies
**Build:** evaluate all three on the same validation split, pick and justify a winner.
**Checkpoint:** If you had to defend your choice to a skeptical reviewer, what's your one strongest argument?
**Commit:** `Day 47 — fusion strategy comparison + decision`

---

# Track 5 — Evaluation Rigor

### Day 48 — Time-based split
**Build:** re-split the full dataset by timestamp, not randomly (malware families cluster; random splits leak). Retrain final fusion model.
**Checkpoint:** Explain in your own words what "leakage" means here and why a random split would have hidden it.
**Commit:** `Day 48 — time-based split, retrained final model`

### Day 49 — Real-world metrics
**Build:** compute ROC-AUC and FPR@1%, FPR@0.1%.
**Commit:** `Day 49 — real-world metrics table`

### Day 50 — Error analysis
**Build:** inspect false positives/negatives individually, check clustering by family/software type.
**Files:** `docs/error_analysis.md`
**Commit:** `Day 50 — error analysis`

### Day 51 — Adversarial robustness note
**Build:** read how obfuscation/packing evades static-only models; repack one known-detected sample, check if score drops.
**Files:** `docs/robustness_note.md`
**Commit:** `Day 51 — adversarial robustness note`

### Day 52 — Finalize model
**Build:** lock hyperparameters, retrain final pipeline end-to-end (raw files → fusion score).
**Files:** `models/final_pipeline/` (gitignored)
**Commit:** `Day 52 — final model locked`

---

# Demo & Documentation

### Day 53 — Demo skeleton
**Build:** `scripts/demo_app.py` — CLI or Streamlit: upload a PE file → run static(+dynamic) extraction → show fusion score.
**Commit:** `Day 53 — demo app skeleton`

### Day 54 — Explainability
**Build:** add SHAP values for the static model, showing why a file scored the way it did.
**Commit:** `Day 54 — explainability panel`

### Day 55 — Architecture documentation
**Build:** `docs/architecture.md` — full pipeline diagram (raw file → extractors → fusion → score).
**Commit:** `Day 55 — architecture documentation`

### Day 56 — Limitations & future work
**Build:** `docs/limitations.md` — novel packers, anti-VM malware, dataset staleness.
**Commit:** `Day 56 — limitations documented`

### Day 57 — Dry run
**Build:** full end-to-end dry run of the demo as if presenting; fix rough edges.
**Commit:** `Day 57 — rehearsed working demo`

---

# Final Write-Up

### Day 58 — Report structure
**Build:** Introduction, Related Work (EMBER, Raff et al., CAPEv2), Methodology sections.
**Commit:** `Day 58 — report draft sections 1-3`

### Day 59 — Results & evaluation
**Build:** Results section with comparison tables and plots.
**Commit:** `Day 59 — report Results section`

### Day 60 — Discussion & ethics
**Build:** Discussion, Limitations, short Ethical Considerations note.
**Commit:** `Day 60 — report remaining sections`

### Day 61 — Polish
**Build:** proofread full report, format references, prepare slide deck if needed.
**Commit:** `Day 61 — polished report + slides`

### Day 62 — Final review & submit
**Build:** final read-through vs Day 1's goals, confirm demo still runs, submit/share.
**Commit:** `Day 62 — final submission`
