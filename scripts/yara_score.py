import sys
import glob
import yara

RULES_DIR = "rules"
SAMPLES_DIR = "data/raw"

def load_rules(rules_dir):
    # yara.compile can take a dict of {namespace: filepath}
    # namespace just avoids rule-name collisions across files
    rule_files = glob.glob(f"{rules_dir}/*.yar")
    if not rule_files:
        print(f"No .yar files found in {rules_dir}")
        sys.exit(1)

    filepaths = {f"ns_{i}": path for i, path in enumerate(rule_files)}
    return yara.compile(filepaths=filepaths)

def score_file(compiled_rules, filepath):
    matches = compiled_rules.match(filepath)
    return matches  # list of yara.Match objects, empty list = no hits

def main():
    compiled_rules = load_rules(RULES_DIR)
    samples = glob.glob(f"{SAMPLES_DIR}/*.exe")

    if not samples:
        print(f"No .exe files found in {SAMPLES_DIR}")
        sys.exit(1)

    for sample in samples:
        matches = score_file(compiled_rules, sample)
        if matches:
            match_names = [str(m) for m in matches]
            print(f"{sample}: MATCH -> {match_names}")
        else:
            print(f"{sample}: no match")

if __name__ == "__main__":
    main()