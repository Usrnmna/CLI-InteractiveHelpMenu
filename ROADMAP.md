# Project roadmap

**Next task — audit the 12 bundled GNU `tar` options.** Start with `--directory`
and the effect of argument order, then check archive selection, extraction,
exclusion patterns and compression. Continue with `grep` (14 entries) and
`ls` (19). The [tar profile](profiles/tar.json) contains the current menu text.
The [completed rsync pilot](docs/rsync-option-audit.md) shows the expected audit
and terminal evidence.

## Purpose and scope

The Interactive Help Menu helps a Bash user understand an option, select it
and continue editing the pending command. The current development goal is to
make the first line of help easy to scan while keeping the details needed to
choose and use each option correctly. Coverage includes bundled command
descriptions, options, operands and keywords, plus help displayed through
maintained discovery routes. The [project overview](README.md) describes the
product; the [documentation index](docs/README.md) covers its other capabilities.

Use this page to locate the next unfinished command and record progress.
Keep the detailed findings with each family audit. Update this roadmap when
a batch finishes, a source discrepancy blocks work, or the scope changes.

## Bundled menu progress

At the pilot baseline the [bundled profiles](profiles/) contained 942 selectable
entries across 76 profiles. The rsync review covered 29 entries, leaving 913
across 75 profiles. Counts include command-specific keywords and separate
alias profiles. Related spellings can share source research, but each menu
still needs a rendering and insertion check.

| Command family or commands | Profiles | Entries | Review status |
| --- | ---: | ---: | --- |
| `rsync` | 1 | 29 | Complete locally. [Manual comparison and sandbox results](docs/rsync-option-audit.md) |
| GNU `tar` | 1 | 12 | Next |
| GNU `grep`, `ls` | 2 | 33 | Queued after tar |
| OpenSSH — `ssh`, `scp`, `sftp` | 3 | 51 | Planned |
| Git — stash, worktree, commit and log | 13 | 104 | Planned, starting with stash and worktree |
| `7z`, `7zz`, `fd`, `fdfind`, `fzf`, `ffmpeg`, `yq` | 7 | 94 | Pending |
| `ip`, `ss`, `systemctl`, `journalctl`, `openssl` | 11 | 119 | Pending |
| `uv`, `ruff`, `pytest`, `go`, `dotnet`, `bun` | 18 | 232 | Pending |
| `podman`, `psql`, `ansible-playbook`, `az`, `gcloud` | 12 | 155 | Pending |
| `esptool`, `esptool.py`, `pio`, `platformio`, `arduino-cli` | 8 | 113 | Pending |

## Discovered command help

The [compatibility matrix](tests/fixtures/help/matrix.json) lists 162 maintained
command paths across 73 executable names at the pilot baseline. The matrix and
bundled inventories overlap. Count a bundled review against a discovery path
only when the audit also checks the help produced through that route.

| Matrix tier | Paths | Description review |
| --- | ---: | --- |
| Essential | 46 | Pending |
| Next | 65 | Pending |
| Extended | 51 | Pending |

For each path, identify its help source and version. Compare what the menu
displays with the applicable manual and available versioned help capture.
Some fixtures are synthetic or excerpted, and some root commands provide only
usage information. Record those outcomes explicitly. If a qualification appears
in a capture but disappears from the menu, trace it through parsing and
rendering, retain the original capture and add a regression for the loss.
See the [fixture provenance guide](tests/fixtures/help/README.md).

## How to audit a batch

1. **Establish the reference.** Inventory the command paths, selectable entries
   and aliases. Compare them with the upstream manual and the Ubuntu 24.04 and
   26.04 man pages where available. Record the actual versions, source links
   and any differences. For tools without a distribution man page, use
   version-matched official command documentation and identify the missing source.
2. **Decide what belongs on screen.** Give each row a short explanation of its
   effect. Keep details that change the invocation or result, including operand
   requirements, units, defaults, order, interactions, side effects and version
   limits. Remove duplicated wording and generic menu instructions. Keep useful
   manual terms searchable. Preserve precise numerical and argument guidance
   when changing prose. An entry can pass review with its existing wording.
3. **Account for gaps.** Record each material omission or conflict and its
   resolution. Identify documented options outside the curated selection so a
   future reviewer can distinguish a deliberate subset from an overlooked entry.
   Flag proposed additions separately for a scope decision.
4. **Verify the rendered result.** Inspect every revised row and its Details
   pane in a real terminal. At the 60×16 minimum, scroll to a consequential
   qualification and check that it is reachable. Search for a familiar manual
   term. Verify cancellation preserves the buffer and cursor, and selection
   inserts the intended spelling without executing the pending command.
5. **Run the compatibility checks.** Use the offline sandbox for focused tests
   while editing. At the end of a batch run the full suite on Ubuntu 26.04 with
   Python 3.14 and Ubuntu 24.04 with Python 3.10 and 3.12. Record pass, failure
   and skip counts with the environment. Record hosted CI separately when
   evidence for the revision is available. The [sandbox guide](docs/development.md#isolated-local-debugging)
   covers setup, targets and including new files.

## Recording progress and finishing the audit

For a partial batch, replace the status in its row with the exact command paths
reviewed, a link to the findings, any unresolved item and the next unchecked
path. Split a grouped row when that makes the remaining work clearer. Update
the **Next task** at the top. If profiles or matrix routes change, reconcile the
counts against the two linked inventories.

The audit is complete when every bundled entry and maintained discovery path
has a source-backed disposition, every material omission has been corrected or
documented with its remaining limitation, and the rendered-menu checks and
three sandbox configurations pass for the completed changes. Keep a link to
the final evidence here so the result can be checked from a fresh checkout.
