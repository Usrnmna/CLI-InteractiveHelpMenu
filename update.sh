#!/usr/bin/env bash
# Upgrade an existing runtime from this source directory, preserving local edits.
set -euo pipefail
if (( BASH_VERSINFO[0] < 4 || (BASH_VERSINFO[0] == 4 && BASH_VERSINFO[1] < 4) )); then
    printf '%s\n' 'Updating requires Bash 4.4 or newer.' >&2
    exit 1
fi
project_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
exec "${CLI_HELP_PYTHON:-python3}" "$project_root/scripts/installation.py" update "$@"
