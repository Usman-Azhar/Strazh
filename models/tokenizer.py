"""
Day 39 — API Sequence Tokenizer

Builds a vocabulary over API call names from CAPEv2 reports and converts
variable-length API sequences into padded integer tensors for LSTM/Transformer
input. Follows the tokenizer contract in docs/dynamic_feature_spec.md v1.0:

    <PAD> = 0, <UNK> = 1, real tokens start at 2.
    Max sequence length: 2048 (truncate right, pad right).
"""

import json
import os
from collections import Counter


PAD_TOKEN = "<PAD>"
UNK_TOKEN = "<UNK>"
PAD_ID = 0
UNK_ID = 1
DEFAULT_MAX_LEN = 2048
DEFAULT_MIN_FREQ = 1


class APITokenizer:
    def __init__(self, max_len=DEFAULT_MAX_LEN, min_freq=DEFAULT_MIN_FREQ):
        self.max_len = max_len
        self.min_freq = min_freq
        self.token2id = {PAD_TOKEN: PAD_ID, UNK_TOKEN: UNK_ID}
        self.id2token = {PAD_ID: PAD_TOKEN, UNK_ID: UNK_TOKEN}
        self.token_counts = Counter()

    @property
    def vocab_size(self):
        return len(self.token2id)

    def build_vocab(self, sequences):
        self.token_counts = Counter()
        for seq in sequences:
            self.token_counts.update(seq)

        self.token2id = {PAD_TOKEN: PAD_ID, UNK_TOKEN: UNK_ID}
        for token, count in self.token_counts.most_common():
            if count >= self.min_freq:
                self.token2id[token] = len(self.token2id)

        self.id2token = {v: k for k, v in self.token2id.items()}
        return self

    def encode(self, sequence):
        ids = [self.token2id.get(api, UNK_ID) for api in sequence[:self.max_len]]
        return ids

    def encode_padded(self, sequence):
        ids = self.encode(sequence)
        ids += [PAD_ID] * (self.max_len - len(ids))
        return ids

    def decode(self, ids):
        return [self.id2token.get(i, UNK_TOKEN) for i in ids if i != PAD_ID]

    def batch_encode(self, sequences, pad=True):
        if pad:
            return [self.encode_padded(seq) for seq in sequences]
        return [self.encode(seq) for seq in sequences]

    def save(self, path):
        data = {
            "max_len": self.max_len,
            "min_freq": self.min_freq,
            "token2id": self.token2id,
            "token_counts": dict(self.token_counts),
        }
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load(cls, path):
        with open(path, "r") as f:
            data = json.load(f)
        tok = cls(max_len=data["max_len"], min_freq=data["min_freq"])
        tok.token2id = data["token2id"]
        tok.id2token = {int(v): k for k, v in tok.token2id.items()}
        tok.token_counts = Counter(data.get("token_counts", {}))
        return tok

    def summary(self):
        return {
            "vocab_size": self.vocab_size,
            "max_len": self.max_len,
            "min_freq": self.min_freq,
            "total_unique_apis": len(self.token_counts),
            "top_10": self.token_counts.most_common(10),
        }


def build_tokenizer_from_sequences_file(seq_path, output_path=None,
                                         max_len=DEFAULT_MAX_LEN,
                                         min_freq=DEFAULT_MIN_FREQ):
    with open(seq_path, "r") as f:
        sequences = json.load(f)

    tokenizer = APITokenizer(max_len=max_len, min_freq=min_freq)
    tokenizer.build_vocab(sequences.values())

    if output_path:
        tokenizer.save(output_path)
        print(f"Saved tokenizer to {output_path}")

    return tokenizer


if __name__ == "__main__":
    import sys

    seq_path = sys.argv[1] if len(sys.argv) > 1 else "data/processed/api_sequences_clean.json"
    out_path = sys.argv[2] if len(sys.argv) > 2 else "models/api_tokenizer.json"

    if not os.path.exists(seq_path):
        print(f"Sequences file not found: {seq_path}")
        print("Run build_dynamic_matrix.py and clean_dynamic_data.py first.")
        print("\nDemo mode: building tokenizer from test fixtures...\n")

        fixtures = os.path.join(os.path.dirname(__file__), "..", "tests", "fixtures")
        from dynamic_sandbox.api_sequence import extract_flat_sequence

        demo_seqs = {}
        for fname in ["cape_report_benign.json", "cape_report_suspicious.json"]:
            fpath = os.path.join(fixtures, fname)
            if os.path.exists(fpath):
                with open(fpath) as f:
                    report = json.load(f)
                demo_seqs[fname] = extract_flat_sequence(report)

        tok = APITokenizer(max_len=DEFAULT_MAX_LEN, min_freq=1)
        tok.build_vocab(demo_seqs.values())
    else:
        tok = build_tokenizer_from_sequences_file(seq_path, out_path)

    info = tok.summary()
    print(f"Vocabulary size: {info['vocab_size']}")
    print(f"Max sequence length: {info['max_len']}")
    print(f"Unique APIs seen: {info['total_unique_apis']}")
    print(f"\nTop 10 APIs:")
    for api, count in info["top_10"]:
        print(f"  {api}: {count}")
