"""Record opt-in timing while delegating discovery, output and status to unittest."""

import json
import os
import sys
import time
import unittest


report_failed = False


def emit(event, **fields):
    """Append an event to the standalone report or the sandbox stdout stream."""
    global report_failed
    if report_failed:
        return
    stream = os.environ.get("CLI_HELP_TEST_TIMING_STREAM")
    path = os.environ.get("CLI_HELP_TEST_TIMING_LOG")
    encoded = json.dumps({"event": event, "monotonic": time.monotonic(), **fields}) + "\n"
    try:
        if stream:
            with os.fdopen(os.dup(1), "wb") as output:
                output.write((stream + encoded).encode("ascii"))
        elif path:
            with open(path, "a", encoding="utf-8") as output:
                output.write(encoded)
    except OSError as error:
        report_failed = True
        try:
            print(f"Cannot write test timing report: {error}", file=sys.stderr)
        except OSError:
            pass


def test_ids(suite):
    """Yield discovered IDs in traversal order before unittest consumes the suite."""
    for item in suite:
        if isinstance(item, unittest.BaseTestSuite):
            yield from test_ids(item)
        else:
            yield item.id()


class TimedLoader(unittest.TestLoader):
    """Observe ordinary discovery and keep even IDs blocked by fixture errors."""

    def discover(self, start_dir, pattern="test*.py", top_level_dir=None):
        emit("discovery-start")
        suite = super().discover(start_dir, pattern, top_level_dir)
        emit("discovery-end", tests=list(test_ids(suite)))
        return suite


class TimedResult(unittest.TextTestResult):
    """Record outcome callbacks without altering result bookkeeping or console output."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.active = None
        self.case_seconds = 0.0
        self.failed = False

    def startTest(self, test):
        emit("test-start", test=test.id())
        self.active = test
        self.started = time.monotonic()
        self.outcomes = []
        super().startTest(test)

    def stopTest(self, test):
        super().stopTest(test)
        seconds = time.monotonic() - self.started
        self.case_seconds += seconds
        emit("test-end", test=test.id(), seconds=seconds, outcomes=self.outcomes)
        self.active = None

    def record(self, test, status, *, parent=None, **fields):
        """Attach subtests to their case and emit fixture results outside any case."""
        if status in {"fail", "error", "unexpected-success"} and not self.failed:
            self.failed = True
            emit("first-failure", test=test.id(), status=status)
        outcome = {"status": status, **fields}
        if self.active is None:
            emit("fixture-outcome", test=test.id(), **outcome)
        else:
            if parent is not None:
                outcome["subtest"] = test.id()
            self.outcomes.append(outcome)

    def addSuccess(self, test):
        self.record(test, "pass")
        super().addSuccess(test)

    def addSkip(self, test, reason):
        self.record(test, "skip", parent=getattr(test, "test_case", None), reason=reason)
        super().addSkip(test, reason)

    def addFailure(self, test, error):
        self.record(test, "fail")
        super().addFailure(test, error)

    def addError(self, test, error):
        self.record(test, "error")
        super().addError(test, error)

    def addExpectedFailure(self, test, error):
        self.record(test, "expected-failure")
        super().addExpectedFailure(test, error)

    def addUnexpectedSuccess(self, test):
        self.record(test, "unexpected-success")
        super().addUnexpectedSuccess(test)

    def addSubTest(self, test, subtest, error):
        if error is not None:
            status = "fail" if issubclass(error[0], test.failureException) else "error"
            self.record(subtest, status, parent=test)
        super().addSubTest(test, subtest, error)


class TimedRunner(unittest.TextTestRunner):
    """Keep standard console formatting and measure execution outside individual cases."""

    resultclass = TimedResult

    def run(self, test):
        emit("unittest-start")
        started = time.monotonic()
        result = super().run(test)
        seconds = time.monotonic() - started
        emit("unittest-end", seconds=seconds, case_seconds=result.case_seconds,
             outside_cases_seconds=seconds - result.case_seconds, tests_run=result.testsRun,
             failures=len(result.failures), errors=len(result.errors), skipped=len(result.skipped),
             expected_failures=len(result.expectedFailures),
             unexpected_successes=len(result.unexpectedSuccesses))
        return result


def main():
    """Record a shell checkpoint or invoke the native unittest CLI with observers."""
    args = sys.argv[1:]
    if args[0] == "event":
        event = args[1]
        fields = {}
        if event == "suite-start":
            fields = {"python": sys.version}
        elif event == "phase":
            fields = {"phase": args[2]}
        elif event == "suite-end":
            fields = {"exit_code": int(args[2]), "phase": args[3]}
            if fields["exit_code"] and fields["phase"] != "unittest":
                emit("first-failure", **fields)
        emit(event, **fields)
        return
    # Match python -m unittest's starting import path and native exit semantics.
    sys.path[0] = os.getcwd()
    unittest.main(module=None, argv=["python -m unittest", *args],
                  testRunner=TimedRunner, testLoader=TimedLoader())


if __name__ == "__main__":
    main()
