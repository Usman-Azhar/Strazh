import math
import random
from features.entropy import shannon_entropy

def test_all_zero_bytes_near_zero_entropy():
    data = bytes([0] * 10_000)
    ent = shannon_entropy(data)
    assert ent < 0.01  # essentially zero, only one symbol ever appears

def test_uniform_random_bytes_near_max_entropy():
    random.seed(42)
    data = bytes(random.randint(0, 255) for _ in range(50_000))
    ent = shannon_entropy(data)
    assert 7.9 <= ent <= 8.0  # close to the theoretical ceiling

def test_real_text_section_in_between():
    # swap this path for one of your own sample .text section dumps
    with open("data/raw/notepad_text_section.bin", "rb") as f:
        data = f.read()
    ent = shannon_entropy(data)
    assert 3.0 < ent < 7.0  # not flat, not random — typical code range