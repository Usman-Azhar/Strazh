"""Tests for Day 39 — models/tokenizer.py"""

import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from models.tokenizer import (
    APITokenizer, PAD_ID, UNK_ID, PAD_TOKEN, UNK_TOKEN,
    DEFAULT_MAX_LEN,
)


class TestAPITokenizerBuild(unittest.TestCase):
    def setUp(self):
        self.sequences = [
            ["NtCreateFile", "NtWriteFile", "RegSetValueExW"],
            ["NtCreateFile", "LdrLoadDll", "NtCreateFile"],
            ["InternetOpenUrlA", "HttpSendRequestA"],
        ]
        self.tok = APITokenizer(max_len=10, min_freq=1)
        self.tok.build_vocab(self.sequences)

    def test_special_tokens(self):
        self.assertEqual(self.tok.token2id[PAD_TOKEN], PAD_ID)
        self.assertEqual(self.tok.token2id[UNK_TOKEN], UNK_ID)

    def test_vocab_size(self):
        unique_apis = set(api for seq in self.sequences for api in seq)
        self.assertEqual(self.tok.vocab_size, len(unique_apis) + 2)

    def test_all_apis_present(self):
        for seq in self.sequences:
            for api in seq:
                self.assertIn(api, self.tok.token2id)

    def test_min_freq_filters(self):
        tok = APITokenizer(max_len=10, min_freq=2)
        tok.build_vocab(self.sequences)
        self.assertNotIn("RegSetValueExW", tok.token2id)
        self.assertIn("NtCreateFile", tok.token2id)


class TestAPITokenizerEncode(unittest.TestCase):
    def setUp(self):
        self.tok = APITokenizer(max_len=5, min_freq=1)
        self.tok.build_vocab([["A", "B", "C"]])

    def test_encode_known(self):
        ids = self.tok.encode(["A", "B", "C"])
        self.assertEqual(len(ids), 3)
        self.assertTrue(all(i >= 2 for i in ids))

    def test_encode_unknown(self):
        ids = self.tok.encode(["A", "UNKNOWN_API"])
        self.assertEqual(ids[1], UNK_ID)

    def test_encode_padded(self):
        ids = self.tok.encode_padded(["A", "B"])
        self.assertEqual(len(ids), 5)
        self.assertEqual(ids[2:], [PAD_ID, PAD_ID, PAD_ID])

    def test_truncation(self):
        ids = self.tok.encode(["A", "B", "C", "A", "B", "C", "A"])
        self.assertEqual(len(ids), 5)

    def test_decode(self):
        ids = self.tok.encode(["A", "B", "C"])
        decoded = self.tok.decode(ids)
        self.assertEqual(decoded, ["A", "B", "C"])

    def test_decode_skips_pad(self):
        ids = self.tok.encode_padded(["A"])
        decoded = self.tok.decode(ids)
        self.assertEqual(decoded, ["A"])


class TestAPITokenizerBatch(unittest.TestCase):
    def test_batch_encode_padded(self):
        tok = APITokenizer(max_len=4, min_freq=1)
        tok.build_vocab([["X", "Y", "Z"]])
        batch = tok.batch_encode([["X", "Y"], ["Z"]], pad=True)
        self.assertEqual(len(batch), 2)
        self.assertEqual(len(batch[0]), 4)
        self.assertEqual(len(batch[1]), 4)

    def test_batch_encode_unpadded(self):
        tok = APITokenizer(max_len=4, min_freq=1)
        tok.build_vocab([["X", "Y", "Z"]])
        batch = tok.batch_encode([["X", "Y"], ["Z"]], pad=False)
        self.assertEqual(len(batch[0]), 2)
        self.assertEqual(len(batch[1]), 1)


class TestAPITokenizerSaveLoad(unittest.TestCase):
    def test_roundtrip(self):
        tok = APITokenizer(max_len=100, min_freq=1)
        tok.build_vocab([["NtCreateFile", "LdrLoadDll", "RegSetValueExW"]])

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name

        try:
            tok.save(path)
            loaded = APITokenizer.load(path)

            self.assertEqual(tok.vocab_size, loaded.vocab_size)
            self.assertEqual(tok.max_len, loaded.max_len)
            self.assertEqual(tok.token2id, loaded.token2id)

            original = tok.encode(["NtCreateFile", "LdrLoadDll"])
            restored = loaded.encode(["NtCreateFile", "LdrLoadDll"])
            self.assertEqual(original, restored)
        finally:
            os.unlink(path)


class TestAPITokenizerSummary(unittest.TestCase):
    def test_summary_structure(self):
        tok = APITokenizer(max_len=10, min_freq=1)
        tok.build_vocab([["A", "B", "A"]])
        info = tok.summary()
        self.assertIn("vocab_size", info)
        self.assertIn("top_10", info)
        self.assertEqual(info["vocab_size"], 4)  # PAD, UNK, A, B


if __name__ == "__main__":
    unittest.main()
