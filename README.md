# Strazh (Страж) — Hybrid Static + Dynamic Malware Detection Classifier

> *Strazh* — Russian for "Guardian" / "Sentinel".

A 12-week learning & build project combining **static PE feature extraction**
and **dynamic sandbox behavior analysis** into a hybrid ML classifier for
malware detection.

## Project Tracks

1. **Security Fundamentals** — PE format, headers, sections, entropy
2. **Static Feature Extraction** — EMBER-style features (pefile, lief, capstone, yara)
3. **Dynamic Sandboxing** — CAPEv2-based behavioral analysis
4. **ML / DL Modeling** — XGBoost baseline → deep learning fusion model
5. **Evaluation Rigor** — proper train/test splits, adversarial robustness checks

## Repo Structure

```
strazh/
├── static_features/    # PE parsing, header/entropy/import feature extraction
├── dynamic_sandbox/     # CAPEv2 configs, report parsing, behavior features
├── models/               # Trained model artifacts (gitignored, large files)
├── notebooks/            # Exploratory analysis, EDA
├── scripts/               # Utility & pipeline scripts
├── data/
│   ├── raw/               # Raw PE samples / sandbox reports (gitignored)
│   └── processed/         # Extracted feature CSVs/parquet
├── tests/                 # Unit tests
└── docs/                   # Notes, diagrams, writeups per day/week
```

## Setup

```bash
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Status

🟢 **Week 1, Day 1** — Environment setup + PE format orientation

## Disclaimer

This project is for defensive security research and education only.
No malware is authored, distributed, or weaponized here — only benign
samples and publicly available datasets/sandbox reports are used to
build a *detection* classifier.
