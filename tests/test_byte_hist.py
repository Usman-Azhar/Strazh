import pytest

from features.byte_hist import byte_histogram


def test_histogram_sums_to_one():
    data = bytes([0, 1, 2, 3, 4, 5, 255] * 100)
    hist = byte_histogram(data)
    assert sum(hist) == pytest.approx(1.0, abs=1e-9)


def test_histogram_length_is_256():
    data = bytes([10, 20, 30])
    hist = byte_histogram(data)
    assert len(hist) == 256


def test_empty_input_returns_zero_vector():
    hist = byte_histogram(b"")
    assert hist == [0.0] * 256


def test_single_byte_value_concentrated():
    data = bytes([65] * 500)  # all 'A' (0x41)
    hist = byte_histogram(data)
    assert hist[65] == pytest.approx(1.0, abs=1e-9)
    assert sum(hist) == pytest.approx(1.0, abs=1e-9)
    # every other bin should be exactly zero
    assert all(p == 0.0 for i, p in enumerate(hist) if i != 65)


def test_known_distribution():
    # 4 zero-bytes and 1 one-byte -> bin 0 should be 0.8, bin 1 should be 0.2
    data = bytes([0, 0, 0, 0, 1])
    hist = byte_histogram(data)
    assert hist[0] == pytest.approx(0.8, abs=1e-9)
    assert hist[1] == pytest.approx(0.2, abs=1e-9)