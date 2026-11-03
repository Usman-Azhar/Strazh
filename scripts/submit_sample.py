import sys
import json
import urllib.request
import urllib.parse
import time

CAPE_API = "http://localhost:8090/apiv2"

def submit_file(file_path):
    """Submit a PE file to CAPEv2 for analysis via the REST API."""
    with open(file_path, "rb") as f:
        file_data = f.read()

    boundary = "----StrazhBoundary"
    filename = file_path.rsplit("/", 1)[-1].rsplit("\\", 1)[-1]

    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
        f"Content-Type: application/octet-stream\r\n\r\n"
    ).encode() + file_data + f"\r\n--{boundary}--\r\n".encode()

    req = urllib.request.Request(
        f"{CAPE_API}/tasks/create/file/",
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )
    resp = urllib.request.urlopen(req)
    result = json.loads(resp.read())
    return result.get("data", {}).get("task_ids", [None])[0]


def wait_for_report(task_id, poll_interval=15, timeout=600):
    """Poll until the task reaches 'reported' status or timeout."""
    elapsed = 0
    while elapsed < timeout:
        req = urllib.request.Request(f"{CAPE_API}/tasks/view/{task_id}/")
        resp = urllib.request.urlopen(req)
        result = json.loads(resp.read())
        status = result.get("data", {}).get("status", "")
        print(f"  Task {task_id}: {status} ({elapsed}s elapsed)")
        if status == "reported":
            return True
        time.sleep(poll_interval)
        elapsed += poll_interval
    return False


def fetch_report(task_id):
    """Download the full JSON report for a completed task."""
    req = urllib.request.Request(f"{CAPE_API}/tasks/report/{task_id}/")
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read())


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python submit_sample.py <path_to_pe_file>")
        sys.exit(1)

    path = sys.argv[1]
    print(f"Submitting {path}...")
    task_id = submit_file(path)
    if task_id is None:
        print("Submission failed.")
        sys.exit(1)
    print(f"Task ID: {task_id}")

    print("Waiting for analysis...")
    if wait_for_report(task_id):
        report = fetch_report(task_id)
        out_path = f"data/raw/cape_reports/report_{task_id}.json"
        with open(out_path, "w") as f:
            json.dump(report, f, indent=2)
        print(f"Report saved to {out_path}")
    else:
        print("Timed out waiting for report.")
        sys.exit(1)
