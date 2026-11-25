# fzf option audit

First recorded 2026-11-22. This first pass covered 17 bundled rows. See the [expanded inventory and verification](fzf-manual-coverage.md) for the later manual comparison.

## Sources

| Reference | Version | Scope |
| --- | --- | --- |
| [Upstream fzf manual](https://raw.githubusercontent.com/junegunn/fzf/v0.75.0/man/man1/fzf.1) | 0.75.0 | Options, extended search, field expressions, preview placeholders, bindings and exit status. |
| [Ubuntu 24.04 fzf(1)](https://manpages.ubuntu.com/manpages/noble/man1/fzf.1.html) | 0.44.1-1ubuntu0.3 | Noble manual and distribution package. |
| [Ubuntu 26.04 fzf(1)](https://manpages.ubuntu.com/manpages/resolute/man1/fzf.1.html) | 0.67.0-1 | Resolute manual and distribution package. |
| [Pinned manual](https://raw.githubusercontent.com/junegunn/fzf/v0.60.3/man/man1/fzf.1), [argument parser](https://raw.githubusercontent.com/junegunn/fzf/v0.60.3/src/options.go) and [selection actions](https://raw.githubusercontent.com/junegunn/fzf/v0.60.3/src/terminal.go) | 0.60.3 | Version used by the structured value guides, including selection count, height modifiers and delimiter parsing. |

## Disposition of the 17 entries

The 17 selections covered matching, fields, selections, preview and display. The height summary needed both terminal rows and percentages. Narrow-screen checks exercised the delimiter qualification.

## Compatibility and manual-only coverage

A one-character dot acted as a regular expression on Noble and a literal on the later editions. The multi-character expression `[.]` matched a literal dot across the tested editions.

## Observed fzf behavior

The packaged fzf 0.44.1 and 0.67.0 executables ran in offline sandboxes against fixed, disposable input. Interactive fixtures used private tmux sockets and a preview that only printed a field. [Ubuntu package archive](https://archive.ubuntu.com/ubuntu/pool/universe/f/fzf/)

| Fixture | Observed result |
| --- | --- |
| Fuzzy, exact and anchored search | From `cat`, `scatter`, `cXaXt` and `dog`, both builds matched the first three for `cat`, the first two for `--exact` and only `cat` for the anchored query `^cat$`. Filter mode returned 1 for a missing term. |
| Delimiters and transformed fields | Splitting `a.ok` on `.` and searching field 2 for `ok` failed to match on Noble and matched on Resolute. The expression `[.]` matched on both. Both also accepted a multi-character regex delimiter. With `id:two:red`, `--with-nth 2.. --nth 1` matched `two` and Enter returned the original three-field item. |
| Record separators | Both builds preserved an embedded newline in a matching input item with `--read0`. Combining it with `--print0` emitted a NUL terminator. Each switch also worked independently. |
| Height parsing | Both accepted row, fractional percentage and adaptive percentage values. Only Resolute accepted `--height=-2`. Both rejected `--height=~-2` with status 2. |
| Marking items | In both finders two Tab presses followed by Enter returned two items with bare `--multi`. The same keys returned one item with `-m1`, `--multi=0`, `--multi=-1` or `-m-1`. |
| Layout, bindings and preview | In each of the three layouts, the observed prompt and first-match positions agreed with the menu. The finder displayed the initial query and both header lines in order. Moving between matches with bound keys changed a field-based preview before Enter. Accepting returned the highlighted original item. |

This filter prints `a.ok` and exits with status 0 on both Ubuntu builds. Changing `'[.]'` to `'.'` gives no output and status 1 on Noble.

```bash
printf '%s\n' a.ok a.no | fzf --delimiter '[.]' --nth 2 --filter ok
```

## Rendered menu and sandbox checks

The first-pass Bash/tmux checks walked the original selections, inspected the rendered Details and checked shell editing on the three Ubuntu/Python targets. [Terminal regression](../tests/test_expansion_terminal.py)

The first full-suite run caught a missing unit in the `--height` summary. The revised summary names terminal rows and percentages directly. Five focused tests then passed on each target, covering the minimum-size terminal interaction, optional selection counts, numerical semantics, visible units and the inventory review. To repeat the terminal check, substitute `host`, `noble310` or `noble312` for TARGET. [Sandbox instructions](development.md#isolated-local-debugging)

| Full offline suite | Python | Passed | Failed | Skipped |
| --- | --- | ---: | ---: | ---: |
| Ubuntu 24.04.5 LTS | 3.10.20 | 1,336 | 0 | 1 |
| Ubuntu 24.04.5 LTS | 3.12.3 | 1,336 | 0 | 1 |
| Ubuntu 26.04.1 LTS | 3.14.4 | 1,336 | 0 | 1 |

Each Linux suite skipped the Windows-specific probe.
