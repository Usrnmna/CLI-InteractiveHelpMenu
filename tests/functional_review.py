#!/usr/bin/env python3
"""Record isolated Linux review evidence without executing pending workloads.

The suite mode runs the same preflight checks and unittest discovery as run.sh,
with per-test JSON outcomes. Live mode reuses the maintained compatibility
harness and checks additional supported paths against explicit sentinel flags.
"""

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
import time
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cli_help"))
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "scripts"))

# These paths use existing root discovery or built-in Git/Docker routes.
# Assertions are checked against installed help/manuals during the review.
ADDITIONAL_CASES = [
    ("grep", ["--ignore-case", "--line-number"], ["--version"]),
    ("find", ["-name", "-type"], ["--version"]),
    ("tar", ["--create", "--extract"], ["--version"]),
    ("git rebase", ["--interactive", "--onto"], ["--version"]),
    ("docker build", ["--file", "--tag"], ["--version"]),
]


def save_json(path, value):
    """Write inspectable UTF-8 evidence to the selected report directory."""
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def source_fingerprints():
    """Hash the release source inventory to detect edits during verification."""
    from build_release import source_files

    return {path.relative_to(ROOT).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in source_files(ROOT)}


class RecordedResult(unittest.TextTestResult):
    """Preserve unittest outcomes, including subtest failures and tracebacks."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.records = []
        self.subtests = []

    def record(self, test, status, detail=None):
        self.records.append({"test": test.id(), "status": status, "detail": detail})

    def addSuccess(self, test):
        super().addSuccess(test)
        self.record(test, "passed")

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.record(test, "failed", self._exc_info_to_string(err, test))

    def addError(self, test, err):
        super().addError(test, err)
        self.record(test, "error", self._exc_info_to_string(err, test))

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self.record(test, "skipped", reason)

    def addExpectedFailure(self, test, err):
        super().addExpectedFailure(test, err)
        self.record(test, "expected_failure", self._exc_info_to_string(err, test))

    def addUnexpectedSuccess(self, test):
        super().addUnexpectedSuccess(test)
        self.record(test, "unexpected_success")

    def addSubTest(self, test, subtest, err):
        super().addSubTest(test, subtest, err)
        status = "passed" if err is None else ("failed" if issubclass(err[0], test.failureException) else "error")
        self.subtests.append({"test": subtest.id(), "status": status})
        if err:
            self.record(subtest, status, self._exc_info_to_string(err, test))


def run_suite(output, label):
    """Run shell/configuration checks and all tests, retaining non-pass outcomes."""
    preflight = []
    for script in ("bash/interactive-help.bash", "install.sh", "uninstall.sh", "update.sh",
                   "review-update.sh", "update-from-github.sh"):
        result = subprocess.run(["bash", "-n", script], capture_output=True, text=True, timeout=15)
        preflight.append({"command": ["bash", "-n", script], "exit_code": result.returncode,
                          "output": result.stdout + result.stderr})
    for drivers in (None, str(ROOT / "config/drivers.example")):
        environment = dict(os.environ)
        if drivers:
            environment["CLI_HELP_DRIVERS"] = drivers
        result = subprocess.run([sys.executable, "cli_help/main.py", "--check"],
                                env=environment, capture_output=True, text=True, timeout=30)
        preflight.append({"drivers": drivers, "exit_code": result.returncode,
                          "output": result.stdout + result.stderr})
    started = time.monotonic()
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"), pattern="test_*.py")
    with (output / (label + ".log")).open("w", encoding="utf-8") as stream:
        result = unittest.TextTestRunner(stream=stream, verbosity=2,
                                        resultclass=RecordedResult).run(suite)
    counts = Counter(item["status"] for item in result.records)
    summary = {status: counts[status] for status in
               ("passed", "failed", "error", "skipped", "expected_failure", "unexpected_success")}
    document = {"tests_run": result.testsRun, "seconds": time.monotonic() - started,
                "summary": summary,
                "summary_unit": "test outcomes; failing subtests are separate records",
                "preflight": preflight, "cases": result.records, "subtests": result.subtests}
    save_json(output / (label + ".json"), document)
    print(json.dumps({"suite": label, "tests_run": result.testsRun, "summary": document["summary"]}), flush=True)
    return int(not result.wasSuccessful() or any(item["exit_code"] for item in preflight))


def run_live(output, timeout):
    """Exercise all maintained cases and a separate set of supported additions."""
    from command_paths import help_route, load_driver_registry
    from discovery import ProbeError, run_probe
    from live_compatibility import check_case, program_version
    import shutil

    registry = load_driver_registry(ROOT / "config/drivers.example")
    report = output / "live-programs.json"
    with (output / "live-console.log").open("w", encoding="utf-8") as stream:
        result = subprocess.run([sys.executable, "tests/live_compatibility.py", "--report", str(report), "--timeout", str(timeout)],
                                stdout=stream, stderr=subprocess.STDOUT, timeout=900)
    if not report.exists():
        raise RuntimeError("The live harness did not produce a report; inspect live-console.log")
    document = json.loads(report.read_text())
    for case in document["cases"]:
        words = case["command"]
        route = help_route(words[0], tuple(words[1:]), registry)
        case["help_arguments"] = list(route.arguments)
        case["manual"] = route.manual
    save_json(report, document)
    additions = []
    for command, flags, version_args in ADDITIONAL_CASES:
        words = command.split()
        case = check_case(words, registry, expected_flags=flags, timeout=timeout)
        case["version"] = program_version(words, version_args)
        case["expected_flags"] = flags
        route = help_route(words[0], tuple(words[1:]), registry)
        case["help_arguments"], case["manual"] = list(route.arguments), route.manual
        additions.append(case)
        binary = shutil.which(words[0])
        argv = [binary, *route.arguments] if binary and route.arguments else None
        if binary and not route.arguments and route.manual and shutil.which("man"):
            argv = [shutil.which("man"), "-P", "/bin/cat", "--no-hyphenation", "--no-justification", "--", route.manual]
        if argv:
            try:
                (output / (command.replace(" ", "-") + "-help.txt")).write_text(run_probe(argv, 10), encoding="utf-8")
            except ProbeError as error:
                case["capture_error"] = str(error)
    save_json(output / "live-additions.json", {"cases": additions, "source_timeout_seconds": timeout,
              "summary": dict(Counter(case["status"] for case in additions))})
    print(json.dumps({"live": document["summary"], "additions": dict(Counter(case["status"] for case in additions))}), flush=True)
    return int(result.returncode != 0 or any(case["status"] == "failed" for case in additions))


def main():
    """Select evidence lanes and isolate user configuration for their duration."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--suite", metavar="LABEL")
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--live-timeout", type=float, default=4)
    parser.add_argument("--prepend-path", action="append", default=[])
    parser.add_argument("--compose-plugin-dir", type=Path)
    args = parser.parse_args()
    if not args.suite and not args.live:
        parser.error("Select --suite LABEL and/or --live")
    if not 0.05 <= args.live_timeout <= 30:
        parser.error("--live-timeout must be between 0.05 and 30 seconds")
    if args.suite and (Path(args.suite).name != args.suite or args.suite in (".", "..")):
        parser.error("Suite label must be a filename without directories")
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    os.chdir(ROOT)
    with tempfile.TemporaryDirectory(prefix="cli-help-functional-review-") as home:
        for key in list(os.environ):
            if key.startswith("CLI_HELP_") or key.startswith("BASH_FUNC_") or key in ("BASH_ENV", "ENV", "PROMPT_COMMAND", "MANPATH"):
                os.environ.pop(key)
        os.environ.update(HOME=home, XDG_CONFIG_HOME=home + "/.config", XDG_DATA_HOME=home + "/.local/share",
                          XDG_CACHE_HOME=home + "/.cache", INPUTRC="/dev/null", LC_ALL="C.UTF-8")
        os.environ["PATH"] = os.pathsep.join([*args.prepend_path, "/usr/bin", "/bin"])
        if args.compose_plugin_dir:
            docker = Path(home) / ".docker"
            docker.mkdir()
            save_json(docker / "config.json", {"cliPluginsExtraDirs": [str(args.compose_plugin_dir.resolve())]})
        environment = {"recorded_at": datetime.now(timezone.utc).isoformat(), "platform": platform.platform(),
                       "python": sys.version, "path": os.environ["PATH"], "isolated_home": True}
        environment["source_sha256"] = source_fingerprints()
        for name, argv in {"bash": ["bash", "--version"], "gcc": ["gcc", "--version"],
                           "tmux": ["tmux", "-V"], "man": ["man", "--version"]}.items():
            try:
                probe = subprocess.run(argv, capture_output=True, text=True, timeout=10)
                environment[name] = {"exit_code": probe.returncode, "version": (probe.stdout + probe.stderr).splitlines()[0]}
            except (OSError, subprocess.TimeoutExpired) as error:
                environment[name] = {"error": str(error)}
        save_json(output / ((args.suite or "live") + "-environment.json"), environment)
        failed = run_suite(output, args.suite) if args.suite else 0
        if args.live:
            failed |= run_live(output, args.live_timeout)
        final_sources = source_fingerprints()
        environment["source_changes_during_run"] = sorted(
            name for name in environment["source_sha256"].keys() | final_sources.keys()
            if environment["source_sha256"].get(name) != final_sources.get(name))
        save_json(output / ((args.suite or "live") + "-environment.json"), environment)
        failed |= bool(environment["source_changes_during_run"])
        return failed


if __name__ == "__main__":
    raise SystemExit(main())
