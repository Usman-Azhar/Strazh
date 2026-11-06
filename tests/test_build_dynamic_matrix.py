"""Tests for Day 34 — build_dynamic_matrix.py"""

import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dynamic_sandbox.build_dynamic_matrix import (
    extract_network_flags,
    extract_signature_features,
    extract_category_counts,
    extract_all_features,
    build_matrix,
    TABULAR_COLUMNS,
)

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")


def _load(name):
    with open(os.path.join(FIXTURES, name)) as f:
        return json.load(f)


class TestNetworkFlags(unittest.TestCase):
    def test_benign_no_network(self):
        report = _load("cape_report_benign.json")
        flags = extract_network_flags(report)
        self.assertEqual(flags["has_dns"], 0)
        self.assertEqual(flags["has_http"], 0)
        self.assertEqual(flags["has_tcp"], 0)
        self.assertEqual(flags["has_udp"], 0)

    def test_suspicious_has_network(self):
        report = _load("cape_report_suspicious.json")
        flags = extract_network_flags(report)
        self.assertEqual(flags["has_dns"], 1)
        self.assertEqual(flags["has_http"], 1)
        self.assertEqual(flags["has_tcp"], 1)
        self.assertEqual(flags["has_udp"], 1)

    def test_missing_network_section(self):
        flags = extract_network_flags({})
        self.assertEqual(flags["has_dns"], 0)


class TestSignatureFeatures(unittest.TestCase):
    def test_benign_no_sigs(self):
        report = _load("cape_report_benign.json")
        sigs = extract_signature_features(report)
        self.assertEqual(sigs["signature_count"], 0)
        self.assertEqual(sigs["max_severity"], 0)

    def test_suspicious_sigs(self):
        report = _load("cape_report_suspicious.json")
        sigs = extract_signature_features(report)
        self.assertEqual(sigs["signature_count"], 3)
        self.assertEqual(sigs["max_severity"], 3)


class TestCategoryCounts(unittest.TestCase):
    def test_benign_categories(self):
        report = _load("cape_report_benign.json")
        cats = extract_category_counts(report)
        self.assertGreater(cats["cat_system"], 0)
        self.assertGreater(cats["cat_registry"], 0)
        self.assertGreater(cats["cat_file"], 0)
        self.assertEqual(cats["cat_network"], 0)

    def test_suspicious_categories(self):
        report = _load("cape_report_suspicious.json")
        cats = extract_category_counts(report)
        self.assertGreater(cats["cat_network"], 0)
        self.assertGreater(cats["cat_process"], 0)

    def test_all_known_categories_present(self):
        cats = extract_category_counts({})
        for key in ["cat_file", "cat_registry", "cat_process",
                    "cat_network", "cat_system", "cat_ui", "cat_other"]:
            self.assertIn(key, cats)


class TestExtractAllFeatures(unittest.TestCase):
    def test_feature_count(self):
        report = _load("cape_report_benign.json")
        feats = extract_all_features(report)
        expected_keys = set(TABULAR_COLUMNS) - {"sample_name"}
        self.assertTrue(expected_keys.issubset(set(feats.keys())))

    def test_all_values_numeric(self):
        report = _load("cape_report_suspicious.json")
        feats = extract_all_features(report)
        for key, val in feats.items():
            self.assertIsInstance(val, (int, float), f"{key} is not numeric")


class TestBuildMatrix(unittest.TestCase):
    def test_build_from_fixtures(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            count = build_matrix(FIXTURES, tmpdir)
            self.assertEqual(count, 2)
            self.assertTrue(os.path.exists(
                os.path.join(tmpdir, "dynamic_features.csv")))
            self.assertTrue(os.path.exists(
                os.path.join(tmpdir, "api_sequences.json")))

    def test_csv_has_header(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            build_matrix(FIXTURES, tmpdir)
            with open(os.path.join(tmpdir, "dynamic_features.csv")) as f:
                header = f.readline().strip()
            self.assertEqual(header, ",".join(TABULAR_COLUMNS))

    def test_sequences_json_structure(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            build_matrix(FIXTURES, tmpdir)
            with open(os.path.join(tmpdir, "api_sequences.json")) as f:
                seqs = json.load(f)
            self.assertEqual(len(seqs), 2)
            for name, seq in seqs.items():
                self.assertIsInstance(seq, list)
                self.assertTrue(all(isinstance(s, str) for s in seq))

    def test_empty_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            empty = os.path.join(tmpdir, "empty")
            os.makedirs(empty)
            count = build_matrix(empty, tmpdir)
            self.assertEqual(count, 0)


if __name__ == "__main__":
    unittest.main()
