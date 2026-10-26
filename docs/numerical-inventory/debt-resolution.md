# Maintained numerical contract debt resolution

[Implementation inventory](README.md) · [Coverage policy](step7-enforcement.md) · [Numerical contract](../numerical-value-contract.md) · [Previous local handoff](step9-handoff.md)

The subsequent [diagnostic investigation](diagnostic-investigation.md) records
fresh review of the retained heuristic/external diagnostics without changing
the maintained completeness result. The counts and test selections below
remain evidence from the debt-resolution follow-up.

The maintained-content follow-up resolves all 360 previously incomplete records.
Strict and prospective coverage both pass: all 504 required contracts are
complete, the legacy-debt entries list is empty and no individual exceptions
exist. The validator, formatter, checker, eligibility rules and runtime mechanisms
are unchanged. This is maintained contract completeness within recorded source
applicability, not universal verification of external help or installed targets.

## Baseline, scope and current census

The starting checkout was clean on `main` at
`06b1347de65b89f1565c3acaad3f646e69694b41`. Earlier Steps 1–9 were already present.
The branch, revision and Git index remain unchanged. All follow-up edits remain
local, unstaged and uncommitted.

| Measure | Starting result | Final result |
| --- | --- | --- |
| Required maintained contracts | 504 | 504; identical source/identity eligibility |
| Complete contracts | 144 | 504 |
| Incomplete records / strict errors | 360 / 414 | 0 / 0 |
| Individual exceptions | 0 | 0 |
| Bundled profiles / categories / option-keyword records | 76 / 96 / 942 | Unchanged |
| Value-bearing records / keywords / optional-value records | 463 / 28 / 6 | Unchanged overlapping subsets |
| Shared definitions / positional groups / components | 22 / 3 / 6 | Unchanged |
| Explicit named paths / primary matrix cases | 327 / 162 | Unchanged |
| Protected inventory inputs / identities | 356 / 6,159 | 357 / 6,160; one new maintained semantic reference fixture |
| Parsed help observations / canonical option-keyword identities | 7,591 / 5,243 | Unchanged |

The original debt comprised 304 missing contracts, 47 source-derived
option/keyword contracts and nine source-derived definitions. Definitions overlap
their explicit consumers; these are record counts and must not be added as
independent option coverage. The 304 omissions included ordinary text, paths,
named choices and identifiers, rather than 304 proven missing physical units.

Content changes affect 68 existing profiles: 351 option/keyword records and nine
definitions. The 351 records comprise 170 nonnumerical values, 58 enumerations,
56 identifiers, 39 delegated grammars, 13 ordered levels, ten counts, two
timestamps and one each of composite, scalar duration and physical quantity.
The nine definitions add seven delegated grammars, one count and one identifier.
All 479 option/keyword contracts, three groups and 22 definitions now pass.

The earlier 128 verified option contracts and positional metadata retain their
existing evidence. Fresh research concerns the incomplete records; it does not
represent a new independent factual audit of every earlier claim.

## Source review and principal corrections

Authoritative version-tagged source and applicable official references establish
the new declarations. Retrieval is data-only: no upstream source, target help,
editor, workload or installed application is executed. Selected SDK source text
is read from Google's official pinned archive without extracting an SDK tree or
installing it.
The separate [semantic reference fixture](../../tests/fixtures/value-semantics/debt-resolution-evidence.json)
records independent expectations for difficult cases; complete per-entry URLs,
locators and applicability remain owned by production metadata.

| Content | Source-reviewed correction or completed boundary |
| --- | --- |
| OpenSSL `s_client -verify` | The CLI requires a positive depth and rejects zero; intermediate CAs are counted, excluding leaf and trust anchor. The earlier zero allowance confused this CLI parser with other depth APIs. [3.0.16 option declaration](https://raw.githubusercontent.com/openssl/openssl/openssl-3.0.16/apps/s_client.c) and [positive-integer parser](https://raw.githubusercontent.com/openssl/openssl/openssl-3.0.16/apps/lib/opt.c) establish the distinction |
| OpenSSL `x509 -checkend` | Signed, base-autodetected integer seconds must fit the implementation's integer/time types. Zero means the current instant; negatives move the comparison into the past. No universal platform width or safe extreme offset is invented. [3.0.16 implementation](https://raw.githubusercontent.com/openssl/openssl/openssl-3.0.16/apps/x509.c) |
| SFTP `-B` / `-R` | Bytes and outstanding requests remain distinct. Legacy decimal `strtol` parsing rejects zero/tail text but can wrap/truncate negative or large conversions. Newer `-X` bounds are not transplanted. Fallbacks are 32,768 bytes and 64 requests; server negotiation affects unspecified defaults, and SFTP v0 limits buffers to 20,480 bytes. [9.9p2 CLI](https://raw.githubusercontent.com/openssh/openssh-portable/V_9_9_P2/sftp.c) and [client initialization](https://raw.githubusercontent.com/openssh/openssh-portable/V_9_9_P2/sftp-client.c) |
| Arduino compilation jobs | The operand is a signed 32-bit worker count; zero uses available CPU cores. Negative values pass the CLI's integer parser but start no workers and can stall queued compilation. This source-level upstream limitation is documented, not repaired or exercised. [1.2.2 CLI](https://raw.githubusercontent.com/arduino/arduino-cli/v1.2.2/internal/cli/compile/compile.go) and [worker loop](https://raw.githubusercontent.com/arduino/arduino-cli/v1.2.2/internal/arduino/builder/compilation.go) |
| Ansible forks and source grammars | Forks require at least one process; configured defaults retain the built-in value five. Inventory, host-pattern subscripts and extra variables retain plugin/variable-specific grammar rather than fabricated global units. [2.18.6 conflict validation](https://raw.githubusercontent.com/ansible/ansible/v2.18.6/lib/ansible/cli/__init__.py) and [inventory pattern evaluation](https://raw.githubusercontent.com/ansible/ansible/v2.18.6/lib/ansible/inventory/manager.py) |
| gcloud list limits / page sizes | Both accept positive counts up to the SDK Python `sys.maxsize`, or exact lowercase `unlimited`. Zero/negatives are rejected by the SDK argument type; service paging limits remain distinct. Readable-size output uses binary KiB/MiB/GiB with `--long`, not a numerical operand. The [official 515.0.0 archive](https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-515.0.0-linux-x86_64.tar.gz), `calliope/base.py`, `arg_parsers.py` and storage listing sources establish these facts |
| PostgreSQL ports and commands | Ports identify TCP services/socket suffixes; explicit ports must be 1–65535. One shared port or a host-matched list is supported, with empty entries selecting defaults. Database connection strings, SQL/backslash commands and psql variables retain their own grammar. [17.4 libpq connection implementation](https://raw.githubusercontent.com/postgres/postgres/REL_17_4/src/interfaces/libpq/fe-connect.c) and [psql reference](https://raw.githubusercontent.com/postgres/postgres/REL_17_4/doc/src/sgml/ref/psql-ref.sgml) |
| PlatformIO serial ports | Explicit non-pattern strings, including digit-only strings, pass through unchanged. No stable numerical device index is established. Patterns select the first matching enumerated device, whose ordering is not stable. [6.1.18 port finder](https://raw.githubusercontent.com/platformio/platformio-core/v6.1.18/platformio/device/finder.py) |
| Git dates / expiry | A bare number is not uniformly a duration: Git's date heuristics distinguish large epoch-second candidates from calendar/time fields. Explicit calendar, timezone and relative forms remain available. Exact `never`/`false` select zero cutoff, while `all`/`now` select `TIME_MAX`; direct prune defaults differ from garbage-collection age policy. [2.48.0 date implementation](https://raw.githubusercontent.com/git/git/v2.48.0/date.c) |
| yq indentation | Positive values count spaces. YAML zero selects four spaces and rejects negatives; JSON/XML nonpositive values use no indentation spaces. This does not promise single-line XML. The CLI assigns this preference only to YAML/JSON/XML; other encoders are unaffected. [4.44.3 preference assignments](https://raw.githubusercontent.com/mikefarah/yq/v4.44.3/cmd/utils.go), [YAML dependency](https://raw.githubusercontent.com/mikefarah/yq/v4.44.3/go.mod) and [encoder zero default](https://raw.githubusercontent.com/go-yaml/yaml/v3.0.1/encode.go) |
| Named values / delegated grammars | MSBuild configuration, framework and runtime strings are identifiers, not closed numeric scales. VSTest filters, Azure JMESPath, uv Python requests and FFmpeg URL/filtergraph values identify their actual parser/delegation boundary. Ruff extension mapping uses `python`, `pyi` and `ipynb`; `py` is not the language token. [Ruff 0.11.13 parser](https://raw.githubusercontent.com/astral-sh/ruff/0.11.13/crates/ruff_linter/src/settings/types.rs) |
| .NET verbosity enum codes | The SDK's enum parser also admits integers: 0/1 select quiet/q, 2/3 minimal/m, 4/5 normal/n, 6/7 detailed/d and 8/9 diagnostic/diag. These alias codes are not five linear severity levels. Undefined representable codes can be forwarded numerically and rejected downstream. Case-insensitive named levels remain the recommended spelling. The [SDK dependency revision](https://raw.githubusercontent.com/dotnet/sdk/v9.0.200/eng/Version.Details.xml) pins the [actual enum converter](https://raw.githubusercontent.com/dotnet/command-line-api/803d8598f98fb4efd94604b32627ee9407f246db/src/System.CommandLine/Binding/ArgumentConverter.cs) |

Existing adequate summaries are preserved. Seven summaries place clarified
worker-count, list-count, positive-depth or encoder-specific meaning earlier.
Obsolete investigation prose on the previously source-derived records is replaced
with the reviewed explanation and exact release qualification. Bare numbers,
accepted spellings and actual scale remain separate; no input conversion occurs.

Evidence pinning does not remove command support or add runtime version guards.
Unlisted releases, libraries, plugins, services and chips are not silently
verified. Azure's JMESPath dependency is not release-pinned by its CLI package;
the contract verifies the pinned CLI's delegation and the owning grammar, not an
invented universal library version or function set. Board/build properties and
protocol/filter-specific values similarly retain their actual owner.

## Shared definitions, reviews and debt removal

Existing definition names and explicit reference relationships are retained:

| Profile | Definitions and all explicit consumers |
| --- | --- |
| `ansible-playbook` | `inventory-source`: `--inventory`, `-i`; `extra-variables`: `--extra-vars`, `-e` |
| `arduino-cli compile` | `compile-jobs`: `-j`, `--jobs` |
| `pio device monitor`, `platformio device monitor` | Each profile's own `serial-port-selector`: `-p`, `--port` |
| `psql` | `server-port`: `--port`, `-p`; `database-request`: `--dbname`, `-d`; `command-string`: `--command`, `-c`; `variables`: `--set`, `-v` |

These nine definitions have 18 explicit option consumers; consumers are already
included in the 351 option/keyword records. Similar summaries never establish an
alias. Positional groups and their six component declarations remain unchanged.

Reconciliation updates exactly 429 stale fingerprints: 351 option/keyword
identities, nine definitions, 68 changed profile inputs and the existing semantic
reference fixture. One new fixture source receives its own disposition. Reviewed
members move into classification-specific completed-contract groups; unrelated
group fields, members and fingerprints remain unchanged. Newly emptied groups
are removed without changing surviving decisions. External observations sharing
an identity remain explicitly outside the bundled factual disposition.

Each of the 360 debt rows is removed only after its actual maintained validation
and presentation/search propagation checks pass. The policy's enrollment context,
invalidation rules, supported codes and empty exceptions list are preserved.
No failing record receives a new or refreshed allowance. The exact removed rows,
source identities and fingerprint changes are recorded in ignored machine-readable
evidence; inventory generation does not perform this review automatically.

## Verification and protected behavior

The final passive selection passes **250 tests across 13 modules, with no skips**:
contract, inventory, migration, enforcement/mutations, source preservation,
presentation/search/layout, authoring, integrated round trips, core validation,
navigation, literal insertion, argument syntax and optional integer behavior.
The 13 new source-fact tests exercise actual browser details/search and a fake
window. Independent expectations come from the reviewed reference fixture.

The existing enforcement mutation tests still reject new deficient profiles,
categories, options, keywords, fixtures and components; missing meaning/scale or
bare-number rules; invalid references/forms/aliases; obsolete exceptions; and
display/search omissions. New regressions also deliberately remove active
details/search text and factual evidence. All coverage/validator implementation
bytes and the complete required source/identity set match the starting baseline.

Two tests that depended on production debt are corrected without reducing their
requirements: an explicit legacy specimen still requires `sem_metadata_missing`,
and source-derived mutations still require review diagnostics and external
warnings. Historical unresolved-example identities remain in the semantic fixture
under an explicitly historical key. Existing unit/scale and alias assertions
remain active.

The initial broader selection accidentally included one CLI subprocess fixture;
the process guard blocked it before launch. That unchanged fixture is excluded
from the final passive selection, and only its affected module is rerun. Another
collection subprocess fixture is excluded in advance. No target or real editor
runs. Windows test-only inherited temporary-directory permissions apply solely
under selected ignored cache paths; application permissions are unchanged.

Independent comparisons preserve all profile fields except authorized option
summary/detail/metadata and the nine reviewed definitions. Flags, categories,
placeholders, arity, optionality, attached forms, bundles, positional metadata,
command boundaries, supported routes and literal insertion remain unchanged.
Runtime modules, drivers, configuration, raw help captures and all 11 tracked
historical release files retain their starting bytes. Existing unrelated CRLF
files are not normalized; edited profile JSON uses the existing UTF-8/LF policy.

The three existing heuristic warnings and ten external informational diagnostics
remain visible. The 4,246 unresolved inventory classifications principally concern
external observations or declaration-only evidence; they are not maintained
completeness debt. A captured option or passing matrix sentinel still does not
establish a complete upstream grammar.

No native Bash/Readline, POSIX recovery, installed-target, hardware, package or
hosted-CI result is supplied. Earlier step acceptance records retain their
historical status; native gaps remain open despite current strict success.

## Reproduction and evidence

Run from the repository root with existing Python/Git availability:

```bash
python -X utf8 -B scripts/inventory_numerical_descriptions.py --check --summary
python -X utf8 -B scripts/inventory_numerical_descriptions.py --check --output tests/reports/numerical-inventory/debt-inventory.json --summary
python -X utf8 -B scripts/check_numerical_coverage.py --output tests/reports/numerical-inventory/debt-prospective.json --summary
python -X utf8 -B scripts/check_numerical_coverage.py --mode strict --output tests/reports/numerical-inventory/debt-strict.json --summary
python -X utf8 -B -m unittest discover -s tests -p test_numerical_debt_resolution.py -v
python -X utf8 -B -m unittest discover -s tests -p test_numerical_migration.py -v
python -X utf8 -B -m unittest discover -s tests -p test_value_semantics.py -v
python -X utf8 -B -m unittest discover -s tests -p test_numerical_coverage.py -v
git diff --check
```

Both coverage commands now exit zero. The retained local guarded runner is
`.cache/numerical-debt-followup/run_tests.py`; its explicit module selections and
process exclusions are recorded in `tests/reports/numerical-inventory/debt-tests.json`.
The general Linux suite contains process/native/package fixtures and is not a
substitute for this task's inspected passive selection.

Generated evidence remains under `tests/reports/numerical-inventory/`:
`debt-baseline-inventory.json`, `debt-baseline-prospective.json`,
`debt-baseline-strict.json`, `debt-reconciliation.json`, `debt-tests.json`,
`debt-inventory.json`, `debt-prospective.json`, `debt-strict.json` and
`debt-followup-verification.json`. `debt-source-evidence.json` records the reviewed
source URLs, archive members and text hashes. The original baseline and pinned research text
are retained separately under `.cache/numerical-debt-followup/`. Reports use
deterministic ordering and repository-relative references; they are local,
ignored evidence rather than publication artifacts.

No maintained contract remains unresolved within this reported scope. Extending
factual claims to other implementations/releases, fixing upstream operational
edge behavior or obtaining native acceptance requires separate work. No new
command enrichment, compatibility expansion, runtime redesign, unrelated
configuration change, build, package/release operation, staging, commit, push,
hosted workflow trigger or online repository modification occurs in this follow-up.
Read-only authoritative documentation retrieval is the only network activity.
