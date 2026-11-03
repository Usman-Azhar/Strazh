import sys
import os
import glob
import json
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from submit_sample import submit_file, wait_for_report, fetch_report

SAMPLES_DIR = "data/raw"
OUTPUT_DIR = "data/raw/cape_reports"


def batch_submit(samples_dir, output_dir, poll_interval=15, timeout=600):
    """Submit all EXEs in samples_dir through CAPEv2, save each report."""
    os.makedirs(output_dir, exist_ok=True)
    samples = glob.glob(os.path.join(samples_dir, "*.exe"))

    if not samples:
        print(f"No .exe files found in {samples_dir}")
        return

    print(f"Found {len(samples)} samples to submit.\n")

    results = []
    for i, sample_path in enumerate(samples, 1):
        name = os.path.basename(sample_path)
        print(f"[{i}/{len(samples)}] Submitting {name}...")

        try:
            task_id = submit_file(sample_path)
            if task_id is None:
                print(f"  FAILED: no task ID returned")
                results.append({"file": name, "status": "submit_failed"})
                continue

            print(f"  Task ID: {task_id}, waiting for report...")
            if wait_for_report(task_id, poll_interval, timeout):
                report = fetch_report(task_id)
                out_path = os.path.join(output_dir, f"report_{name}.json")
                with open(out_path, "w") as f:
                    json.dump(report, f, indent=2)
                print(f"  Saved: {out_path}")
                results.append({"file": name, "status": "ok", "task_id": task_id})
            else:
                print(f"  TIMEOUT after {timeout}s")
                results.append({"file": name, "status": "timeout", "task_id": task_id})

        except Exception as e:
            print(f"  ERROR: {e}")
            results.append({"file": name, "status": "error", "error": str(e)})

    print(f"\n--- Batch Summary ---")
    for r in results:
        print(f"  {r['file']}: {r['status']}")

    ok_count = sum(1 for r in results if r["status"] == "ok")
    print(f"\n{ok_count}/{len(results)} reports collected successfully.")


if __name__ == "__main__":
    samples = sys.argv[1] if len(sys.argv) > 1 else SAMPLES_DIR
    batch_submit(samples, OUTPUT_DIR)
