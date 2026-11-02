#!/usr/bin/env bash
# scripts/revert_snapshot.sh
# Reverts the VM to the clean baseline snapshot and (optionally) boots it.

set -euo pipefail

VM_NAME="Strazh-Win10"
SNAPSHOT_NAME="clean-baseline"

echo "Powering off VM if running..."
VBoxManage controlvm "$VM_NAME" poweroff || true   # ok if it's already off

echo "Reverting to snapshot: $SNAPSHOT_NAME"
VBoxManage snapshot "$VM_NAME" restore "$SNAPSHOT_NAME"

if [[ "${1:-}" == "--start" ]]; then
    echo "Starting VM headless..."
    VBoxManage startvm "$VM_NAME" --type headless
fi

echo "Done."