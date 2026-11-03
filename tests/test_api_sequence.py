import os
import json
import pytest
from dynamic_sandbox.api_sequence import (
    load_report,
    extract_api_sequences,
    extract_flat_sequence,
    api_ngrams,
    api_ngram_counts,
    api_category_counts,
)

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")
BENIGN = os.path.join(FIXTURES, "cape_report_benign.json")
SUSPICIOUS = os.path.join(FIXTURES, "cape_report_suspicious.json")


def test_load_report():
    report = load_report(BENIGN)
    assert "behavior" in report
    assert "info" in report


class TestExtractApiSequences:
    def test_benign_single_process(self):
        report = load_report(BENIGN)
        seqs = extract_api_sequences(report)
        assert len(seqs) == 1
        pid, name = list(seqs.keys())[0]
        assert name == "notepad.exe"
        assert len(seqs[(pid, name)]) == 10

    def test_suspicious_multiple_processes(self):
        report = load_report(SUSPICIOUS)
        seqs = extract_api_sequences(report)
        assert len(seqs) == 5
        pids = {pid for pid, _ in seqs}
        assert 3100 in pids
        assert 3200 in pids

    def test_order_preserved(self):
        report = load_report(BENIGN)
        seqs = extract_api_sequences(report)
        apis = list(seqs.values())[0]
        assert apis[0] == "LdrLoadDll"
        assert apis[-1] == "ShowWindow"

    def test_empty_behavior(self):
        report = {"behavior": {"processes": []}}
        seqs = extract_api_sequences(report)
        assert seqs == {}

    def test_missing_behavior(self):
        report = {}
        seqs = extract_api_sequences(report)
        assert seqs == {}


class TestExtractFlatSequence:
    def test_benign_flat(self):
        report = load_report(BENIGN)
        flat = extract_flat_sequence(report)
        assert len(flat) == 10
        assert flat[0] == "LdrLoadDll"

    def test_suspicious_merges_all_processes(self):
        report = load_report(SUSPICIOUS)
        flat = extract_flat_sequence(report)
        per_proc = extract_api_sequences(report)
        total_per_proc = sum(len(v) for v in per_proc.values())
        assert len(flat) == total_per_proc

    def test_sorted_by_timestamp(self):
        report = load_report(SUSPICIOUS)
        flat_calls = []
        for proc in report["behavior"]["processes"]:
            for call in proc["calls"]:
                flat_calls.append(call["timestamp"])
        flat_calls.sort()
        flat = extract_flat_sequence(report)
        assert len(flat) == len(flat_calls)


class TestApiNgrams:
    def test_bigrams(self):
        apis = ["NtCreateFile", "NtWriteFile", "RegSetValueExW"]
        bigrams = api_ngrams(apis, 2)
        assert bigrams == ["NtCreateFile_NtWriteFile", "NtWriteFile_RegSetValueExW"]

    def test_trigrams(self):
        apis = ["A", "B", "C", "D"]
        trigrams = api_ngrams(apis, 3)
        assert trigrams == ["A_B_C", "B_C_D"]

    def test_single_element(self):
        assert api_ngrams(["A"], 2) == []

    def test_empty(self):
        assert api_ngrams([], 1) == []


class TestApiNgramCounts:
    def test_counts_multiple_n(self):
        apis = ["A", "B", "A", "B"]
        counts = api_ngram_counts(apis, ns=(1, 2))
        assert counts["A"] == 2
        assert counts["B"] == 2
        assert counts["A_B"] == 2
        assert counts["B_A"] == 1


class TestApiCategoryCounts:
    def test_benign_categories(self):
        report = load_report(BENIGN)
        cats = api_category_counts(report)
        assert cats["system"] == 3
        assert cats["registry"] == 3
        assert cats["file"] == 2
        assert cats["ui"] == 2

    def test_suspicious_has_process_and_network(self):
        report = load_report(SUSPICIOUS)
        cats = api_category_counts(report)
        assert cats["process"] > 0
        assert cats["network"] > 0
