#!/usr/bin/env bash
# Validate source syntax, bundled data, and the real Bash terminal contract.
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."

timing=
if [[ ${CLI_HELP_TEST_TIMING:-} == 1 ]]; then
    if [[ -n ${CLI_HELP_TEST_TIMING_STREAM:-} ]]; then
        timing=1
    elif mkdir -p tests/reports/timing 2>/dev/null &&
        report=$(mktemp -d tests/reports/timing/suite-XXXXXXXX 2>/dev/null); then
        export CLI_HELP_TEST_TIMING_LOG="$PWD/$report/events.jsonl"
        printf 'Test timing report: %s\n' "$CLI_HELP_TEST_TIMING_LOG" >&2
        timing=1
    else
        printf 'Cannot create test timing report in tests/reports/timing\n' >&2
    fi
fi

# Keep the preflight commands in the same errexit context in both modes.
# Reporting is best effort. The EXIT trap receives the suite's original status.
timing_event() {
    if [[ $timing == 1 ]]; then
        python3 -I tests/timed_unittest.py event "$@" || :
    fi
}

timing_phase() {
    phase=$1
    timing_event phase "$phase"
}

if [[ $timing == 1 ]]; then
    phase=start
    trap 'timing_event suite-end "$?" "$phase"' EXIT
    timing_event suite-start
fi
timing_phase shell-syntax
for script in bash/interactive-help.bash install.sh uninstall.sh update.sh review-update.sh update-from-github.sh; do
    bash -n "$script"
done
timing_phase numerical
python3 -B scripts/check_numerical_coverage.py --summary
timing_phase collection
python3 cli_help/main.py --check
timing_phase driver-collection
CLI_HELP_DRIVERS="$PWD/config/drivers.example" python3 cli_help/main.py --check

discovery=(discover -s tests -p 'test_*.py' -v)
if [[ $timing == 1 ]]; then
    timing_phase unittest
    python3 tests/timed_unittest.py "${discovery[@]}"
else
    python3 -m unittest "${discovery[@]}"
fi
