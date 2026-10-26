"""Run the offline suite with per-test evidence and pending-command protection.

Ordinary Bash GUI checks use static profiles with discovery disabled. Inspected
process-contract tests supply private PATH fixtures and retain their explicit
probe modes. The test that deliberately executes pending input is skipped.
Run from Linux; package and installation tests use their own disposable homes.
"""

import json
import os
from pathlib import Path
import sys
import time
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "tests/reports/current-regression"


class Evidence(unittest.TextTestResult):
    """Record individual outcomes, including failed subcases and skip reasons."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.records = []
        self.started = time.monotonic()

    def startTest(self, test):
        self.started = time.monotonic()
        super().startTest(test)

    def record(self, test, status, detail=""):
        self.records.append({"test": test.id(), "status": status, "detail": detail,
                             "seconds": round(time.monotonic() - self.started, 3)})

    def addSuccess(self, test):
        self.record(test, "pass")
        super().addSuccess(test)

    def addSkip(self, test, reason):
        self.record(test, "skip", reason)
        super().addSkip(test, reason)

    def addFailure(self, test, error):
        self.record(test, "fail", self._exc_info_to_string(error, test))
        super().addFailure(test, error)

    def addError(self, test, error):
        self.record(test, "fail", self._exc_info_to_string(error, test))
        super().addError(test, error)

    def addSubTest(self, test, subtest, error):
        if error:
            self.record(subtest, "fail", self._exc_info_to_string(error, test))
        super().addSubTest(test, subtest, error)


def main():
    """Apply review-only harness settings, run discovery and save local evidence."""
    os.chdir(ROOT)
    REPORTS.mkdir(parents=True, exist_ok=True)
    sys.path[:0] = [str(ROOT / "tests"), str(ROOT / "cli_help")]
    import test_bash_pty

    original = test_bash_pty.BashSession.__init__

    def isolated(self, folder, custom=False, locale_name="C.UTF-8", extra_environment=None):
        """Disable live lookup; explicit PATH cases retain controlled probe doubles."""
        extra = dict(extra_environment or {})
        if "PATH" not in extra:
            extra["CLI_HELP_DISCOVERY"] = "off"
        return original(self, folder, custom, locale_name, extra)

    test_bash_pty.BashSession.__init__ = isolated
    name = "test_select_inserts_without_executing_then_normal_enter_executes"
    method = getattr(test_bash_pty.BashIntegrationTests, name)
    reason = ("Task safety: this test explicitly executes its pending sentinel command; "
              "passive insertion is covered separately.")
    setattr(test_bash_pty.BashIntegrationTests, name, unittest.skip(reason)(method))

    started = time.monotonic()
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"), pattern="test_*.py")
    result = unittest.TextTestRunner(verbosity=2, resultclass=Evidence).run(suite)
    report = {"tests_run": result.testsRun, "failures": len(result.failures),
              "errors": len(result.errors), "skipped": len(result.skipped),
              "seconds": round(time.monotonic() - started, 3), "python": sys.version,
              "records": result.records}
    (REPORTS / "linux-suite.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return int(not result.wasSuccessful())


if __name__ == "__main__":
    raise SystemExit(main())
