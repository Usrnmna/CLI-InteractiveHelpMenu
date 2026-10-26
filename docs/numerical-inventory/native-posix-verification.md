# Native terminal and POSIX verification

[Implementation inventory](README.md) · [Earlier integrated verification](step8-verification.md) ·
[Authoring rules](step6-authoring.md) · [Collection recovery](../collection-recovery.md)

The native follow-up establishes scoped Bash/Readline, curses and POSIX
filesystem evidence beyond the earlier fake-window and mocked-process checks.
The starting checkout is clean at
`f91dc452222965b9b07115311a5d73a899fd42af`. Baseline reconciliation and both
coverage modes pass with 504 complete required contracts, no maintained debt
and no individual exceptions. Historical reports remain separate evidence.

## Environment and execution boundary

| Environment | Observed scope |
| --- | --- |
| Existing Ubuntu 24.04 WSL2 distribution | Linux 5.15.153.1-microsoft-standard-WSL2, glibc 2.39, unprivileged UID 1000 |
| Interpreter and shell | Python 3.12.3, Bash 5.2.21(1)-release, `C.UTF-8` |
| Terminal | tmux 3.4, private server/socket and real controlling PTY, `tmux-256color` |
| Linux filesystem | ext4; explicitly selected disposable directories under `/tmp` |
| Windows-mounted filesystem | 9p/DrvFS; separate disposable directories under `.cache/native-posix-followup/posix-9p/` |

The ext4 run label identifies the native fixtures' selected temporary root.
Some existing passive regression suites retain their own bounded repository
cache directories on 9p. Filesystem-specific conclusions below come from the
explicit native collection fixtures, not from those passive snapshots.

The restricted Windows process initially received
`Wsl/EnumerateDistros/Service/E_ACCESSDENIED`. The same read-only lookup and the
authorized tests succeeded outside that sandbox boundary. No distribution,
dependency, service or operating-system feature was installed or reconfigured.
The separate Docker Desktop and other WSL environments were not used.

The existing `TmuxShell` harness now starts Bash with `--noprofile --norc`, a
minimal environment, disabled discovery and history, and a disposable home.
Only the inspected test bootstrap is sourced. This also suppresses the system
interactive startup file. A new optional test-only profile directory supplies
inert synthetic metadata; it is not a production configuration extension.

Only harness-control lines are submitted to Bash. Pending lines are typed,
inspected through a Readline callback, then cleared or discarded without
accepting them. Marker files detect unintended execution of substitutions,
operators or the synthetic command function. Browser acceptance selects an
option; it never submits the edited command line. Private servers are stopped
without accepting remaining input.

The guarded runner permits private tmux operations and the inspected collection
inspection/recovery CLI cases. POSIX child processes execute closed test
operations through `fork`; they do not invoke targets. Network, discovery
probes, arbitrary subprocesses and shell-execution helpers are blocked. Real
editors, documentation renderers, target help/version probes and package tests
are excluded. All test-created temporary trees belong to the selected run.

## Verification matrix

`passed` applies only to the named observed boundary. Native terminal results
refer to tmux-rendered cells and PTY behavior, rather than human visual acceptance.

| Criterion | Owner and selected evidence | Result and observable guarantee |
| --- | --- | --- |
| N-01 / AC-02 | Bash adapter; new native terminal tests and existing screen tests | Passed on the Ubuntu PTY: opening, navigation, cancellation, reopening, literal buffers and cursor positions survive |
| N-02 / AC-08 | Formatter → presentation → actual curses list/details/search | Passed: seconds, literal `ms`, unlimited meaning and placeholders are searchable; complete long details remain reachable by scrolling |
| N-03 / AC-08 | Existing syntax/screen tests and native numerical resize test | Passed: 60×16 minimum, 40×10 fallback, shrink/grow, long labels, wide/combining text, clipping indicators and retained scrollback |
| N-04 / AC-01 | Actual Readline insertion through the adapter | Passed: separate, equals, attached-only and optional operands preserve surrounding quoted text and the character cursor |
| N-05 / AC-03 | Non-execution markers and reason-coded syntax rejection | Passed: substitutions, pipelines, redirection and compound operators remain unevaluated; command boundaries reject unsupported edits |
| N-06 / AC-02 | Actual termios reads and externally delivered SIGINT | Passed: cancellation and SIGINT restore terminal attributes and allow reopening with the original buffer; only the identified UI child is signaled |
| N-07 / AC-02 | Shell-option and binding snapshots | Passed: widget use preserves unrelated settings; unbind removes its private dispatch keys while preserving an unrelated custom binding |
| N-08 / AC-09 | Native review CLI → real read-only preview → exit | Passed: numerical guidance renders; Enter inspects rather than inserts; saved files remain byte-identical and review locks are released |
| N-09 / AC-09 | Actual competing writer processes | Passed on ext4 and 9p: existing writer locks block contenders; normal exit releases the owned locks |
| N-10 / AC-09 | Actual atomic replacement and open-file descriptors | Passed on ext4 and 9p: staged bytes remain invisible before replacement; old descriptors retain old complete bytes and new opens read complete replacement bytes |
| N-11 / AC-09 | Kernel permission-denied save, unprivileged process | Passed on ext4: valid saved bytes survive and backup/draft remain recoverable. Blocked on the tested 9p mount: `chmod` does not enforce write denial |
| N-12 / AC-09 | Actual concurrent modification and draft cancellation | Passed on ext4 and 9p: changed saved files are not overwritten; cancelled drafts do not save or create review backups |
| N-13 / AC-09 | SIGINT/SIGKILL at inspected save checkpoints → real recovery | Passed on ext4 and 9p: backups survive partial saves; graceful interruption releases locks; abrupt termination retains locks and blocks recovery until explicit inspection |
| N-14 / AC-09 | Existing collection tests, now on native Linux | Passed on ext4: real symlink/FIFO handling, pinned-root/parent descriptors, byte-preserving restore and ownership checks, with controlled race interleavings |
| N-15 / AC-10 | Reconciliation, prospective/strict gates and existing mutation regressions | Passed: eligibility, strict requirements, empty debt and exception lists remain unchanged |

The exact test identities, failures, skips and environment facts belong to the
ignored `native-*-tests.json` reports. The final verification report joins those
results to this matrix and independent repository comparisons.

The final Ubuntu selection passes 251 tests across fourteen modules, with no
failures or skips: 21 real terminal cases, 23 native collection/process cases
and 207 affected passive regressions. The separate 9p selection runs six
process/filesystem cases: five pass and the permission witness is explicitly
blocked/skipped. A successful runner exit does not make that sixth case pass.

## POSIX failure and recovery findings

The process tests pause only at existing write boundaries. Lock creation,
file descriptors, replacement, permissions, signals and recovery all use the
actual kernel and filesystem. Checkpoints supply deterministic interleavings;
they do not replace these mechanisms with simulated success.

A SIGINT during a partial profile/driver save enters existing error handling,
retains its backup and releases cooperative locks. A SIGKILL cannot run cleanup:
its locks remain and the application correctly reports uncertain ownership.
The test releases only its own known-dead child's exact, unchanged locks in the
disposable fixture before exercising explicit recovery. This is not an
application stale-lock removal policy. Real collection locks are untouched.

Killing a writer before `os.replace` retains the original file and a diagnosable
staged temporary. Per-file atomicity does not provide a multi-file transaction,
automatic rollback, power-loss durability or cleanup after SIGKILL. Existing
backups and explicit fresh-snapshot recovery remain necessary.

The 9p permission witness creates a file successfully after `chmod` removes
write bits. That test is recorded as blocked/skipped, not passed. Other 9p
write, contention, interruption and recovery tests pass independently. These
results do not establish Windows ACL denial, native Windows collection recovery,
or equivalent behavior on arbitrary mounts.

## Test changes and repairs

| File | Purpose |
| --- | --- |
| `tests/test_terminal_screen.py` | Reuse the existing private terminal harness with hermetic startup and an optional synthetic profile directory |
| `tests/test_native_numerical_terminal.py` | Add actual terminal, numerical search/details, insertion, non-execution, signal restoration, bindings and read-only preview cases |
| `tests/test_native_posix.py` | Add real child-process contention, atomic visibility, permission denial, concurrent edits, interruptions and backup recovery |

No production defect is established by the completed checks, and no runtime
repair is required. Initial failures were confined to the new harness: an
unsupported optional-value spelling prevented loading the synthetic profile,
and cursor setup counted combining-character movement as separate keystrokes.
The fixture now validates before launch and uses the supported
`nonnegative_integer` declaration. Cursor setup navigates an ASCII span where
available, with independent Readline character-offset assertions. The
non-execution case also requires the specific shell-syntax diagnostic, avoiding
a false pass caused by unrelated configuration rejection. Existing assertions,
numerical policies and runtime behavior are unchanged.

Production modules, profiles, captures, drivers, argument declarations, Git/CI
configuration and historical release files retain their starting hashes.
The numerical inventory and `review.json` are unchanged; no fingerprint,
classification, factual status, debt row or exception is refreshed.

## Reproduction and evidence

On an existing suitable Linux/WSL environment, from the repository root:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests -p test_native_numerical_terminal.py -v
PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests -p test_native_posix.py -v
python3 -B scripts/inventory_numerical_descriptions.py --check --summary
python3 -B scripts/check_numerical_coverage.py --summary
python3 -B scripts/check_numerical_coverage.py --mode strict --summary
git diff --check
```

Select an existing writable disposable `TMPDIR` to repeat filesystem-specific
checks. Native terminal tests require the already available Bash, curses and
tmux dependencies; they do not install them. Do not run the general suite under
these restrictions without inspecting its target, editor and package fixtures.

The retained local guarded runner is
`.cache/native-posix-followup/run_native.py`. The fresh ext4 selection uses
`--label final-ext4 --selection full`; the separate mounted-filesystem selection
uses `--label mounted-filesystem --selection posix --filesystem 9p`.
These labels identify the recorded earlier runs. Later selections require fresh
labels to preserve those historical reports.
The later [expansion-test response correction](parser-association-repairs.md#expansion-test-response-correction)
adds the complete expansion module to that guarded selection. The 251-test result
above remains the earlier native snapshot. The new `--selection expansion`
entry point selects the complete expansion and parser-association modules;
current follow-up reports remain distinct from these historical native results.
Evidence under `tests/reports/numerical-inventory/` includes:

- `native-baseline-{inventory,prospective,strict}.json` and final counterparts.
- `native-initial-tests.json` and `native-terminal-refined-tests.json`, retaining
  the early harness failures.
- `native-final-ext4-tests.json` and `native-mounted-filesystem-tests.json`,
  recording exact fresh selections and outcomes.
- `native-posix-verification.json`, recording matrix results, input hashes,
  coverage, encoding, links and unchanged index/revision evidence.

## Remaining limits

The subsequent [full Linux-suite verification](full-linux-verification.md)
records an unmodified 929-test Python 3.12 run, including inspected disposable
process, lifecycle and archive fixtures. It extends this account's earlier
restricted selection without establishing Python 3.10, real installed-target,
9p permission-denial or hosted-CI results.

The native PTY/Readline and ext4 acceptance gaps are closed within this matrix.
The 9p permission-denial case remains unestablished. Human visual/font acceptance,
physical Windows-terminal behavior, arbitrary POSIX implementations, GUI terminal
emulators, SIGTERM/SIGKILL UI restoration, hardware, installed targets,
package lifecycle, power loss and hosted CI are not established. No broader
platform or architecture change follows from these results.

All follow-up changes remain local, unstaged and uncommitted. No commit, push,
publication, hosted workflow, online GitHub change or global configuration change
is part of this verification.
