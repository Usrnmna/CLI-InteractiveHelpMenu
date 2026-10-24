"""Verify retry bounds, evidence retention and the final documentation failure gate."""

from datetime import datetime, timedelta, timezone
from email.utils import format_datetime
from email.message import Message
import importlib.util
import io
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError


SPEC = importlib.util.spec_from_file_location(
    "retry_documentation_links", Path(__file__).resolve().parents[1] / "scripts/retry_documentation_links.py"
)
retry = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(retry)
GNU_URL = "https://www.gnu.org/software/coreutils/manual/html_node/env-invocation.html"
FIRST_FAILURE = f"# Summary\n\n* [429] <{GNU_URL}>\n"


class DocumentationRetryTests(unittest.TestCase):
    def test_retry_after_parses_seconds_dates_and_invalid_values(self):
        now = datetime(2026, 10, 24, tzinfo=timezone.utc)
        self.assertEqual(retry.retry_after_seconds("4", now), 4)
        self.assertEqual(retry.retry_after_seconds(format_datetime(now + timedelta(seconds=70)), now), 70)
        self.assertEqual(retry.retry_after_seconds(format_datetime(now - timedelta(seconds=5)), now), 0)
        for value in (None, "invalid", "-4", "nan"):
            with self.subTest(value=value):
                self.assertIsNone(retry.retry_after_seconds(value, now))

    def test_wait_has_margin_and_refuses_excessive_server_delay(self):
        self.assertEqual(retry.retry_delay([None, 4]), 60)
        self.assertEqual(retry.retry_delay([70]), 75)
        self.assertEqual(retry.retry_delay([115]), 120)
        with self.assertRaises(ValueError):
            retry.retry_delay([116])

    def test_only_unique_gnu_https_429_links_are_probed(self):
        report = FIRST_FAILURE * 2 + "\n[404] <https://www.gnu.org/missing>\n[429] <https://other.example/>\n[429] <http://www.gnu.org/>"
        self.assertEqual(retry.gnu_rate_limited_urls(report), [GNU_URL])

    def test_http_429_probe_retains_headers_and_reads_retry_after(self):
        headers = Message()
        headers["Retry-After"] = "70"
        error = HTTPError(GNU_URL, 429, "Too Many Requests", headers, io.BytesIO(b"rate limited"))
        evidence = io.StringIO()
        with patch.object(retry, "urlopen", side_effect=error) as request:
            self.assertEqual(retry.probe_retry_after(GNU_URL, evidence), 70)
        self.assertEqual(
            request.call_args.args[0].get_header("User-agent"),
            "CLI-InteractiveHelpMenu-link-check (+https://github.com/Usrnmna/CLI-InteractiveHelpMenu)",
        )
        self.assertIn("HTTP status: 429", evidence.getvalue())
        self.assertIn("Retry-After: 70", evidence.getvalue())

    def run_gate(self, *, first_outcome="failure", first_report=FIRST_FAILURE,
                 second_code=0, second_report="| Total | 1 |\n", delay=4,
                 timeout=False, version="lychee 0.24.2\n"):
        """Run the real controller with isolated reports and mocked time/processes."""
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        directory = Path(temporary.name)
        first = directory / "first.md"
        second = directory / "second.md"
        final = directory / "final.md"
        if first_report is not None:
            first.write_text(first_report)
        second.write_text("| Total | 999 |\n")  # Old evidence must never mask a missing new report.

        def process(command, **kwargs):
            if "--version" in command:
                return subprocess.CompletedProcess(command, 0, version, "")
            if timeout:
                raise subprocess.TimeoutExpired(command, 180)
            if second_report is not None:
                second.write_text(second_report)
            return subprocess.CompletedProcess(command, second_code)

        with patch.multiple(retry, REPORT_DIRECTORY=directory, FIRST_REPORT=first, SECOND_REPORT=second, FINAL_REPORT=final), \
                patch.object(retry.time, "sleep") as sleep, \
                patch.object(retry, "probe_retry_after", return_value=delay), \
                patch.object(retry.subprocess, "run", side_effect=process) as run, \
                patch.dict(retry.os.environ, {"GITHUB_STEP_SUMMARY": ""}):
            try:
                code = retry.finish(first_outcome)
            except ValueError:
                code = 1
        return code, first, second, final, run, sleep

    def test_successful_initial_check_has_no_retry_or_delay(self):
        code, first, second, final, run, sleep = self.run_gate(first_outcome="success")
        self.assertEqual(code, 0)
        self.assertEqual(final.read_text(), first.read_text())
        self.assertFalse(second.exists())
        run.assert_not_called()
        sleep.assert_not_called()

    def test_retry_checks_full_glob_and_retains_both_reports(self):
        code, first, second, final, run, sleep = self.run_gate()
        self.assertEqual(code, 0)
        self.assertEqual(first.read_text(), FIRST_FAILURE)
        self.assertEqual(final.read_text(), second.read_text())
        self.assertEqual(run.call_count, 2)  # Version check plus exactly one retry.
        command = run.call_args.args[0]
        self.assertIn("**/*.md", command)
        self.assertIn("lychee.toml", command)  # The successful-response cache remains enabled.
        self.assertEqual([call.args[0] for call in sleep.call_args_list], [10, 60])

    def test_unresolved_retry_still_fails(self):
        code, *_ = self.run_gate(second_code=2, second_report="| Total | 1 |\n" + FIRST_FAILURE)
        self.assertEqual(code, 2)

    def test_missing_or_empty_retry_report_cannot_pass(self):
        for report in (None, "| Total | 0 |\n"):
            with self.subTest(report=report):
                code, *_ = self.run_gate(second_report=report)
                self.assertNotEqual(code, 0)

    def test_retry_timeout_preserves_initial_report_and_fails(self):
        code, first, second, final, *_ = self.run_gate(timeout=True)
        self.assertNotEqual(code, 0)
        self.assertEqual(first.read_text(), FIRST_FAILURE)
        self.assertIn("180-second", second.read_text())
        self.assertEqual(final.read_text(), second.read_text())

    def test_excessive_retry_after_prevents_the_second_check(self):
        code, first, second, final, run, sleep = self.run_gate(delay=1000)
        self.assertNotEqual(code, 0)
        self.assertFalse(second.exists())
        self.assertEqual(run.call_count, 1)  # Only the version check.
        self.assertEqual(final.read_text(), first.read_text())

    def test_missing_initial_report_fails_without_retry(self):
        code, first, second, final, run, sleep = self.run_gate(first_report=None)
        self.assertNotEqual(code, 0)
        run.assert_not_called()
        sleep.assert_not_called()

    def test_non_gnu_failure_is_not_retried_or_masked(self):
        code, first, second, final, run, sleep = self.run_gate(first_report="[404] <https://example.com/missing>")
        self.assertNotEqual(code, 0)
        run.assert_not_called()
        sleep.assert_not_called()

    def test_unpinned_version_is_rejected_before_retry(self):
        code, first, second, final, run, sleep = self.run_gate(version="lychee 0.25.0\n")
        self.assertNotEqual(code, 0)
        self.assertEqual(run.call_count, 1)
        sleep.assert_not_called()


if __name__ == "__main__":
    unittest.main()
