# Contributing

[Project overview](../README.md) · [Documentation index](../docs/README.md) ·
[Architecture and validation](../docs/development.md)

## Reports and proposals

Bug reports should identify the project revision or package, relevant Linux/Bash/
Python environment, and a minimal reproduction with synthetic arguments. Describe
expected behavior and observed buffer, cursor, or display changes separately.
Feature and compatibility requests should explain the intended interaction;
command requests should identify the implementation, version, route, and public
documentation where available.

Credentials, private paths, command histories, raw captures, and unredacted
diagnostic reports should remain local. Summaries of reason codes and relevant
configuration choices are usually sufficient. See
[passive diagnostics and privacy boundaries](../docs/diagnostics.md).

## Local changes and validation

The runtime targets Linux with Bash 4.4+, Python 3.10+ with `curses`, a UTF-8
locale, and `stty`. Linux sessions under WSL can provide the development
environment. Follow applicable repository instructions and keep changes focused
on the described problem.

Run relevant checks from the repository root. For runtime changes, the full
validation entry point is:

```bash
bash tests/run.sh
```

GCC, Git, and tmux are test dependencies. The
[development guide](../docs/development.md#source-layout-and-validation) describes
the test environment, focused suites, and evidence limits. Documentation-only
changes can use link and rendered-content checks appropriate to the edited files;
the [documentation workflow](../docs/development.md#continuous-integration)
documents the pinned link checker.

For Git ignore and attribute changes:

```bash
python3 -B -m unittest discover -s tests -p test_repository_config.py -v
git diff --check
```

For numerical-description inventory changes, run:

```bash
python3 -B scripts/inventory_numerical_descriptions.py --check --summary
python3 -B -m unittest discover -s tests -p test_numerical_inventory.py -v
```

The [inventory guide](../docs/numerical-inventory/README.md) defines source
coverage, counting rules, review identities, and unresolved work. New or changed
entries require review before their annotations or fingerprints are updated.
Reconciliation checks annotation integrity; it does not establish correct units
or implement the proposed production numerical contract. Record reviewed and
unresolved coverage separately. A complete local inventory can contain source
paths and raw-help excerpts; share the summary rather than the full report.

For maintained command/category/option/keyword/component or fixture changes,
also run the offline prospective numerical gate:

```bash
python3 -B scripts/check_numerical_coverage.py --summary
python3 -B -m unittest discover -s tests -p test_numerical_coverage.py -v
```

The [coverage policy and contributor workflow](../docs/numerical-inventory/step7-enforcement.md)
defines classification, metadata, provenance, display/search propagation and
exact exceptions. New and relevant changed content cannot inherit legacy debt.
Inspect full diagnostics without `--summary`; resolve heuristic disagreements
through source review rather than guessed units. Current prospective success
does not establish full maintained completeness: strict mode reports the exact
remaining migration debt. Raw external captures need explicit census review,
not fabricated verified contracts. Runtime legacy loading remains compatible.

For changes crossing numerical parsing, cache, authoring or presentation owners,
run `python -X utf8 -B -m unittest discover -s tests -p test_numerical_integration.py -v`.
The [integrated verification guide](../docs/numerical-inventory/step8-verification.md)
maps criteria to evidence and distinguishes passive success from native/platform
acceptance. A small repair needs a demonstrated failing guarantee and a regression
test; unresolved numerical migration must not be hidden by expanding debt.

Keep tests independent of real operational workloads. Browsing or inserting help
must leave the pending command unexecuted. Fixed help/version/manual probes have
separate [execution boundaries](../docs/discovery-and-safety.md). Terminal changes
require rendered evidence in addition to logical buffer assertions; recorded
versions and environments limit the scope of those results.

### Focused verification

Apply checks relevant to the changed behavior rather than reporting unrelated
suites as evidence for a different boundary.

| Changed area | Evidence to include |
| --- | --- |
| Terminal interaction | Visible cells, cursor, alternate screen, scrollback, and relevant resize/reopen behavior; mixed-width text and delayed key sequences for display/input changes |
| Compatibility and argument syntax | Captured implementation/version, fixed documentation requests, exact option names, attached values, declared bundles, argument/child boundaries, driver activation/precedence, and unchanged legacy defaults |
| Diagnostics and caching | Privacy, absence of target processes and writes in passive modes, provenance, redaction, and relevant cache invalidation |
| Collection or update recovery | Stale evidence, concurrent edits, uncertain locks, unsafe paths, interruptions, and preservation of original bytes |
| Repository configuration | Root and nested ignore rules, visible maintained fixtures/templates/releases, binary attributes and editor exclusions, workflow lint, strict failure handling, and explicitly scoped uploads |
| Numerical inventory | Independent counts, automatic discovery beyond sentinels, stable identities, annotation reconciliation, deterministic passive generation, and explicit semantic uncertainty |
| Numerical coverage | Prospective gate, shared contract diagnostics, exact debt/exception invalidation, omission/growth mutations and actual display/search propagation; strict readiness and factual verification remain separate |
| Release preparation | Exact candidate source manifest, checksums, actual-package lifecycle checks, and installed rendered adapter evidence; rebuild after changing included inputs and distinguish local candidates from publication |

## Generated files and release inputs

Use `.cache/` for downloaded tools and local environments, `tests/reports/` for
test/capture evidence, `dist/` for local release builds, and `generated-help/` for
checkout-local generated collections. Maintained help fixtures and public
documentation media remain trackable. The
[media guide](../docs/assets/README.md) explains actual terminal capture and
regeneration; screenshots and recordings should reflect observed behavior.

Numerical inventory facts belong in `tests/reports/numerical-inventory/`.
The guide and `docs/numerical-inventory/review.json` are maintained inputs and
remain visible to Git. Inventory test sessions use ignored `.cache/` snapshots;
`cli-help-inventory-*` directories are also excluded at any depth. Matching
release-source and link-scan rules exclude disposable inventory sessions.

Git ignore rules do not remove tracked files or control release packaging.
Inspect the diff and selected files before submitting. Preserve historical
release artifacts; new builds belong in a separate output directory. See
[release provenance and validation](../docs/release-candidate.md).

## Pull requests

Explain the concrete problem and resulting behavior. Include the checks actually
run, their results, and material compatibility limits. Distinguish fixture tests,
live help probes, rendered terminal checks, package checks, and hosted CI results.
Repository configuration changes should report ignore/attribute checks and
workflow validation when relevant. Local builds and local tests do not establish
publication or a passing hosted workflow.
