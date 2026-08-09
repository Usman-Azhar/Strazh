import os
import random

import pytest

from features.entropy import shannon_entropy, section_entropy
from static_features.sections_manual import read_sections

SAMPLE_PATH = os.path.join("data", "raw", "notepad.exe")


def test_all_zero_bytes():
    data = bytes(1000)  # 1000 zero bytes
    entropy = shannon_entropy(data)
    assert entropy == pytest.approx(0.0, abs=1e-9)


def test_uniform_random_bytes():
    random.seed(42)
    data = bytes(random.randint(0, 255) for _ in range(200_000))
    entropy = shannon_entropy(data)
    assert entropy == pytest.approx(8.0, abs=0.05)


@pytest.mark.skipif(not os.path.exists(SAMPLE_PATH), reason="sample EXE not present")
def test_real_text_section():
    with open(SAMPLE_PATH, "rb") as f:
        file_data = f.read()

    sections = read_sections(SAMPLE_PATH)
    text_section = next(
        (s for s in sections if s["name"] == ".text"), None
    )
    assert text_section is not None, "no .text section found in sample"

    entropy = section_entropy(
        file_data, text_section["raw_offset"], text_section["raw_size"]
    )

    assert 0.0 <= entropy <= 8.0
    assert entropy > 1.0  # real code shouldn't look near-zero either