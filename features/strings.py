import re

MIN_LENGTH = 4  # anything shorter is too likely to be random noise

# --- extraction ---

def extract_ascii_strings(data: bytes, min_length: int = MIN_LENGTH) -> list[str]:
    """Find runs of printable ASCII bytes, 1 byte per character."""
    pattern = rb'[\x20-\x7e]{%d,}' % min_length  # printable ASCII range
    matches = re.findall(pattern, data)
    return [m.decode('ascii') for m in matches]


def extract_utf16le_strings(data: bytes, min_length: int = MIN_LENGTH) -> list[str]:
    """Find runs of printable chars stored as 2 bytes each, second byte usually 0x00."""
    pattern = rb'(?:[\x20-\x7e]\x00){%d,}' % min_length
    matches = re.findall(pattern, data)
    # strip the null bytes back out to get readable text
    return [m.decode('utf-16-le') for m in matches]


# --- categorization ---

URL_RE = re.compile(r'^(https?://)')
IP_RE = re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')
REGISTRY_RE = re.compile(r'^HK(EY_)?[A-Z_]+\\')
FILEPATH_RE = re.compile(r'^[A-Za-z]:\\|^\\\\')

SUSPICIOUS_KEYWORDS = [
    "cmd.exe", "powershell", "WinExec", "VirtualAlloc",
    "CreateRemoteThread", "RegSetValue", "URLDownloadToFile",
]

def categorize_string(s: str) -> str:
    """Simple rule-based labeling — first matching rule wins."""
    if URL_RE.match(s):
        return "url"
    if IP_RE.match(s):
        return "ip"
    if REGISTRY_RE.match(s):
        return "registry_path"
    if FILEPATH_RE.match(s):
        return "file_path"
    if any(keyword.lower() in s.lower() for keyword in SUSPICIOUS_KEYWORDS):
        return "suspicious_keyword"
    return "other"


def extract_and_categorize(path: str) -> list[dict]:
    """Full pipeline: read file, pull both string types, tag each one."""
    with open(path, 'rb') as f:
        data = f.read()

    all_strings = extract_ascii_strings(data) + extract_utf16le_strings(data)

    results = []
    for s in all_strings:
        results.append({"string": s, "category": categorize_string(s)})
    return results


if __name__ == "__main__":
    import sys
    from collections import Counter

    path = sys.argv[1]
    results = extract_and_categorize(path)

    print(f"Total strings found: {len(results)}")
    counts = Counter(r["category"] for r in results)
    for category, count in counts.most_common():
        print(f"  {category}: {count}")

    print("\nSample flagged strings:")
    for r in results:
        if r["category"] != "other":
            print(f"  [{r['category']}] {r['string']}")