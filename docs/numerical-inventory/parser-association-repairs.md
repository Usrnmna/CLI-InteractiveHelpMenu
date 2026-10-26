# Operand parsing and manual association repairs

[Implementation inventory](README.md) · [Diagnostic investigation](diagnostic-investigation.md) ·
[Preservation rules](step4-preservation.md) · [Driver reference](../profiles-and-drivers.md)

The focused follow-up repairs compound operand recovery, nested interactive
documentation and explicit alias-pair extraction. The included stash-show route
now declares the bounded common-option portion of its borrowed manual.
Numerical validation, completeness policy and production metadata are unchanged.

The subsequent [native/POSIX verification](native-posix-verification.md) adds
scoped Ubuntu terminal, Readline and filesystem evidence. The results and
platform exclusions below remain those of the passive parser-repair snapshot.

The starting revision is `06b1347de65b89f1565c3acaad3f646e69694b41`, with the
earlier debt-resolution and diagnostic-investigation changes already present
locally. Those changes remain preserved. The revision and index remain unchanged;
all follow-up work is local, unstaged and uncommitted.

## Reproductions and corrected behavior

| Source | Starting passive result | Corrected passive result |
| --- | --- | --- |
| Podman 4.9.3 run capture, line 88 | `--memory` and `-m` lose `<number>[<unit>]` and appear valueless | Both retain the complete placeholder as one required operand; only the suffix fragment is optional |
| Same capture, line 89 | `--memory-reservation` loses the same compound placeholder | One required operand is retained |
| SFTP manual capture, interactive-command section at line 194 | Interactive `ls` flags enter the root option set; repeated spellings acquire unrelated observations | The complete section remains unassigned context. Root `-l limit`, `-R num_requests` and other genuine root declarations remain active |
| Git 2.43.0 diff manual under the stash-show capture key | Requested command and source manual are conflated; root-specific declarations are active under stash-show | The declared common-option scope retains diff formatting and stores source-specific declarations as inactive context |
| Same manual, line 902 | `-1 --base, -2 --ours, -3 --theirs` becomes one incomplete alias list | Three explicit short/long pairs remain distinct in the native manual view and source observations |

The immutable fixtures remain the reproduction inputs. No target help, manual
renderer, container, editor, pending command or operational workload runs.

The [Git 2.43 stash reference](https://raw.githubusercontent.com/git/git/v2.43.0/Documentation/git-stash.txt)
documents diff formatting for `show`; its
[implementation](https://raw.githubusercontent.com/git/git/v2.43.0/builtin/stash.c)
uses revision/diff setup before comparing the stored trees. This is distinct
from the working-tree/index conditions in the
[2.43 diff manual](https://raw.githubusercontent.com/git/git/v2.43.0/Documentation/git-diff.txt).
SFTP's capture has no exact release; the
[OpenSSH 9.6p1 manual](https://raw.githubusercontent.com/openssh/openssh-portable/V_9_6_P1/sftp.1)
confirms the interactive `ls` context for that reference release. No broader
installed-version or numerical-scale guarantee is introduced.

## Parsing rules and owning components

| Files | Purpose |
| --- | --- |
| `cli_help/discovery.py` | Balanced operands, declaration pairs, nested context, source association, profile construction and cache identity |
| `cli_help/drivers.py`, `config/drivers.example/git.json` | Optional validated manual scope on the existing stash-show route |
| `cli_help/diagnostics.py` | Scope-aware passive cache inspection |
| `cli_help/manual_import.py`, `cli_help/bulk_scan.py` | Scope preservation through existing passive transformations and saves |
| `scripts/inventory_numerical_descriptions.py`, `review.json` | Shared association census, precise source locations and exact reconciliation |
| `tests/test_parser_association.py`, `tests/test_numerical_diagnostics.py` | Real/synthetic regressions and replacement of limitation-only assertions with corrected ownership checks |

[discovery.py](../../cli_help/discovery.py) remains the owning parser and
profile-construction module. No second help parser or numerical interpretation
engine is added.

`placeholder_prefix` reads balanced angle/square fragments within one token.
Required `<amount>[<suffix>]` differs from optional `[<amount>[<suffix>]]`;
adjacent optional fragments remain optional. Separate explicit angle
placeholders can establish multiple required operands. Equals forms retain
their existing literal insertion spelling. Description-column brackets do not
become operands.

Top-level variadic ellipses and ambiguous nested free-form bracket grammars
remain conservative limitations. An ellipsis inside one list placeholder does
not imply multiple shell operands. Existing unsupported lowercase optional-prefix
grammars are not silently expanded. No unit, scale, suffix meaning or value
conversion is inferred from the recovered spelling.

`parse_option_groups` separates repeated short/long pairs while preserving the
compatible flat `parse_option_line` API. Shared explanations follow the explicit
pair that the source declares, rather than every adjacent selector.

`parse_help_document` retains explicit `INTERACTIVE COMMANDS` and `SUBCOMMANDS`
sections in the existing unassigned shared-documentation container. A later
top-level section resumes normal parsing. A plain `Commands` heading remains
eligible for root options: journalctl uses that heading for root actions.
Preserved nested text is not rebound to root options merely because it mentions
the same flag spelling.

The passive inventory uses the same command-aware association helper. It also
retains the actual line and alias group of each repeated declaration. Previously,
the first occurrence of a flag could incorrectly supply every later observation's
location and alias list. A synthetic repeated-declaration test independently
checks the two source locations.

## Explicit manual delegation

The additive driver field is `paths[].manual_scope: "common_options"`. It
requires a nonempty manual name; other values and explicit null are rejected.
Only the existing stash-show → git-diff example route receives the field.
Its command words, help arguments, manual name and insertion boundaries remain
unchanged. No command-specific option allowlist is introduced.

The field enables selection from explicit common/shared-option headings, or an
OPTIONS section ending with a reference to “these common options”. Wrapped
markers are supported. This source structure establishes a bounded document
region, not verified numerical facts or universal compatibility.

Requested command, manual lookup, returned manual title and actual request argv
remain separate provenance facts. Unavailable argv is not reconstructed from a
label. Original section names remain attached to source-only declarations.
Scoped-out text and qualifications remain accessible through the existing
details view as unassigned context; they do not become root search terms or
insertable options.

Routes without the new field retain their legacy whole-manual inference and
merge inventory, with explicit source-applicability qualifications when a manual
is borrowed. Header-only imports also preserve their existing behavior while
recording title uncertainty. This matters for stash-list/log delegation and for
intentional text imports under another executable name. Source titles alone
cannot establish a complete delegation policy.

A declared scope with no recognized shared region contributes source-only
documentation. Other valid sources remain usable. If no applicable options
remain, the existing failure path returns `help_source_scope`; no action probe
or invented option is substituted. Older custom drivers do not gain a scope
automatically; the field must be declared explicitly where that boundary is
desired.

## Propagation, merging and caching

Profile construction, passive manual import and controlled collection transforms
retain recovered placeholders, source context and the optional route field.
Replacement imports reapply an existing scope under the collection lock;
ordinary preflight validation still occurs before creating output directories.
No editor or guided-authoring redesign is introduced.

Existing first-source text precedence, coherent arity selection and atomic
numerical-metadata ownership remain unchanged. Explicit shared definitions and
inactive alternatives keep their existing rules. A recovered declaration does
not authorize transferring a scalar contract to an incompatible argument group.

Cache generation advances from 12 to 13 so older interpreted payloads are not
reused. A declared manual scope also participates in cache identity, because
changing that field can change active documentation under the same executable,
manual and request. Passive cache inspection uses the same identity input.
TTL, size limits, atomic writes, executable guards and probe policies are
unchanged. Existing caches are not purged.

Cold construction and isolated reload are checked for the actual Podman, SFTP
and Git captures, including source-only text and owning sections. Mocked
discovery verifies fixed request arguments and cache reuse without invoking
the inert executable/renderer identity files.

## Census and exact reconciliation

| Measure | Starting snapshot | Final snapshot |
| --- | ---: | ---: |
| Bundled profiles / categories / option-keyword records | 76 / 96 / 942 | Unchanged |
| Explicit named paths / driver route records | 327 / 155 | Unchanged |
| Required / complete maintained contracts | 504 / 504 | Unchanged |
| Debt / individual exceptions | 0 / 0 | Unchanged |
| Parsed help observations | 7,591 | 7,548 |
| Canonical option-keyword identities | 5,243 | 5,231 |
| External-only logical identities | 3,977 | 3,965 |
| Numeric fixed spellings | 30 | 26 |
| Protected input files / total inventory identities | 357 / 6,160 | 358 / 6,149 |
| Unresolved planning classifications | 4,249 | 4,237 |
| Heuristic warnings / external informational groups | 3 / 14 | Unchanged |

The 43-observation reduction comprises 27 nested SFTP observations across three
source copies and sixteen out-of-scope Git observations. These are parsed
source-observation counts, not unique options or removed command support.

Twelve incorrect logical root identities disappear: SFTP `-1`, `-h`, `-n`, `-t`,
and stash-show `--base`, `--cached`, `--merge-base`, `--staged`, `-0`, `-1`, `-2`
and `-static`. Their original text remains in source context. Native git-diff
parsing still recognizes the separately documented stage pairs.

One protected source identity is added for `cli_help/diagnostics.py`, which owns
passive scope-sensitive cache inspection. This is a source-census addition,
not an option or compatibility expansion.

Exactly 429 existing fingerprints are reassessed: 290 source-context additions,
101 declaration-location/alias relationships with unchanged option bodies,
21 recovered placeholder/operand records, nine scoped duplicate-observation
corrections, one existing route and six source owners. One repeated identical
declaration gains its correct distinct source observation. The machine ledger
retains each before/after fingerprint, observation set and reason.

Twelve orphaned active-option annotations are retired individually; the empty
nested-context investigation group is retired. Three recovered Podman memory
records move into `external-podman-operands-preserved`, retaining unresolved,
source-derived numerical status. The remaining resource investigations continue
separately. No factual group is promoted to verified, and no debt fingerprint,
allowed code or exception is refreshed or expanded.

## Verification and remaining limits

The final inspected passive selection covers parser/association tests, existing
driver and import validation, passive diagnostics, preservation/cache, inventory,
enforcement mutations, numerical contracts/migrations, presentation/search,
authoring, integration and inert insertion/navigation. Exact test IDs, results,
exclusions and environmental accommodations are retained in the ignored report.
Native/process fixtures are excluded unless their boundary is replaced by a
controlled mock. Windows test-only temporary permissions and the refusing Bash
fixture import stand-in do not change application behavior.

Early candidate rules exposed two regressions: treating every `Commands` heading
as interactive, and automatically restricting an unscoped borrowed log manual.
Dedicated counterexamples now protect both legacy behaviors. Initial new-test
API/whitespace assumptions were corrected without weakening existing tests.

Regeneration commands from the repository root are:

```bash
python -X utf8 -B scripts/inventory_numerical_descriptions.py --check --output tests/reports/numerical-inventory/association-inventory.json --summary
python -X utf8 -B scripts/check_numerical_coverage.py --output tests/reports/numerical-inventory/association-prospective.json --summary
python -X utf8 -B scripts/check_numerical_coverage.py --mode strict --output tests/reports/numerical-inventory/association-strict.json --summary
python -X utf8 -B -m unittest discover -s tests -p test_parser_association.py -v
git diff --check
```

The retained local guarded runner is
`.cache/parser-association-followup/run_tests.py`. Generated evidence under
`tests/reports/numerical-inventory/` includes the `association-baseline-*`
reports, `association-reconciliation.json`, current inventory/coverage reports,
`association-tests.json`, the initial new-test report and
`association-verification.json`. The verification report owns current exact test
totals, protected hashes, declaration comparisons and determinism results.
These ignored artifacts do not replace the maintained inventory or validator.

Remaining limits include other manual layouts, conservative ambiguous/variadic
grammars, unscoped legacy delegation, unversioned captures and incomplete external
numerical semantics. Native terminals, installed targets, POSIX recovery,
hardware, package lifecycle and hosted CI are not established by these tests.
No numerical migration, command-specific enrichment, probing expansion,
repository-configuration overhaul, staging, commit, push or publication occurs.

## Expansion-test response correction

The subsequent correction starts from a clean checkout at
`21453cb2d1adb949ffb3bdaa08caedb6f7aa03dd`. The two expansion tests for fixed
probe arguments and manual/disabled modes reproduce the reported stash-show
errors before editing. Both return the hand-authored `Options:` specimen as
the mocked git-diff manual. That specimen has no recognized common-option region,
so the declared route correctly rejects it. The earlier 251-test native selection
does not include this expansion module and supplies no result for these cases.

`probe_response` in
[the expansion tests](../../tests/test_expansion_development.py) now separates
executable help from fixed manual requests. Both mocked executable lookups still
resolve to `sys.executable`; the fixed renderer prefix identifies the manual
request. Its complete arguments must match the selected route. For scoped
manuals, the capture key locates a candidate, while the recorded `man` source,
full fixed argument tail, successful status and nonempty text establish whether
that candidate is usable. The recorded renderer name is deliberately distinct
from the mocked executable path. Missing or mismatched captures produce an
actionable assertion rather than a synthetic fallback.

Executable-help responses, unscoped manual specimens and the existing
pytest/Yarn/esptool identity responses retain their previous purposes. The
original synthetic specimen and raw captures remain byte-identical. No common
heading is fabricated and no production parser or route is changed.

New regression cases check help/manual separation, a generic unrelated source,
missing/mismatched capture requests and actual auto/man discovery through the
scoped stash-show route. Formatting options remain active, stage selectors remain
excluded, and the inadequate specimen still fails closed through discovery.
Existing pending-value, fixed-request and disabled-mode assertions remain intact.

The ignored local runner `.cache/native-posix-followup/run_native.py` now includes
the complete expansion-development module in its guarded `full` selection.
Its new `expansion` selection runs that module with the parser-association module.
The selection name `full` refers to this guarded subset, not the general Linux
suite. Normal CI discovery already includes the module; CI definitions and the
Python matrix are unchanged.

Focused reproduction on an existing suitable Linux/WSL environment:

```bash
python3 -B -m unittest discover -s tests -p test_expansion_development.py -v
python3 -B -m unittest discover -s tests -p test_parser_association.py -v
python3 -B scripts/inventory_numerical_descriptions.py --check --summary
python3 -B scripts/check_numerical_coverage.py --summary
python3 -B scripts/check_numerical_coverage.py --mode strict --summary
```

The complete focused selection passes 39 tests on Python 3.12.3 in Ubuntu 24.04
WSL and on Windows Python 3.13.0, with no skips. Windows-only inherited directory
permissions are confined to selected test cache paths; no production permission
changes occur. Exact focused and expanded regression selections are retained in
the ignored reports rather than inferred from prior test counts.
The expanded guarded Python 3.12 selection passes 268 tests across fifteen
modules with no skips. This is the inspected local subset, not a full Linux
suite or hosted-workflow result.

Python 3.10 is unavailable in the checked Windows launcher and common local
interpreter locations. The separately registered `Ubuntu` distribution cannot
start because its virtual disk is missing; its interpreter version is unknown.
No environment is repaired, installed or provisioned for this correction.

The unmodified full Linux suite is not run on either requested version under
this scope. It includes target/help-renderer process fixtures, a Bash test that
deliberately submits the pending line, editor fixtures and installation/release
tests. Those boundaries remain excluded rather than broadly mocked or reported
as full-suite passes. Python 3.10 and hosted-CI success remain unestablished.

Fresh evidence under `tests/reports/numerical-inventory/` uses the
`expansion-response-baseline-*`, `expansion-response-focused-313.json`,
`native-expansion-response-focused-312-tests.json`,
`native-expansion-response-regression-312-tests.json` and
`expansion-response-verification.json` names. Current reconciliation, coverage
and protected-file comparisons belong to those reports. Earlier native and
association reports remain historical evidence. No inventory annotation,
numerical policy, debt allowance or individual exception is changed.

The later [full Linux-suite verification](full-linux-verification.md) separately
establishes the unmodified Python 3.12 runner result after inspection of its
synthetic process and disposable lifecycle boundaries. It preserves the focused
correction above. That account also records the subsequent successful GitHub
Python 3.10 and 3.12 jobs with their run and commit identity. Local Python 3.10
verification remains unperformed, and the interrupted setup remnants are removed.
