# PostgreSQL psql command-line coverage

The [psql menu](../profiles/psql.json) grew from 21 to 70 rows, including one Ubuntu launcher option. The command-line Options sections agree on 35 effects and 70 distinct spellings. The shell glob alias `-?` is searchable under `--help`, with quoting guidance. The [declaration inventory](../tests/fixtures/psql-manual/declarations.tsv) lists each long spelling, short alias and operand requirement. The two long variable names share `-v`. The optional topic belongs only to the long help spelling.

## Sources and scope

The reviewed clients are PostgreSQL 19 upstream, Ubuntu 24.04's postgresql-client-16 version 16.15-0ubuntu0.24.04.1 and Ubuntu 26.04's postgresql-client-18 version 18.6-0ubuntu0.26.04.1. Their command-line sections expose the same options. The getopt declarations also agree across PostgreSQL 16.0, 17.4, 18.0 and 19.0. Existing structured connection and variable guidance retains its original 17.4 source scope. [PostgreSQL 19 manual](https://www.postgresql.org/docs/19/app-psql.html) · [Noble manual](https://manpages.ubuntu.com/manpages/noble/man1/psql.1.html) · [Resolute manual](https://manpages.ubuntu.com/manpages/resolute/man1/psql.1.html) · [PostgreSQL 19 client parser](https://github.com/postgres/postgres/blob/REL_19_0/src/bin/psql/startup.c)

The positional database and login role belong in the command description. SQL, interactive backslash commands, print settings and client variables have their own grammars. The menu explains how to pass or look up these operands. It covers client command-line options. The original fixture corpus includes a [versioned fixed-help capture](../tests/fixtures/help/followup-systems/psql.txt) and a separate compact format specimen.

Ubuntu also provides an option outside the upstream declaration table. The packaged `/usr/bin/psql` launcher recognizes `--cluster VERSION/NAME` or `--cluster VERSION/HOST:[PORT]`. The versioned client binary itself rejects that option. Noble documents it in postgresql-client-common 257build1.1. The extracted Resolute 290ubuntu1 wrapper and packaged man page confirm it. This adds one distinct effect to the 35 upstream effects, for 36 effects and 71 spellings. [Noble wrapper manual](https://manpages.ubuntu.com/manpages/noble/man1/pg_wrapper.1.html) · [Resolute wrapper manual](https://manpages.ubuntu.com/manpages/resolute/man1/pg_wrapper.1.html)

## Changes to the original rows

| Original spellings | Disposition and visible effect |
| --- | --- |
| `--host -h`, `--port -p`, `--username -U`, `--dbname -d` | Retained port ranges, per-host defaults and connection metadata. Added socket-directory syntax, the positional operands and connection-string precedence. |
| `--command -c`, `--file -f` | Completed input processing. Repeated actions run in order. One SQL string is a single request. A backslash command needs its own action. A dash filename reads standard input at that point. |
| `--no-psqlrc -X`, `--no-password`, `--password` | Added startup-file scope, failure without another password source, and prompt behavior on reconnect. |
| `--set -v` | Retained the distinction between assignment, unsetting and empty values. Added connection-state timing and the `--variable` alias. |
| `--csv`, `--tuples-only` | Retained the format and heading effects. Added how to omit the CSV header. |
| `--single-transaction` | Replaced an overly broad claim with the required `-c` or `-f` inputs, transaction boundaries, error handling and limits. |

Added the remaining input echo, output, field and record separator, session, list, version, help and formatting spellings. A log duplicates query output while an output destination redirects it. NUL field and record delimiters have separate effects.

## Verification

The extracted Ubuntu 26.04 client reported PostgreSQL 18.6. With an empty environment and private home, its fixed `--help` showed both variable aliases and its fixed `--help=commands` listed backslash commands. These probes exited before connecting. SQL execution and rollback behavior are manual findings. The [combined verification report](remaining-bundled-verification.md) records the menu and sandbox results.
