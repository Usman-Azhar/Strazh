import os
import pytest
from dynamic_sandbox.behavior_draft import (
    load_report,
    extract_file_operations,
    extract_registry_operations,
    extract_process_tree,
    extract_all_behavior_features,
)

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")
BENIGN = os.path.join(FIXTURES, "cape_report_benign.json")
SUSPICIOUS = os.path.join(FIXTURES, "cape_report_suspicious.json")


class TestFileOperations:
    def test_benign_minimal_writes(self):
        report = load_report(BENIGN)
        ops = extract_file_operations(report)
        assert ops["file_writes"] == 0
        assert ops["file_creates"] == 1
        assert ops["dropped_count"] == 0
        assert ops["dropped_pe_count"] == 0

    def test_suspicious_has_writes_and_drops(self):
        report = load_report(SUSPICIOUS)
        ops = extract_file_operations(report)
        assert ops["file_writes"] == 2
        assert ops["file_creates"] == 2
        assert ops["dropped_count"] == 2
        assert ops["dropped_pe_count"] == 1

    def test_suspicious_written_paths(self):
        report = load_report(SUSPICIOUS)
        ops = extract_file_operations(report)
        assert any("svchost_helper.dll" in p for p in ops["written_paths"])
        assert any("payload_stage2.bin" in p for p in ops["written_paths"])

    def test_empty_report(self):
        report = {"behavior": {"processes": []}, "dropped": []}
        ops = extract_file_operations(report)
        assert ops["file_writes"] == 0
        assert ops["dropped_count"] == 0


class TestRegistryOperations:
    def test_benign_reads_only(self):
        report = load_report(BENIGN)
        ops = extract_registry_operations(report)
        assert ops["registry_reads"] == 3
        assert ops["registry_writes"] == 0
        assert ops["persistence_writes"] == 0

    def test_suspicious_has_persistence(self):
        report = load_report(SUSPICIOUS)
        ops = extract_registry_operations(report)
        assert ops["registry_writes"] == 2
        assert ops["persistence_writes"] == 2

    def test_suspicious_persistence_keys(self):
        report = load_report(SUSPICIOUS)
        ops = extract_registry_operations(report)
        keys = ops["persistence_keys"]
        assert any("CurrentVersion\\Run" in k for k in keys)
        assert any("Services\\" in k for k in keys)

    def test_empty_report(self):
        report = {"behavior": {"processes": []}}
        ops = extract_registry_operations(report)
        assert ops["registry_reads"] == 0
        assert ops["registry_writes"] == 0


class TestProcessTree:
    def test_benign_flat_tree(self):
        report = load_report(BENIGN)
        tree = extract_process_tree(report)
        assert tree["tree_depth"] == 1
        assert tree["tree_breadth"] == 0
        assert tree["total_processes"] == 1
        assert tree["process_names"] == ["notepad.exe"]

    def test_suspicious_deep_tree(self):
        report = load_report(SUSPICIOUS)
        tree = extract_process_tree(report)
        assert tree["tree_depth"] == 3
        assert tree["tree_breadth"] == 2
        assert tree["total_processes"] == 5
        assert "suspicious_sample.exe" in tree["process_names"]
        assert "cmd.exe" in tree["process_names"]
        assert "powershell.exe" in tree["process_names"]
        assert "whoami.exe" in tree["process_names"]

    def test_empty_tree(self):
        report = {"behavior": {"processtree": []}}
        tree = extract_process_tree(report)
        assert tree["tree_depth"] == 0
        assert tree["total_processes"] == 0

    def test_missing_processtree(self):
        report = {"behavior": {}}
        tree = extract_process_tree(report)
        assert tree["tree_depth"] == 0


class TestCombinedFeatures:
    def test_benign_feature_vector(self):
        report = load_report(BENIGN)
        features = extract_all_behavior_features(report)
        assert features["file_writes"] == 0
        assert features["registry_writes"] == 0
        assert features["persistence_writes"] == 0
        assert features["tree_depth"] == 1
        assert features["total_processes"] == 1

    def test_suspicious_feature_vector(self):
        report = load_report(SUSPICIOUS)
        features = extract_all_behavior_features(report)
        assert features["file_writes"] > 0
        assert features["registry_writes"] > 0
        assert features["persistence_writes"] > 0
        assert features["tree_depth"] > 1
        assert features["total_processes"] > 1
        assert features["dropped_pe_count"] > 0

    def test_all_keys_present(self):
        report = load_report(BENIGN)
        features = extract_all_behavior_features(report)
        expected_keys = {
            "file_creates", "file_writes", "dropped_count", "dropped_pe_count",
            "registry_reads", "registry_writes", "persistence_writes",
            "tree_depth", "tree_breadth", "total_processes",
        }
        assert set(features.keys()) == expected_keys

    def test_all_values_numeric(self):
        report = load_report(SUSPICIOUS)
        features = extract_all_behavior_features(report)
        for key, val in features.items():
            assert isinstance(val, (int, float)), f"{key} is {type(val)}, not numeric"

    def test_benign_vs_suspicious_separation(self):
        """Benign and suspicious reports should produce clearly different vectors."""
        benign = extract_all_behavior_features(load_report(BENIGN))
        suspicious = extract_all_behavior_features(load_report(SUSPICIOUS))

        assert suspicious["file_writes"] > benign["file_writes"]
        assert suspicious["registry_writes"] > benign["registry_writes"]
        assert suspicious["persistence_writes"] > benign["persistence_writes"]
        assert suspicious["tree_depth"] > benign["tree_depth"]
        assert suspicious["total_processes"] > benign["total_processes"]
