# Bundled rsync option audit

First recorded 2026-11-21. This first pass covered 29 bundled rows. See the [expanded inventory and verification](rsync-manual-coverage.md) for the later manual comparison.

| Manual | Documented version | Client summary rows | Selectable | Other client rows | Daemon summary rows |
| --- | --- | ---: | ---: | ---: | ---: |
| [Ubuntu 24.04 LTS](https://manpages.ubuntu.com/manpages/noble/man1/rsync.1.html) | 3.2.7-1ubuntu1.5 | 144 | 29 | 115 | 14 |
| [Ubuntu 26.04 LTS](https://manpages.ubuntu.com/manpages/resolute/man1/rsync.1.html) | 3.4.1+ds1-7ubuntu0.3 | 144 | 29 | 115 | 14 |
| [Upstream rsync](https://download.samba.org/pub/rsync/rsync.1) | 3.5.2 | 157 | 29 | 128 | 16 |

Counts follow the printed **Option Summary**. Aliases on one row count once.
Daemon startup has a separate summary, including some spellings shared with the
client. At the pilot baseline, all daemon startup entries were manual-only.

## Selectable client options

The pilot covered 29 client selections. Its Details qualified preview and deletion, directory filters, transfer skipping and rate interpretation.

## Client options available in the manuals

The Ubuntu 3.2.7 and 3.4.1 summaries each listed 144 client and 14 daemon rows. Upstream 3.5.2 listed 157 client and 16 daemon rows. Some aliases shared a printed row, and some client and daemon spellings overlapped.

## Rendered-menu verification

The terminal regression opens the bundled profile in Bash with discovery off.
It checks the preview and deletion guidance in a 120×40 tmux pane, scrolls to the
last line at 60×16, then verifies that cancellation preserves the pending
command and cursor. A shell stub detects accidental execution.

Run the focused regression from the repository root in the
[local sandbox](development.md#isolated-local-debugging).

```bash
python3 -I tests/run_sandbox.py -- python3 -m unittest discover -s tests \
  -p test_terminal_screen.py -k test_rsync_preview_and_deletion_guidance_is_readable -v
```

All 29 summaries and full descriptions appeared in a 160×80 tmux pane on
Ubuntu 24.04.5 with Python 3.10.20 and 3.12.3 and on Ubuntu 26.04.1 with
Python 3.14.4. Each offline full suite ran 1,328 tests with 1,327 passes and one
Windows-specific skip. These checks exercised menu rendering and shell editing
without starting an rsync transfer.
