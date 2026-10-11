from features.strings import (
    extract_ascii_strings, extract_utf16le_strings,
    categorize_string, extract_and_categorize,
)

def test_ascii_extraction_finds_plain_string():
    data = b"junk\x00\x01hello world\x02\x03junk"
    result = extract_ascii_strings(data)
    assert "hello world" in result

def test_utf16le_extraction_finds_windows_style_string():
    # "hello" stored the way Windows commonly stores it: 2 bytes/char
    data = "hello".encode('utf-16-le')
    result = extract_utf16le_strings(data)
    assert "hello" in result

def test_ascii_extraction_misses_utf16_strings():
    # this is the point of today's checkpoint - prove it with a test
    data = "hello".encode('utf-16-le')
    result = extract_ascii_strings(data)
    assert "hello" not in result

def test_categorize_url():
    assert categorize_string("http://fake-test-domain.example") == "url"

def test_categorize_suspicious_keyword():
    assert categorize_string("calls WinExec here") == "suspicious_keyword"

def test_categorize_plain_text():
    assert categorize_string("just some normal text") == "other"