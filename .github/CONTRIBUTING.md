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
| Release preparation | Exact candidate source manifest, checksums, actual-package lifecycle checks, and installed rendered adapter evidence; rebuild after changing included inputs and distinguish local candidates from publication |

## Generated files and release inputs

Use `.cache/` for downloaded tools and local environments, `tests/reports/` for
test/capture evidence, `dist/` for local release builds, and `generated-help/` for
checkout-local generated collections. Maintained help fixtures and public
documentation media remain trackable. The
[media guide](../docs/assets/README.md) explains actual terminal capture and
regeneration; screenshots and recordings should reflect observed behavior.

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
