# Python-version and full Linux-suite verification

## Current result

The unmodified `tests/run.sh` completes successfully on local Ubuntu 24.04.5
WSL2 with Python 3.12.3: 929 tests run in 311.801 seconds, with no failures or
errors and one existing Windows-only skip. The preceding expansion-development
and parser-association selection passes all 39 tests without skips. No test is
excluded from the full discovery, and no additional mocks or skips are introduced
for this execution.

Python 3.10 execution remains blocked. It is absent from the bounded interpreter
locations checked in the usable distribution. The Windows launcher lists only
Python 3.13. The separate `Ubuntu` registration cannot attach its missing virtual
disk (`Wsl/Service/CreateInstance/MountVhd/HCS/ERROR_FILE_NOT_FOUND`); its Python
version is unknown. No interpreter, dependency, distribution or disk is installed,
repaired or reconstructed. Python 3.12 success does not establish Python 3.10
compatibility or hosted GitHub success.

This follow-up extends the execution boundary of the earlier
[expansion-response correction](parser-association-repairs.md#expansion-test-response-correction)
and [native/POSIX verification](native-posix-verification.md). Their earlier
restricted selections remain historical evidence.

## Baseline and environment

The starting and ending revision is
`21453cb2d1adb949ffb3bdaa08caedb6f7aa03dd`. The pre-existing expansion-test correction
and its two documentation changes are preserved. The Git index retains its
starting hash. This follow-up adds verification documentation and ignored local
evidence; no production or maintained test repair is necessary.

The tested environment uses Linux x86-64, the WSL2 5.15.153.1 kernel, glibc 2.39,
Bash 5.2.21, tmux 3.4, GCC 13.3.0 and `C.UTF-8`. Existing standard-library curses,
PTY and POSIX locking facilities are available. Disposable sources and test
files reside on Linux ext4, rather than the Windows-mounted 9p filesystem.
The original checkout is read through 9p only to prepare and compare the source
snapshot and to retain explicitly named reports.

All 505 Git-visible starting files, including preserved release artifacts, are
copied into a disposable snapshot and verified byte-for-byte before execution.
No Git metadata or unrelated ignored installation, collection or candidate output
is copied. The same source hashes remain intact after the suite. Real shell
startup files retain their starting hashes.

An unprivileged user/network namespace retains UID/GID 1000 and contains only
loopback with no external routes. It provides offline execution for the complete
process tree without replacing subprocesses, sockets, PTYs or filesystem behavior
with new test mocks. A private HOME, XDG paths, temporary directory, shell history
and input configuration isolate writes. The runner starts from a cleared
environment; inherited shell hooks, exported functions and user Python settings
are absent. The initial separately prepared `/tmp` snapshot was unavailable on
the next WSL invocation; no tests ran in that attempt. The successful preparation,
discovery and execution occur in one WSL session.

## Inspected execution boundary

Static enumeration covers 61 `test_*.py` modules and 929 declared methods. Actual
unittest discovery independently finds 929 tests. Discovery imports are first
checked with process, network and write entry points blocked; these guards are
removed before actual execution. The full runner performs its existing Bash
syntax checks, numerical coverage command, bundled/profile-driver validation and
unrestricted unittest discovery.

| Owners or test classes | Processes and destinations | Disposition |
| --- | --- | --- |
| Core, numerical, inventory, parser and argument tests | Passive transforms and existing controlled mocks; selected temporary/report directories | Safe passive checks |
| Discovery, module, driver, bulk-scan and manual-import fixtures | Generated scripts with inspected bodies and `sys.executable` shebangs; fixed requests and disposable fixture bins | Authorized synthetic processes; no installed target or real manual renderer |
| `BashIntegrationTests` and terminal/review suites | Owned Bash/PTY children, private tmux sockets, synthetic profiles and snapshot files | Authorized native shell/terminal checks; no personal shell startup or existing tmux server |
| Deliberate Enter case | Inspected fixture-defined `rsync()` writes only its disposable marker | Authorized oracle; actual pending user commands are never submitted |
| Guided/raw review and update-editor tests | Generated Python editor fixtures modify disposable drafts | Authorized synthetic editors; no installed editor |
| Installation, update and removal tests | Inspected repository wrappers, explicit disposable prefixes, private rc files, staged payload checks | Authorized lifecycle checks; real installations and startup files remain untouched |
| Release, candidate and packaged-terminal tests | GCC builds a temporary repository launcher; tar/checksum/native smoke checks and temporary candidate archives | Authorized disposable archive/build checks; no historical rebuild, package publication or persistent installation |
| Historical-upgrade cases | Byte-preserved v0.1.1-alpha installer copy, inspected wrapper/installation code and isolated test prefix | Authorized disposable upgrade path; original historical artifacts remain unchanged |
| Release-download and documentation-link tests | Existing in-memory clients and patched network/process calls | No actual downloads, external renderer or link-scanner execution |
| Live-harness tests | Existing synthetic/fake executable identities and mocked probes | No live compatibility scan or installed-program enumeration |
| Repository-policy tests | `git init`, `check-ignore` and `check-attr` in private fixture repositories | No real index, history, Git configuration, commit or remote operation |
| Native POSIX collection/save tests | Owned children, locks, signals, FIFO/symlink and permission fixtures on ext4 | Actual unprivileged kernel/filesystem checks; no real collection or unrelated process affected |

The Bash PTY harness uses its own rc file and private HOME. The remaining system
interactive startup file is inspected; the tmux harness suppresses it with
`--norc`. Harness control input is separate from buffers under test. Process
timeouts, private process groups and existing child cleanup bound execution.
Package self-extraction stages and cleanup remain inside disposable TMPDIRs.
The offline namespace covers descendants even where an existing test supplies a
different environment.

## Version-specific acceptance

| Criterion | Python 3.12 | Python 3.10 |
| --- | --- | --- |
| Actual requested interpreter | `/usr/bin/python3.12`, version 3.12.3 | Unavailable in checked locations |
| Expansion-development plus parser-association modules | 39 passed; no skips | Blocked |
| Unmodified `tests/run.sh` | Exit 0; 929 tests, 928 passed and one existing skip | Blocked |
| Child interpreter selection | Inspected argv/shebang/PATH/adapter relationships resolve to 3.12.3 | Not established |
| Native PTY/tmux and ext4 lifecycle tests | Included in full discovery and executed | Not established |

The sole skip is
`test_functional_matrix.EdgeCaseTests.test_probe_reports_the_windows_limitation`:
its decorator applies only on Windows because POSIX completes the probe normally.
It does not hide a Linux acceptance requirement. No terminal, permission,
historical-upgrade or candidate test is skipped in this run.

Private `python`, `python3` and `python3.12` PATH entries resolve to the same
canonical interpreter. Python child fixtures use `sys.executable` or an explicit
`CLI_HELP_PYTHON`; fixtures with generated shebangs use that interpreter as well.
The tmux harness's fixed `/usr/bin:/bin` PATH also resolves `python3` to 3.12.3.
This establishes selection through inspected launch paths and resolved executable
identities, rather than an exhaustive syscall trace of every child process.

## Numerical and protected-state checks

Initial reconciliation and prospective/strict coverage pass independently.
Both modes report 504 complete required contracts, zero debt and no individual
exceptions. Three heuristic warnings and fourteen external informational groups
remain distinct from maintained completeness. Final reconciliation and both
coverage modes also pass with unchanged counts; the reports record fresh outcomes
rather than inferred historical results.

The inventory retains 76 profiles, 96 categories and 942 profile option/keyword
records. The coverage view separates those into 914 option and 28 keyword records;
it also records three positional groups and 22 shared definitions. These totals
overlap and are not additive coverage claims. The wider inventory retains 6,149
entries and 358 input files. Production profiles, runtime modules, drivers,
captures, validators, coverage eligibility, review annotations and debt/exception
policy retain their starting hashes. No annotation refresh is required.

## Reproduction and evidence

After inspecting the current checkout and execution boundaries, the maintained
entry points on a suitable existing Linux environment are:

```bash
cd tests
python3 -B -m unittest -v test_expansion_development test_parser_association
cd ..
bash --noprofile --norc tests/run.sh
python3 -B scripts/inventory_numerical_descriptions.py --check --summary
python3 -B scripts/check_numerical_coverage.py --summary
python3 -B scripts/check_numerical_coverage.py --mode strict --summary
```

These commands require the same offline isolation and disposable HOME, TMPDIR,
prefixes and snapshot precautions described above. They are not instructions to
run an uninspected suite against real installations. The retained ignored local
orchestrator prepares the byte-checked snapshot, performs import preflight,
selects the interpreter and executes those focused/full paths. A later run must
select a fresh label to preserve existing evidence:

```bash
env -i PATH=/usr/bin:/bin LC_ALL=C.UTF-8 PYTHONDONTWRITEBYTECODE=1 \
  unshare --user --map-current-user --net /usr/bin/python3 -B \
  .cache/full-linux-verification/run_full.py --label full-linux-repeat
```

Preparation uses the preserved baseline hashes; changed source requires a fresh
reviewed baseline rather than silently reusing stale evidence. This is a local
verification artifact, not a new maintained test framework or CI configuration.

Fresh ignored evidence under `tests/reports/numerical-inventory/` includes:

- `full-linux-static-inventory.json` and `full-linux-preflight-312.json`: complete
  source/discovery census and actual skip identity.
- `full-linux-environment.json` and `full-linux-version-blockers.json`: interpreter,
  tool and unavailable-environment evidence.
- `full-linux-focused-312.log`, `full-linux-suite-312.log` and
  `full-linux-execution-312.json`: actual commands, outcomes, source/startup
  comparisons and environment details.
- `full-linux-baseline-{inventory,prospective,strict}.json`, final counterparts
  and `full-linux-verification.json`: independent numerical/protected-state checks.

Environment-specific paths and interpreter build strings belong to these local
reports; reproducible source references remain repository-relative.

## Remaining limits

The Python 3.12 full local Linux-suite gap is closed within this environment.
The combined Python 3.10/3.12 acceptance criterion remains incomplete until an
actual existing or separately authorized Python 3.10 Linux environment runs the
same full suite. No repair of the unavailable distribution is implied.

Local WSL results do not establish hosted CI, native bare-metal Linux, every
Bash/Readline release, human visual/font acceptance, Windows ACL behavior,
9p permission denial, installed-target compatibility, arbitrary package
installations, power-loss durability or factual completeness of external help.
No production defect, runtime change, weakened assertion, exception or new skip
is introduced. All changes remain local, unstaged and uncommitted; no hosted
workflow or online GitHub operation is performed.
