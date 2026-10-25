# Bundled numerical description migration

[Implementation inventory](README.md) · [Numerical contract and APIs](../numerical-value-contract.md)

This migration corrects authored menu text and adds opt-in descriptive metadata.
Essential numerical meaning appears in the existing `summary`, `detail`, or
profile-description fields. The migration did not connect metadata to rendering,
search, discovery, editing or insertion. Subsequent
[Step 4 source preservation](step4-preservation.md) provides bounded merger/cache
retention, and [Step 5 presentation](step5-presentation.md) connects the retained
explanations to the existing browser and search. No numerical completeness policy
is enabled for legacy profiles or external help.

## Scope and counting

The starting revision is `b7c2169c91e500fbdfae24df886aaeaf1e7fc62a`.
Enumeration was recalculated from that checkout rather than fixed to the audit's
79-entry seed. All 942 authored records were compared with their reviewed
dispositions; value-bearing records, fixed numerical spellings, keywords and
positional components received additional inspection. Short labels alone do not
establish accepted grammar or a numerical defect.

| Measure | Scope |
| --- | --- |
| 56 changed profiles | Existing authored profiles; no new command paths |
| 175 option records with metadata | 159 value-bearing records and 16 fixed flags; includes 9 keywords |
| 128 verified records | Evidence bounded to the explicit implementation/version/applicability variants |
| 47 source-derived records | Partial migration with outstanding investigations; maintained completeness is not claimed |
| 3 positional contracts | Existing repeated `ADDRESS FILE` groups, with 6 reviewed components |
| 123 preserved summaries | Metadata and details added while the original summary wording was retained |
| 52 revised summaries | Essential numerical meaning or a misleading grammar description corrected |

Aliases are separate authored records. Variants and components are not extra
options, and these totals must not be added together. A preserved summary is not
a claim that every original detail or accepted form was complete. Examples of
already useful wording include SFTP outstanding requests, fd directory depth,
worker counts, and output indentation; a missing detail field alone was not
classified as a unit defect.

The metadata classifications comprise 60 delegated values, 31 counts, 20
enumerations, 18 quantities, 17 identifiers, 14 composites, 6 timestamps, 5
durations, 2 nonnumerical operands, 1 index and 1 ordered level. Counts and
identifiers do not receive invented physical units. Pure path/text arguments,
named formats, interface names and fixed algorithm names retain their existing
review dispositions unless a specific numerical interpretation was established.
For example, SHA-256, TLS 1.3 and bzip2 name algorithms, protocols or formats;
their digits do not create a numerical operand.

The profile inventory remains 76 profiles, 96 categories, 942 options, 463
value-bearing records and 28 keywords. At Step 3 the wider inventory contained 6,119
identities, including 5,243 canonical option/keyword identities and 341 input
sources. Built-in paths, example drivers, matrix expectations, captures and
interpreter routes are unchanged. The 175 migrated records do not establish
coverage of the larger captured or dynamically discovered help surface. The
[current inventory guide](README.md) records Step 7's later source/definition
census expansion; these migration counts describe their original scope.

## Principal corrections and evidence

| Content | Authored explanation and applicable evidence |
| --- | --- |
| rsync `--bwlimit=` | Bare numbers use KiB/s: 1024 bytes/second. Single-letter and `iB` suffixes use binary powers; `KB`/`MB` forms use decimal powers. Suffixes are case-insensitive. Fractions, one-byte offsets, KiB granularity and zero disabling the cap are distinguished. [rsync 3.4.1 manual](https://raw.githubusercontent.com/RsyncProject/rsync/v3.4.1/rsync.1.md), `--bwlimit` and size suffix sections. |
| SCP/SFTP `-l` | The inspected implementation multiplies the positive decimal operand by 1024 bits/second, despite the manual's `Kbit/s` label. No suffix is accepted; zero is invalid. [OpenSSH Portable 9.9p2 SCP](https://raw.githubusercontent.com/openssh/openssh-portable/V_9_9_P2/scp.c) and [SFTP](https://raw.githubusercontent.com/openssh/openssh-portable/V_9_9_P2/sftp.c), `case 'l'`. |
| FFmpeg bitrates | Bare values are bits/s; `k`/`K` is decimal, `Ki` is binary, and final `B` multiplies by eight. Encoder defaults and zero effects are not universalized. [FFmpeg 7.1 codec options](https://raw.githubusercontent.com/FFmpeg/FFmpeg/n7.1/doc/codecs.texi) and [numerical syntax](https://raw.githubusercontent.com/FFmpeg/FFmpeg/n7.1/doc/fftools-common-opts.texi). |
| esptool size/frequency | Literal `4MB` means 4 MiB; lowercase `40m` means 40 MHz. Accepted literal sets are separate chip variants. `keep`, `detect`, environment overrides and image-header applicability are distinguished. [esptool 4.8.1](https://raw.githubusercontent.com/espressif/esptool/v4.8.1/docs/en/esptool/flash-modes.rst) and [5.0.2](https://raw.githubusercontent.com/espressif/esptool/v5.0.2/docs/en/esptool/flash-modes.rst), with the pinned CLI declarations linked in each profile. |
| FFmpeg times and Go timeout | FFmpeg bare seconds, `ms`/`us`, clock expressions and input/output placement are explicit. Go nonzero durations require units; `0` is a literal disabling exception, not a seconds default. The pinned testing implementation also disables the alarm for negative unit-bearing durations. [FFmpeg 7.1 time syntax](https://raw.githubusercontent.com/FFmpeg/FFmpeg/n7.1/doc/utils.texi), [Go 1.24.0 ParseDuration](https://raw.githubusercontent.com/golang/go/go1.24.0/src/time/format.go), [test flags](https://raw.githubusercontent.com/golang/go/go1.24.0/src/cmd/go/internal/test/test.go) and [M.startAlarm](https://raw.githubusercontent.com/golang/go/go1.24.0/src/testing/testing.go). |
| pytest durations | `--durations` counts report records; it does not take seconds. Zero selects all, subject to the separate seconds threshold. [pytest 8.3.5 runner](https://raw.githubusercontent.com/pytest-dev/pytest/8.3.5/src/_pytest/runner.py). |
| fzf limits, height and fields | Selection limits count items. Height distinguishes rows, percentages, inverse and adaptive forms. Field indices start at one, permit negative indices from the end and inclusive/open ranges. [fzf 0.60.3 manual](https://raw.githubusercontent.com/junegunn/fzf/v0.60.3/man/man1/fzf.1) and [parser](https://raw.githubusercontent.com/junegunn/fzf/v0.60.3/src/options.go). |
| journalctl/systemctl | Severity levels 0–7 are ordered; boot IDs/ordinals are not times. Calendar, relative and explicit `@` epoch-second forms retain their time basis. Status journal-line counts do not promise limits on `show` properties or `list-units` rows. [systemd 257 journalctl](https://www.freedesktop.org/software/systemd/man/257/journalctl.html), [time syntax](https://www.freedesktop.org/software/systemd/man/257/systemd.time.html) and [systemctl](https://www.freedesktop.org/software/systemd/man/257/systemctl.html). |
| Ruff widths and versions | Preferred width uses Unicode character widths, not UTF-8 bytes; bounds are 1–320. `py310` identifies Python 3.10 rather than a rescalable decimal value. [Ruff 0.11.13 settings](https://raw.githubusercontent.com/astral-sh/ruff/0.11.13/crates/ruff_workspace/src/options.rs). |
| Other counts and identifiers | Git commit/stash counts, PlatformIO workers/baud/control states, Podman log counts, IP prefix-bit counts and forwarding/mapping components have explicit counted subjects, scales or origins. Exact per-entry references and applicability appear in their metadata. |

Representative existing-field corrections include:

| Entry | Previous summary | Current summary |
| --- | --- | --- |
| rsync `--bwlimit=` | Limit transfer bandwidth | Limit bandwidth in KiB/s when unsuffixed; 0 is unlimited |
| SCP `-l` | Limit transfer bandwidth in Kbit/s | Limit bandwidth in units of 1024 bits/s |
| FFmpeg `-b:v` | Set the video bitrate | Set video bitrate in bits/s |
| esptool `--flash-size` | Set flash size | Set flash size; literal 4MB means 4 MiB |
| Go test `-timeout` | Set test timeout | Set timeout with units, such as 30s; 0 disables |

The original argument placeholders and behavioral declarations are retained.
Detail text supplies suffix rules, scales, special cases and release limits.
The psql command-string summary also distinguishes SQL/backslash commands from
an operating-system shell command. Delegated grammars identify their owning
configuration, expression, URL or command grammar instead of asserting one
universal numerical unit.

## Remaining evidence gaps

The 47 source-derived records remain selectable in the ordinary menu, but their
metadata produces `sem_review_required` in explicit maintained validation.
Unverified facets additionally produce `sem_unverified`. External validation
reports these as warnings, while structural contradictions remain errors.
Changing a review status is not a substitute for resolving the investigation.

| Entries | Required investigation |
| --- | --- |
| SFTP `-B`, `-R` | Confirm effective defaults/server caps and signed parsing edges for the supported client/server releases. Byte/request meaning in the pinned source is retained. |
| Ansible inventory/extra variables/forks; Arduino properties/jobs | Pin exact CLI releases, relevant configuration defaults and platform/plugin-dependent grammar. |
| Google Cloud filters/limits/page sizes/readable sizes; Azure queries/blob count | Pin SDK releases and service/API pagination behavior. Confirm numeric bounds and version-dependent special forms rather than imposing universal service limits. |
| PostgreSQL connection/database/command/variable options | Pin the client patch release and connection/variable grammar. Port/socket identifiers are not measurements. |
| uv Python requests; .NET test filters | Pin supported releases and implementation/test-runner alternatives. Version strings and expression numbers retain their owning grammar. |
| Git `--since=`, worktree `--expire` | Establish exact bare-number, relative and timezone parsing. The pinned expiry source already distinguishes `never`/`false` from `all`/`now`; direct prune's absent cutoff differs from garbage-collection age policy. |
| OpenSSL `-checkend`, `-verify`, `-connect` | Pin exact client patches and bounds. Verification depth counts intermediate CAs, excluding the leaf/trust anchor, but complete parser limits are not verified. |
| PlatformIO serial `-p`/`--port` | Establish numeric selector origin, matching and enumeration stability without enumerating devices during help browsing. |
| yq `--indent` | Verify zero/negative behavior per output encoder. The versioned default is two spaces; compact JSON is not a universal rule for every encoder or every program named yq. |
| GNU grep context | Pin supported releases and numeric limits. The described count applies separately before and after each match. |
| FFmpeg input/filter values | Verify protocol/filter-specific numerical grammar. The input URL or filtergraph has no single universal unit. |

Some rows cover several aliases/profiles. The exact member list is maintained in
[review.json](review.json); each profile node identifies the specific
investigation and source locator. Other releases and unlisted chips are not
implicitly covered. A `not_applicable` platform facet indicates that the
parameter definition does not select an OS; it does not assert platform support.
Chip tables describe documentation/source applicability, not hardware validation.

The unchanged review also retains 102 named-enumeration records requiring
accepted-form review and 4,246 unresolved classifications across the broader
inventory. Short categorical labels are not proof of a numerical defect or of
complete accepted forms. No complete semantic verification is claimed for that
remaining surface. At the Step 3 handoff, twelve `change_recommended` identities
concerned shared GNU numerical documentation. Step 4 records their bounded
source-preservation correction without promoting their factual review status.

## Review reconciliation and protected behavior

Exactly 234 stale fingerprints were justified: 175 option/keyword identities,
56 changed profile input sources and 3 profile descriptions. The original
fingerprints of the 6 positional components did not change; their dispositions
now point to the sibling component metadata. Five existing named fixed-selector
records were separately classified as adequate nonnumerical descriptions.

Changed option reviews were split by classification, evidence status and
preserved/corrected summary status. Exact source locators and investigations
remain with the metadata, avoiding a second copy of each definition. A bundled
correction does not verify a captured observation sharing its canonical ID.
Unaffected annotations and fingerprints remain unchanged. F1–F4 now record the
bounded content migration; F5 source preservation, F6 presentation and F7 global
future enforcement remain separate work.

An independent comparison with the starting parsed profiles removes only
description fields and the optional numerical metadata, then compares every
remaining declaration. It establishes unchanged command/category/flag/keyword
inventories, arity, optionality, attached forms, bundles, positional groups,
identity guards and boundaries. Hashes of 280 existing runtime, driver, capture
and GitHub-configuration files are unchanged. Passive insertion tests also
compare buffers and cursors with and without metadata for all selected options.

This evidence does not establish actual target grammar acceptance, installed
versions, terminal-width visibility, UI search behavior, metadata retention
through every editing workflow, or physical flash/serial operation. Those claims
require later work. No pending command, target help/version probe, source
expression or captured command was executed.

## Verification and maintenance

Run from the repository root, without target probes or network operations:

```bash
python -B -m unittest discover -s tests -p test_numerical_migration.py -v
python -B -m unittest discover -s tests -p test_value_semantics.py -v
python -B -m unittest discover -s tests -p test_numerical_inventory.py -v
python -B scripts/inventory_numerical_descriptions.py --check --summary
python -B scripts/inventory_numerical_descriptions.py --check --output tests/reports/numerical-inventory/inventory.json --summary
python -B cli_help/main.py --check
```

On Windows, `python -X utf8 -B` selects UTF-8 console output. The focused migration
tests discover existing opt-in fields automatically; unannotated legacy entries
are not subjected to a new completeness gate. Verified nodes use maintained
validation, while source-derived nodes retain expected external diagnostics.
Explicit alias groups are checked without inferring aliases from similar prose.

[migration-evidence.json](../../tests/fixtures/value-semantics/migration-evidence.json)
contains independently source-reviewed numerical expectations and explicit alias
relationships. It is distinct from synthetic contract fixtures and raw captured
help. The tests exercise plausible wrong scales, omitted units, false verified
claims and conflicting chip variants. A structurally valid but factually wrong
positive multiplier requires a source expectation or manual review; schema
validation cannot prove upstream facts.

The validator, formatter and insertion checks block process, network and file
access after their data is loaded, and compare input objects before and after.
Inventory tests cover deterministic output, source growth and annotation errors.
Generated inventory evidence remains under the existing ignored report directory;
no configuration change or hosted workflow is required.

The local focused checks pass 11 migration tests, 31 contract tests and 16
inventory tests. Structural profile/configuration checking also passes. The
ordinary core test command encounters three Windows temporary-directory ACL
errors; all 19 core tests pass when directory allocation uses real disposable
directories with inherited permissions under the ignored repository cache.
Application and maintained test code are unchanged by that accommodation.

The content migration is complete for the 175 annotated records and three
positional contracts within the reported evidence boundary. Full verified
migration remains open for the 47 source-derived records and the explicitly
unreviewed surfaces above. The separate Step 4 account documents subsequent
preservation through discovery, merging and caching. Formatter presentation,
authoring changes, global enforcement and Steps 5–9 remain outside this migration.
