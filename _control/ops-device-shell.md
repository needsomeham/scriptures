---
title: Ops — Cowork device shell (device_bash) outage
type: control
tags: [ops, windows, cowork]
created: 2026-09-14
sources: []
---
# Cowork device shell outage — what it is, what you can do

## Symptom
Any `device_bash` call fails with
`sandbox-helper: no Plan9 drive shares mounted under /mnt/.virtiofs-root/shared`.
Connected folders still work through the file bridge (list / stage / commit), so vault waves still run — agents just build in the cloud workspace and commit files back, as wave 1 did.

## Root cause (confirmed, not yours)
Microsoft's 2026-09-08 cumulative update broke the Plan9/virtiofs share attach that Cowork's Linux sandbox uses to mount your folders. The host reports success; the guest mounts 0 shares.
- Windows 11 24H2/25H2 x64: **KB5124008** (build 26200.9445 / 26100.9445)
- Windows 11 ARM64: KB5124012 (28000.2954) · Windows 10 22H2: KB5122878 (19045.7725)
- Anthropic status page, 2026-09-10: "Degraded functionality for Claude Cowork on Windows … Microsoft has developed a fix and is working on releasing it." No date.
- Claude Desktop v1.52386.0 (2026-09-10) only improved the error message; the changelog says the underlying problem is not fixed.

## Step 0 — confirm you're on the bad build (2 min)
```powershell
winver                                   # look for 26200.9445 / 26100.9445
Get-HotFix -Id KB5124008                 # present = you have the bad KB
```

## Option A — wait (recommended default)
Nothing to do. Check https://status.claude.com and Windows Update for the Microsoft fix. Meanwhile the vault workflow is unaffected in practice: the architect briefs agents to build in the cloud workspace and commit with the file bridge (≤50 files/call). Cost: slightly more tokens per wave, no functional loss.

## Option B — uninstall the KB (works on most machines; not risk-free)
One reporter hit a boot failure (0xc0000428, signature error) after removal and had to recover with `dism /image:C:\ /cleanup-image /revertpendingactions` + `bcdboot`. Others hit DISM errors 0x800f0825 / 0x800f0926 / 0x800f0905 ("permanent package") and could not uninstall at all. So:

1. **Make a restore point and confirm you have a recovery USB / BitLocker key.**
2. Pause updates so it doesn't reinstall: Settings → Windows Update → Pause updates (max 5 weeks).
3. Try the simple path first (elevated PowerShell):
   ```powershell
   wusa /uninstall /kb:5124008 /norestart
   ```
   If wusa says the update can't be removed, use DISM (package name from your machine, not copied blindly):
   ```powershell
   dism /online /get-packages | findstr /i RollupFix     # find the 26x00.9445 rollup name
   dism /online /remove-package /packagename:<that name>
   ```
4. Reboot. Re-run Step 0 — `Get-HotFix` should no longer list the KB.
5. In Cowork, start a fresh session with the Scriptures folder connected and run any `device_bash` command (e.g. `ls "$HOME/mnt/Scriptures"`). Mounts should return.
6. When Microsoft ships the fix, un-pause updates.

## Not confirmed to help
Restarting/reinstalling Claude Desktop, resetting the workspace, WSL/Hyper-V toggles, disabling Windows Sandbox (`Containers-DisposableClientVM`) on its own, registry edits. Don't spend time on these.

## Sources
- github.com/anthropics/claude-code/issues/92958 (cross-arch confirmation, rollback A/B on 5 machines)
- github.com/anthropics/claude-code/issues/92984 (KB5124008; uninstall fixes; boot-failure report)
- github.com/anthropics/claude-code/issues/93071 (Windows 10 variant)
- claude.com/docs/cowork/changelog (v1.52386.0 entry, 2026-09-10)
