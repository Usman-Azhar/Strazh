import pytest

from features.strings import extract_ascii_strings, extract_utf16le_strings, categorize_string, analyze_strings


def test_ascii_extraction_basic():
    data = b"short\x00\x00hello world\x00\x00ab"  # "ab" is below min_length, should be dropped
    strings = extract_ascii_strings(data, min_length=5)
    assert "hello world" in strings
    assert "ab" not in strings


def test_utf16le_extraction_basic():
    text = "notepad.exe"
    data = text.encode("utf-16le")
    strings = extract_utf16le_strings(data, min_length=5)
    assert text in strings


def test_ascii_does_not_catch_utf16le():
    # UTF-16LE "hello" has null bytes between chars — should NOT show up
    # in the ASCII-only extractor since \x00 isn't a printable byte
    data = "hello".encode("utf-16le")
    strings = extract_ascii_strings(data, min_length=5)
    assert strings == []


def test_categorize_url():
    categories = categorize_string("check http://malicious-example.test/payload")
    assert "URL" in categories


def test_categorize_ip():
    categories = categorize_string("connect to 192.168.1.100 now")
    assert "IP" in categories


def test_categorize_registry():
    categories = categorize_string(r"HKLM\Software\Microsoft\Windows")
    assert "registry_path" in categories


def test_categorize_file_path():
    categories = categorize_string(r"C:\Windows\System32\drivers")
    assert "file_path" in categories


def test_categorize_suspicious_keyword():
    categories = categorize_string("launching powershell -enc payload")
    assert "suspicious_keyword" in categories


def test_categorize_other_fallback():
    categories = categorize_string("just a normal harmless label")
    assert categories == ["other"]


def test_embedded_fake_url_in_benign_copy(tmp_path):
    # Day 16's required test: embed a fake URL into a copy of a benign file,
    # confirm it's extracted and categorized correctly. No real malware used.
    fake_data = b"A" * 200 + b"http://fake-test-domain.example/beacon" + b"B" * 200

    results = analyze_strings(fake_data)
    url_hits = [r for r in results if "URL" in r["categories"]]

    assert len(url_hits) >= 1