# Snapshot Workflow

## One-time: create the clean baseline snapshot
1. Boot the VM, confirm it's in the state you want as your permanent baseline
   (Windows installed, host-only networking configured, no extra software).
2. Power the VM OFF (not just paused) - baseline snapshots are cleaner powered off.
3. Take snapshot named "clean-baseline":
     VBoxManage snapshot "Strazh-Win10" take clean-baseline

## Per-sample cycle (repeat for every run)
1. Revert to clean-baseline.
2. Start the VM.
3. Run the sample / do the analysis.
4. Power off (or let CAPE/automation power off).
5. Revert to clean-baseline again - do NOT snapshot on top of a dirty state.

## Rule
Never take a new "baseline" snapshot after running a sample. All working
snapshots branch FROM clean-baseline, never replace it.