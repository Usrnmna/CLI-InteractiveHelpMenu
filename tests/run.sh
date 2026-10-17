#!/usr/bin/env bash
# Validate source syntax, bundled data, and the real Bash terminal contract.
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
bash -n bash/interactive-help.bash
python3 cli_help/main.py --check
python3 -m unittest discover -s tests -p 'test_*.py' -v
