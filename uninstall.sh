#!/usr/bin/env bash
# Remove a managed installation while retaining changed files and user data.
set -euo pipefail
project_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
exec "${CLI_HELP_PYTHON:-python3}" "$project_root/scripts/installation.py" uninstall "$@"
