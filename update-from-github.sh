#!/usr/bin/env bash
# Download a verified GitHub release and preserve the existing installation.
set -euo pipefail
if (( BASH_VERSINFO[0] < 4 || (BASH_VERSINFO[0] == 4 && BASH_VERSINFO[1] < 4) )); then
    printf '%s\n' 'Updating requires Bash 4.4 or newer.' >&2
    exit 1
fi
project_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
export PYTHONDONTWRITEBYTECODE=1
exec "${CLI_HELP_PYTHON:-python3}" "$project_root/scripts/release_update.py" "$@"
