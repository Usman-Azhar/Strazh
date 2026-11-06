"""Tests for Day 36 — clean_dynamic_data.py"""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dynamic_sandbox.clean_dynamic_data import (
    is_failed_analysis,
    truncate_sequence,
    pad_sequence,
    normalize_tabular_row,
    clean_dataset,
    compute_sequence_stats,
    MAX_SEQ_LEN,
    MIN_SEQ_LEN,
    PAD_TOKEN,
)


class TestIsFailedAnalysis(unittest.TestCase):
    def test_none_sequence(self):
        row = {"cat_file": 5, "cat_registry": 0, "cat_process": 0,
               "cat_network": 0, "cat_system": 0, "cat_ui": 0, "cat_other": 0}
        self.assertTrue(is_failed_analysis(row, None))

    def test_too_short_sequence(self):
        row = {"cat_file": 1, "cat_registry": 0, "cat_process": 0,
               "cat_network": 0, "cat_system": 0, "cat_ui": 0, "cat_other": 0}
        self.assertTrue(is_failed_analysis(row, ["api1", "api2"]))

    def test_zero_total_calls(self):
        row = {"cat_file": 0, "cat_registry": 0, "cat_process": 0,
               "cat_network": 0, "cat_system": 0, "cat_ui": 0, "cat_other": 0}
        self.assertTrue(is_failed_analysis(row, ["a", "b", "c", "d"]))

    def test_valid_analysis(self):
        row = {"cat_file": 5, "cat_registry": 3, "cat_process": 0,
               "cat_network": 0, "cat_system": 2, "cat_ui": 0, "cat_other": 0}
        self.assertFalse(is_failed_analysis(row, ["a", "b", "c", "d"]))


class TestTruncateSequence(unittest.TestCase):
    def test_short_unchanged(self):
        seq = ["a", "b", "c"]
        self.assertEqual(truncate_sequence(seq, 10), ["a", "b", "c"])

    def test_long_truncated(self):
        seq = list(range(100))
        result = truncate_sequence(seq, 50)
        self.assertEqual(len(result), 50)
        self.assertEqual(result[0], 0)
        self.assertEqual(result[49], 49)

    def test_exact_length(self):
        seq = ["a", "b", "c"]
        self.assertEqual(truncate_sequence(seq, 3), ["a", "b", "c"])


class TestPadSequence(unittest.TestCase):
    def test_pad_short(self):
        result = pad_sequence(["a", "b"], 5, PAD_TOKEN)
        self.assertEqual(len(result), 5)
        self.assertEqual(result[:2], ["a", "b"])
        self.assertEqual(result[2:], [PAD_TOKEN] * 3)

    def test_no_pad_needed(self):
        result = pad_sequence(["a", "b", "c"], 3, PAD_TOKEN)
        self.assertEqual(result, ["a", "b", "c"])

    def test_already_longer(self):
        result = pad_sequence(["a", "b", "c"], 2, PAD_TOKEN)
        self.assertEqual(result, ["a", "b", "c"])


class TestNormalizeTabularRow(unittest.TestCase):
    def test_negative_clamped(self):
        row = {"sample_name": "test.json", "file_creates": -1, "registry_reads": 5}
        result = normalize_tabular_row(row)
        self.assertEqual(result["file_creates"], 0)
        self.assertEqual(result["registry_reads"], 5)
        self.assertEqual(result["sample_name"], "test.json")


class TestCleanDataset(unittest.TestCase):
    def test_removes_failed(self):
        rows = [
            {"sample_name": "good.json", "cat_file": 5, "cat_registry": 3,
             "cat_process": 0, "cat_network": 0, "cat_system": 2,
             "cat_ui": 0, "cat_other": 0},
            {"sample_name": "bad.json", "cat_file": 0, "cat_registry": 0,
             "cat_process": 0, "cat_network": 0, "cat_system": 0,
             "cat_ui": 0, "cat_other": 0},
        ]
        seqs = {
            "good.json": ["a", "b", "c", "d", "e"],
            "bad.json": ["x"],
        }
        cleaned_rows, cleaned_seqs, removed = clean_dataset(rows, seqs)
        self.assertEqual(len(cleaned_rows), 1)
        self.assertEqual(cleaned_rows[0]["sample_name"], "good.json")
        self.assertIn("bad.json", removed)

    def test_truncates_long_seqs(self):
        row = {"sample_name": "long.json", "cat_file": 5, "cat_registry": 0,
               "cat_process": 0, "cat_network": 0, "cat_system": 0,
               "cat_ui": 0, "cat_other": 0}
        long_seq = ["api"] * 3000
        cleaned_rows, cleaned_seqs, _ = clean_dataset(
            [row], {"long.json": long_seq})
        self.assertEqual(len(cleaned_seqs["long.json"]), MAX_SEQ_LEN)


class TestComputeSequenceStats(unittest.TestCase):
    def test_empty(self):
        stats = compute_sequence_stats({})
        self.assertEqual(stats["count"], 0)

    def test_basic_stats(self):
        seqs = {"a": [1, 2, 3], "b": [1, 2, 3, 4, 5], "c": [1]}
        stats = compute_sequence_stats(seqs)
        self.assertEqual(stats["count"], 3)
        self.assertEqual(stats["min_len"], 1)
        self.assertEqual(stats["max_len"], 5)
        self.assertEqual(stats["mean_len"], 3.0)


if __name__ == "__main__":
    unittest.main()
