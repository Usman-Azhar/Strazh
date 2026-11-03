import json


def load_report(path):
    with open(path, "r") as f:
        return json.load(f)


def extract_file_operations(report):
    """
    Extract file write operations from API call logs.
    Returns a dict with counts and the list of written paths.
    """
    write_apis = {"NtWriteFile", "NtCreateFile", "MoveFileWithProgressW",
                  "CopyFileExW", "DeleteFileW"}

    writes = []
    creates = []
    for proc in report.get("behavior", {}).get("processes", []):
        for call in proc.get("calls", []):
            if call.get("category") != "file":
                continue
            api = call["api"]
            filepath = call.get("arguments", {}).get("filepath", "")
            if api == "NtWriteFile":
                writes.append(filepath)
            elif api == "NtCreateFile":
                creates.append(filepath)

    dropped = report.get("dropped", [])

    return {
        "file_creates": len(creates),
        "file_writes": len(writes),
        "dropped_count": len(dropped),
        "dropped_pe_count": sum(
            1 for d in dropped if "PE32" in d.get("type", "")
        ),
        "created_paths": creates,
        "written_paths": writes,
        "dropped_files": [d.get("name", "") for d in dropped],
    }


def extract_registry_operations(report):
    """
    Extract registry write operations from API call logs.
    Distinguishes reads from writes for feature extraction.
    """
    read_apis = {"RegOpenKeyExW", "RegQueryValueExW", "NtOpenKey"}
    write_apis = {"RegSetValueExW", "RegCreateKeyExW", "NtSetValueKey",
                  "RegDeleteValueW", "RegDeleteKeyW"}

    reads = []
    writes = []
    persistence_keys = []

    persistence_indicators = [
        "\\CurrentVersion\\Run",
        "\\CurrentVersion\\RunOnce",
        "\\Services\\",
        "\\CurrentVersion\\Explorer\\Shell Folders",
    ]

    for proc in report.get("behavior", {}).get("processes", []):
        for call in proc.get("calls", []):
            if call.get("category") != "registry":
                continue
            api = call["api"]
            regkey = call.get("arguments", {}).get("regkey", "")

            if api in read_apis:
                reads.append(regkey)
            elif api in write_apis:
                writes.append(regkey)
                if any(ind in regkey for ind in persistence_indicators):
                    persistence_keys.append(regkey)

    return {
        "registry_reads": len(reads),
        "registry_writes": len(writes),
        "persistence_writes": len(persistence_keys),
        "written_keys": writes,
        "persistence_keys": persistence_keys,
    }


def _tree_metrics(node):
    """Recursively compute depth and breadth of a process tree node."""
    children = node.get("children", [])
    if not children:
        return 1, 1  # depth=1 (just this node), total_nodes=1

    child_depths = []
    total = 1  # count this node
    for child in children:
        d, n = _tree_metrics(child)
        child_depths.append(d)
        total += n

    return max(child_depths) + 1, total


def extract_process_tree(report):
    """
    Compute depth, breadth, and total node count from the process tree.
    These metrics distinguish benign (flat, 1-2 processes) from malicious
    (deep chains: sample -> cmd -> powershell -> payload).
    """
    trees = report.get("behavior", {}).get("processtree", [])

    if not trees:
        return {
            "tree_depth": 0,
            "tree_breadth": 0,
            "total_processes": 0,
            "process_names": [],
        }

    max_depth = 0
    max_breadth = 0
    total_processes = 0
    process_names = []

    def _collect_names(node):
        names = [node.get("name", "")]
        for child in node.get("children", []):
            names.extend(_collect_names(child))
        return names

    def _max_breadth(node):
        children = node.get("children", [])
        best = len(children)
        for child in children:
            best = max(best, _max_breadth(child))
        return best

    for root in trees:
        depth, count = _tree_metrics(root)
        breadth = _max_breadth(root)
        max_depth = max(max_depth, depth)
        max_breadth = max(max_breadth, breadth)
        total_processes += count
        process_names.extend(_collect_names(root))

    return {
        "tree_depth": max_depth,
        "tree_breadth": max_breadth,
        "total_processes": total_processes,
        "process_names": process_names,
    }


def extract_all_behavior_features(report):
    """
    Combine all behavioral feature groups into a single dict.
    This is the dynamic counterpart to Track 2's static feature vector.
    """
    file_ops = extract_file_operations(report)
    reg_ops = extract_registry_operations(report)
    proc_tree = extract_process_tree(report)

    return {
        "file_creates": file_ops["file_creates"],
        "file_writes": file_ops["file_writes"],
        "dropped_count": file_ops["dropped_count"],
        "dropped_pe_count": file_ops["dropped_pe_count"],
        "registry_reads": reg_ops["registry_reads"],
        "registry_writes": reg_ops["registry_writes"],
        "persistence_writes": reg_ops["persistence_writes"],
        "tree_depth": proc_tree["tree_depth"],
        "tree_breadth": proc_tree["tree_breadth"],
        "total_processes": proc_tree["total_processes"],
    }


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m dynamic_sandbox.behavior_draft <report.json>")
        sys.exit(1)

    report = load_report(sys.argv[1])

    print("=== File Operations ===")
    file_ops = extract_file_operations(report)
    print(f"  Creates: {file_ops['file_creates']}")
    print(f"  Writes:  {file_ops['file_writes']}")
    print(f"  Dropped: {file_ops['dropped_count']} ({file_ops['dropped_pe_count']} PEs)")
    for p in file_ops["written_paths"]:
        print(f"    -> {p}")

    print("\n=== Registry Operations ===")
    reg_ops = extract_registry_operations(report)
    print(f"  Reads:  {reg_ops['registry_reads']}")
    print(f"  Writes: {reg_ops['registry_writes']}")
    print(f"  Persistence writes: {reg_ops['persistence_writes']}")
    for k in reg_ops["persistence_keys"]:
        print(f"    -> {k}")

    print("\n=== Process Tree ===")
    tree = extract_process_tree(report)
    print(f"  Depth:     {tree['tree_depth']}")
    print(f"  Breadth:   {tree['tree_breadth']}")
    print(f"  Processes: {tree['total_processes']}")
    print(f"  Names:     {tree['process_names']}")

    print("\n=== Combined Feature Vector ===")
    features = extract_all_behavior_features(report)
    for k, v in features.items():
        print(f"  {k}: {v}")
