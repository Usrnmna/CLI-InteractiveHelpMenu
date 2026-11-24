"""Exercise the opt-in suite with disposable preflights and unittest fixtures."""

import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
CASES = '''
import unittest

class Cases(unittest.TestCase):
    def test_pass(self):
        print("case body ran")

    @unittest.skip("case unavailable")
    def test_skip(self):
        self.fail()

class Deferred(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        raise unittest.SkipTest("class unavailable")

    def test_unreachable(self):
        self.fail()
'''
FAILURES = '''
class Errors(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        raise RuntimeError("broken class fixture")

    def test_unreachable(self):
        self.fail()

class Subcases(unittest.TestCase):
    def test_subcases(self):
        with self.subTest(value=1):
            self.assertEqual(1, 2)
        with self.subTest(value=2):
            self.skipTest("subcase unavailable")
'''


class TimedUnittestTests(unittest.TestCase):
    """Compare the real shell entry point in normal and timed modes."""

    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.root = Path(folder.name)
        for folder in ("tests", "bash", "scripts", "cli_help"):
            (self.root / folder).mkdir()
        for name in ("bash/interactive-help.bash", "install.sh", "uninstall.sh", "update.sh",
                     "review-update.sh", "update-from-github.sh"):
            (self.root / name).write_text("true\n", encoding="utf-8")
        for name in ("run.sh", "timed_unittest.py"):
            if (ROOT / "tests" / name).exists():
                shutil.copyfile(ROOT / "tests" / name, self.root / "tests" / name)
        self.write("scripts/check_numerical_coverage.py", "print('numerical gate')\n")
        self.write("cli_help/main.py",
                   "import os\nprint('collection check', bool(os.getenv('CLI_HELP_DRIVERS')))\n")

    def write(self, path, source):
        """Install a fixture source file inside the disposable checkout."""
        (self.root / path).write_text(source, encoding="utf-8")

    def run_suite(self, timed):
        """Capture both standard streams and the shell's process exit code."""
        environment = dict(os.environ, CLI_HELP_TEST_TIMING=str(int(timed)), NO_COLOR="1")
        environment.pop("CLI_HELP_TEST_TIMING_STREAM", None)
        environment.pop("CLI_HELP_TEST_TIMING_LOG", None)
        environment.pop("CLI_HELP_DRIVERS", None)
        return subprocess.run(["bash", "tests/run.sh"], cwd=self.root, env=environment,
                              capture_output=True, text=True, timeout=30)

    def assert_pair(self, code):
        """Check normal output and status, ignoring the measured unittest duration."""
        normal, timed = self.run_suite(False), self.run_suite(True)
        self.assertEqual(normal.returncode, code, normal.stderr)
        self.assertEqual(timed.returncode, code, timed.stderr)
        self.assertEqual(normal.stdout, timed.stdout)
        scrub = lambda output: re.sub(r"in [0-9.]+s", "in <duration>",
                                      re.sub(r"(?m)^Test timing report: .*\n", "", output))
        self.assertEqual(scrub(normal.stderr), scrub(timed.stderr))
        report, = (self.root / "tests/reports/timing").glob("*/events.jsonl")
        return [json.loads(line) for line in report.read_text(encoding="utf-8").splitlines()]

    def test_discovery_and_fixture_skip_in_successful_suite(self):
        self.write("tests/test_fixture.py", CASES)
        events = self.assert_pair(0)
        discovery, = (row for row in events if row["event"] == "discovery-end")
        self.assertEqual(discovery["tests"], ["test_fixture.Cases.test_pass",
                                              "test_fixture.Cases.test_skip",
                                              "test_fixture.Deferred.test_unreachable"])
        outcomes = [row for row in events if row["event"] == "test-end"]
        self.assertEqual([row["outcomes"] for row in outcomes],
                         [[{"status": "pass"}], [{"status": "skip", "reason": "case unavailable"}]])
        fixture, = (row for row in events if row["event"] == "fixture-outcome")
        self.assertEqual(fixture["test"], "setUpClass (test_fixture.Deferred)")
        self.assertEqual(fixture["reason"], "class unavailable")

    def test_fixture_error_and_subtest_outcomes_in_failing_suite(self):
        self.write("tests/test_fixture.py", CASES + FAILURES)
        events = self.assert_pair(1)
        test, = (row for row in events if row["event"] == "test-end"
                 and row["test"] == "test_fixture.Subcases.test_subcases")
        # Python 3.10 defers failed subtest callbacks until the case ends.
        self.assertCountEqual(test["outcomes"], [
            {"status": "fail", "subtest": "test_fixture.Subcases.test_subcases (value=1)"},
            {"status": "skip", "subtest": "test_fixture.Subcases.test_subcases (value=2)",
             "reason": "subcase unavailable"},
        ])
        fixture = next(row for row in events if row.get("status") == "error")
        self.assertEqual(fixture["test"], "setUpClass (test_fixture.Errors)")
        failure, = (row for row in events if row["event"] == "first-failure")
        self.assertEqual(failure["test"], fixture["test"])

    def test_preflight_preserves_nonstandard_exit_status(self):
        self.write("tests/test_fixture.py", "raise AssertionError('tests must not be imported')\n")
        self.write("scripts/check_numerical_coverage.py", "raise SystemExit(37)\n")
        events = self.assert_pair(37)
        self.assertFalse(any(row["event"] == "discovery-start" for row in events))
        self.assertEqual(events[-1]["event"], "suite-end")
        self.assertEqual(events[-1]["exit_code"], 37)
        self.assertEqual(events[-1]["phase"], "numerical")
        self.assertEqual(events[-2]["event"], "first-failure")
        self.assertEqual(events[-2]["phase"], "numerical")

    def test_report_open_failure_preserves_suite_result(self):
        self.write("tests/reports", "blocked\n")
        self.write("scripts/check_numerical_coverage.py", "raise SystemExit(37)\n")
        timed = self.run_suite(True)
        self.assertEqual(timed.returncode, 37)
        self.assertIn("Cannot create test timing report", timed.stderr)

    def test_empty_discovery_uses_interpreters_native_exit_status(self):
        code = self.run_suite(False).returncode
        events = self.assert_pair(code)
        self.assertEqual(events[-1]["exit_code"], code)
        self.assertEqual(next(row["tests"] for row in events if row["event"] == "discovery-end"), [])
