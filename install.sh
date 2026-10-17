#!/usr/bin/env bash
# Install the runtime and optionally register it in the current user's Bash rc file.
set -euo pipefail
if (( BASH_VERSINFO[0] < 4 || (BASH_VERSINFO[0] == 4 && BASH_VERSINFO[1] < 4) )); then
    printf '%s\n' 'Installation requires Bash 4.4 or newer.' >&2
    exit 1
fi
project_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
exec "${CLI_HELP_PYTHON:-python3}" "$project_root/scripts/installation.py" install "$@"
