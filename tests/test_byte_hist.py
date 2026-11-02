from features.byte_hist import byte_histogram
from features.byte_hist import windowed_byte_entropy_histogram
import math

def test_histogram_sums_to_one():
    data = bytes([0, 1, 2, 3, 255] * 100)  # arbitrary repeated pattern
    hist = byte_histogram(data)
    assert abs(sum(hist) - 1.0) < 1e-9  # float rounding, so not exact ==

def test_histogram_length_always_256():
    data = bytes([0, 0, 0])
    hist = byte_histogram(data)
    assert len(hist) == 256

def test_all_zero_bytes_spikes_at_zero():
    data = bytes([0] * 1000)
    hist = byte_histogram(data)
    assert hist[0] == 1.0
    assert sum(hist[1:]) == 0.0
    
def test_windowed_histogram_sums_to_one():
    data = bytes(range(256)) * 20  # a few KB of varied, non-random bytes
    vec = windowed_byte_entropy_histogram(data)
    assert len(vec) == 256
    assert math.isclose(sum(vec), 1.0, abs_tol=1e-9)

def test_windowed_histogram_empty_input():
    vec = windowed_byte_entropy_histogram(b"")
    assert vec == [0.0] * 256

def test_all_zero_data_has_low_entropy_bin_concentration():
    data = bytes([0] * 5000)  # pure padding, no randomness anywhere
    vec = windowed_byte_entropy_histogram(data)
    # every window has entropy ~0, every byte is 0x00 -> should concentrate
    # almost entirely in entropy_bin=0, byte_bin=0 (the first cell of the grid)
    assert vec[0] > 0.9