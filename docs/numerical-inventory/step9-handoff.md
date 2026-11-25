# Final repository configuration review and local handoff

This is the configuration review at `45a9c898938ad0a67a440af698378e5da601578e`. For the present checkout, use the [numerical inventory](README.md) and [repository configuration guide](../development.md#repository-configuration).

## Starting and ending state

Step 9 reviewed artifact ownership after [integrated numerical verification](step8-verification.md). The checkout began clean. The review changed six policy, test and documentation files. A comparison against the 494-file baseline preserved other tracked bytes and the index.

## Artifact ownership and policy dispositions

| Area checked | Finding and disposition |
| --- | --- |
| Git and editor settings | Maintained profiles, tests, guides and curated review JSON remained eligible for version control. Media, compressed fixtures and launchers retained binary treatment. The working copy had CRLF in 16 profiles and 69 help fixtures whose Git blobs used LF. The review preserved those input bytes. |
| Generated and private material | Reports, caches, recovery files, generated collections, temporary edits, credentials and local builds belonged outside the maintained inputs. Curated historical releases remained trackable. |
| Release source selection | Git and the link checker excluded installed data beneath `.local/share/cli-interactive-help/`, but the release selector admitted it under a maintained directory. The correction excluded the exact directory at any depth and retained the similarly named `cli-interactive-help-reference/`. A regression demonstrated both cases. [Selector](../../scripts/build_release.py) · [Policy tests](../../tests/test_repository_config.py) |
| CI and installation | Review covered the numerical gate, retry and failure paths, scoped evidence uploads, dependency groups, issue forms and installer inputs. Checks used parsed settings, policy queries and synthetic files. Hosted execution and package lifecycles had separate verification. |

## Numerical implementation and audit mapping

Findings F1–F4 concerned rates, scales, time expressions and counted or composite values. F5–F7 concerned keeping those facts through parsing, display and authoring, and detecting future omissions. The [phase summary](README.md#prioritized-implementation-work) links each implementation and its limits. Per-entry sources distinguish releases such as rsync 3.4.1, OpenSSH 9.9p2, FFmpeg 7.1, Go 1.24.0, fzf 0.60.3 and chip-specific esptool declarations.

## Current inventory and enforcement

At handoff, 76 profiles contained 942 option/keyword rows across 96 categories. The census covered 327 explicit named paths, 356 inputs and 6,159 review identities. Prospective checks passed. Strict mode reported 144 complete records out of 504 required, with 414 errors across the remaining 360 records. Of these, 304 lacked metadata, 47 retained source investigations and nine were shared definitions. Individual exceptions were empty. The later [debt-resolution review](debt-resolution.md) closed that exact population.

## Verification evidence and limits

Nine repository-policy tests and 13 retry-controller tests passed with zero skips. Review included effective Git attributes and ignores, parsed YAML, release source selection and numerical reconciliation. Retry tests used mocked HTTP and time. The run preserved runtime modules, 76 profiles, 209 fixtures and 11 historical release files. The preceding Step 8 passive suite had 362 passes and 17 platform skips. Later [native terminal and filesystem checks](native-posix-verification.md) establish their own platform-specific results.

## Reproduction and future handoff

From the repository root, the following commands exercise the corresponding checks on the current checkout. At the historical Step 9 revision the strict check returned 1.

```bash
python3 -B -m unittest discover -s tests -p test_repository_config.py -v
python3 -B -m unittest discover -s tests -p test_documentation_links.py -v
python3 -B scripts/inventory_numerical_descriptions.py --check --summary
python3 -B scripts/check_numerical_coverage.py --mode strict --summary
git check-ignore --no-index tools/home/.local/share/cli-interactive-help/profiles/private.json
git check-attr text eol linguist-generated -- docs/numerical-inventory/review.json
```

The original `step9-*.json` reports were local evidence under `tests/reports/numerical-inventory/`. Use a new baseline when reviewing later source changes.
