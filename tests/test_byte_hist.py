from features.byte_hist import byte_histogram

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