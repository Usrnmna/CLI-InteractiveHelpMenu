#!/usr/bin/env bash
# Validate source syntax, bundled data, and the real Bash terminal contract.
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
for script in bash/interactive-help.bash install.sh uninstall.sh update.sh review-update.sh update-from-github.sh; do
    bash -n "$script"
done
python3 cli_help/main.py --check
CLI_HELP_DRIVERS="$PWD/config/drivers.example" python3 cli_help/main.py --check
python3 -m unittest discover -s tests -p 'test_*.py' -v
