#!/usr/bin/env bash
# Review saved update conflicts using the adjacent review helper.
set -euo pipefail
project_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
exec "${CLI_HELP_PYTHON:-python3}" "$project_root/scripts/update_review.py" "$@"
