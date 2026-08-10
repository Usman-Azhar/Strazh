import re
import sys

MIN_LENGTH=5

URL_PATTERN=re.compile(r"https?://[^\s]+",re.IGNORECASE)
IP_PATTERN=re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
REGISTRY_PATTERN=re.compile(r"\b(?:HKLM|HKCU|HKCR|HKU|HKCC)\\",re.IGNORECASE)
FILE_PATH_PATTERN=re.compile(r"(?:[A-Za-z]:\\|\\\\)[^\s]+")
SUSPICIOUS_KEYWORDS=["powershell","cmd.exe","rundll32","regsvr32","schtasks","wscript","cscript","winexec","virtualalloc","createremotethread",]

def extract_ascii_strings(data,min_length=MIN_LENGTH):
    pattern=rb"[\x20-\x7e]{" + str(min_length).encode()+rb",}"
    matches=re.findall(pattern,data)
    return [match.decode("ascii") for match in matches]

def extract_utf16le_strings(data,min_length=MIN_LENGTH):
    pattern=(rb"(?:[\x20-\x7e]\x00)" + b"{" + str(min_length).encode() + b",}")
    matches=re.findall(pattern,data)
    return [match.decode("utf-16le") for match in matches]

def extract_strings(data,min_length=MIN_LENGTH):
    ascii_strings=extract_ascii_strings(data,min_length)
    utf16_strings=extract_utf16le_strings(data,min_length)
    return ascii_strings + utf16_strings

def categorize_string(string):
    categories=[]

    if URL_PATTERN.search(string):
        categories.append("URL")

    if IP_PATTERN.search(string):
        categories.append("IP")

    if REGISTRY_PATTERN.search(string):
        categories.append("registry_path")

    if FILE_PATH_PATTERN.search(string):
        categories.append("file_path")

    lower_string=string.lower()

    for keyword in SUSPICIOUS_KEYWORDS:
        if keyword.lower() in lower_string:
            categories.append("suspicious_keyword")
            break

    if not categories: 
        categories.append("other")

    return categories

def analyze_strings(data,min_length=MIN_LENGTH):
    strings=extract_strings(data,min_length)
    results=[]

    for string in strings:
        results.append({"string":string,"categories":categorize_string(string)})

    return results

if __name__ == '__main__':
    path = sys.argv[1]
    with open(path, 'rb') as f:
        data = f.read()

    results = analyze_strings(data)

    print(f"Total strings extracted: {len(results)}\n")

    for r in results:
        if r["categories"] != ["other"]:
            print(f"{r['categories']}: {r['string'][:80]}")