"""Verify retry bounds, evidence retention and the final documentation failure gate."""

from contextlib import redirect_stdout
from datetime import datetime, timedelta, timezone
from email.utils import format_datetime
from email.message import Message
import importlib.util
import io
import json
from pathlib import Path
import shlex
import subprocess
import tempfile
import unittest
from unittest.mock import MagicMock, patch
from urllib.error import HTTPError


SPEC = importlib.util.spec_from_file_location(
    "retry_documentation_links", Path(__file__).resolve().parents[1] / "scripts/retry_documentation_links.py"
)
retry = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(retry)
GNU_URL = "https://www.gnu.org/software/coreutils/manual/html_node/env-invocation.html"
GITHUB_SOURCE = "https://github.com/openssh/openssh-portable/blob/V_10_2_P1/ssh.c"


def failure_report(*entries):
    """Format failures as Lychee 0.24.2 writes them in its Markdown report."""
    return f"| 🚫 Errors | {len(entries)} |\n\n" + "".join(
        f"* [{status}] <{url}>\n" for status, url in entries
    )


FIRST_FAILURE = failure_report(("429", GNU_URL))


def github_report(*entries):
    """Produce a reconciled two-link report with the supplied failures."""
    return (f"| Total | 2 |\n| Successful | {2 - len(entries)} |\n| Timeouts | 0 |\n"
            "| Unknown | 0 |\n| Unsupported | 0 |\n| Excluded | 0 |\n" + failure_report(*entries))


GITHUB_503 = github_report(("503", GITHUB_SOURCE))
API_URL = "https://api.github.com/repos/openssh/openssh-portable/contents/ssh.c?ref=V_10_2_P1"
FILE_METADATA = {"type": "file", "path": "ssh.c", "html_url": GITHUB_SOURCE, "sha": "1" * 40}


def api_response(metadata, status=200, endpoint=API_URL):
    """Mock an HTTP context manager, including the effective URL and JSON body."""
    response = MagicMock()
    response.__enter__.return_value = response
    response.status = status
    response.geturl.return_value = endpoint
    response.read.return_value = json.dumps(metadata).encode()
    return response


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
        report = failure_report(("429", GNU_URL), ("429", GNU_URL), ("503", GITHUB_SOURCE))
        self.assertEqual(retry.retryable_failures(report), [GNU_URL])

    def test_manual_timeouts_use_the_separate_lychee_timeout_count(self):
        report = ("| ⏳ Timeouts | 3 |\n| 🚫 Errors | 0 |\n"
                  "* [TIMEOUT] <https://manpages.ubuntu.com/manpages/resolute/man8/apt.8.html>\n"
                  "* [TIMEOUT] <https://manpages.ubuntu.com/manpages/resolute/man1/hp-align.1.html>\n"
                  f"* [TIMEOUT] <{GNU_URL}>\n")
        self.assertEqual(retry.retryable_failures(report), [])
        for invalid in (report.replace("www.gnu.org", "example.org"),
                        report.replace("Timeouts | 3", "Timeouts | 4"),
                        report.replace("Errors | 0", "Errors | 1"),
                        report + f"* [404] <{GNU_URL}>\n"):
            self.assertIsNone(retry.retryable_failures(invalid))
        mixed = report.replace("Errors | 0", "Errors | 1")
        self.assertEqual(retry.retryable_failures(mixed + f"* [429] <{GNU_URL}>\n"), [GNU_URL])

    def test_cached_duplicate_of_a_known_timeout_allows_one_retry(self):
        package = "https://packages.ubuntu.com/noble/yq"
        source = "https://anongit.mindrot.org/openssh.git/tree/scp.c?h=V_9_6_P1#n508"
        report = (f"| Total | 4 |\n| Errors | 2 |\n| Timeouts | 2 |\n"
                  f"* [ERROR] <{source}> (at 97:697) | Error (cached)\n"
                  f"* [503] <{GITHUB_SOURCE}>\n"
                  f"* [TIMEOUT] <{package}>\n* [TIMEOUT] <{source}>\n")
        code, _, _, _, _, _ = self.run_gate(first_report=report, second_report="| Total | 4 |\n")
        self.assertEqual(code, 0)
        code, *_ = self.run_gate(first_report=report, second_code=2, second_report=report)
        self.assertNotEqual(code, 0)
        for invalid in (report.replace("Error (cached)", "Invalid fragment"),
                        report.replace("#n508>", "#n509>", 1),
                        report.replace("anongit.mindrot.org", "other.example")):
            with self.subTest(report=invalid):
                self.assertIsNone(retry.retryable_failures(invalid))

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

    def run_gate(self, *, first_outcome="success", first_exit_code="2", first_report=FIRST_FAILURE,
                 second_code=0, second_report="| Total | 1 |\n", delay=4,
                 timeout=False, version="lychee 0.24.2\n", output=None):
        """Run the controller with isolated reports and capture its CI commands for optional assertions."""
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
                patch.dict(retry.os.environ, {"GITHUB_STEP_SUMMARY": str(directory / "summary.md")}), \
                patch("sys.argv", ["retry_documentation_links.py", "--first-outcome", first_outcome,
                                   "--first-exit-code", first_exit_code]):
            with redirect_stdout(output if output is not None else io.StringIO()):
                code = retry.main()
        return code, first, second, final, run, sleep

    def test_successful_initial_check_has_no_retry_or_delay(self):
        code, first, second, final, run, sleep = self.run_gate(first_exit_code="0", first_report=github_report())
        self.assertEqual(code, 0)
        self.assertEqual(final.read_text(), first.read_text())
        self.assertFalse(second.exists())
        run.assert_not_called()
        sleep.assert_not_called()

    def test_action_output_must_confirm_a_normal_nonempty_check(self):
        for outcome, raw_code, report in (("failure", "0", "| Total | 0 |"), ("failure", "2", GITHUB_503),
                                          ("success", "", GITHUB_503), ("success", "1", GITHUB_503),
                                          ("success", "0", ""), ("skipped", "", None)):
            with self.subTest(outcome=outcome, raw_code=raw_code):
                log = io.StringIO()
                code, _, _, _, run, _ = self.run_gate(first_outcome=outcome, first_exit_code=raw_code,
                                                      first_report=report, output=log)
                self.assertNotEqual(code, 0)
                self.assertIn("::error::", log.getvalue())
                run.assert_not_called()

    def test_initial_503_that_recovers_on_retry_only_warns(self):
        log = io.StringIO()
        code, _, _, final, *_ = self.run_gate(first_report=GITHUB_503, second_report=github_report(), output=log)
        self.assertEqual(code, 0)
        self.assertIn(f"::warning::Initial HTTP 503 for {GITHUB_SOURCE}", log.getvalue())
        self.assertNotIn("::error::", log.getvalue())
        self.assertIn("Passed after retry", final.with_name("summary.md").read_text())

    def test_retry_checks_same_markdown_as_initial_action_and_retains_both_reports(self):
        code, first, second, final, run, sleep = self.run_gate()
        self.assertEqual(code, 0)
        self.assertEqual(first.read_text(), FIRST_FAILURE)
        self.assertEqual(final.read_text(), second.read_text())
        self.assertEqual(run.call_count, 2)  # Version check plus exactly one retry.
        command = run.call_args.args[0]
        inputs = ["**/*.md", ".github/CONTRIBUTING.md", ".github/pull_request_template.md"]
        self.assertEqual(command[command.index("--output") + 2:], inputs)
        workflow = Path(__file__).resolve().parents[1] / ".github/workflows/ci.yml"
        workflow_text = workflow.read_text()
        self.assertIn("          fail: false\n", workflow_text)
        self.assertIn("          jobSummary: false\n", workflow_text)
        self.assertIn("steps.documentation-links.outputs.exit_code", workflow_text)
        action_args = next(line.strip().removeprefix("args: ") for line in workflow_text.splitlines()
                           if line.strip().startswith("args: --config lychee.toml "))
        self.assertEqual(shlex.split(action_args), ["--config", "lychee.toml", "--no-progress", *inputs])
        self.assertIn("lychee.toml", command)  # The successful-response cache remains enabled.
        self.assertEqual([call.args[0] for call in sleep.call_args_list], [10, 60])

    def test_unresolved_retry_fails_without_annotating_the_test_job(self):
        job_log = io.StringIO()
        with redirect_stdout(job_log):
            code, *_ = self.run_gate(first_report=github_report(("503", GITHUB_SOURCE), ("429", GNU_URL)),
                                     second_code=2, second_report=github_report(("429", GNU_URL)))
        self.assertEqual(code, 2)
        self.assertEqual(job_log.getvalue(), "")

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

    def test_mixed_or_incomplete_failures_are_not_retried(self):
        for other in (("ERROR", GNU_URL + "#missing"), ("404", GITHUB_SOURCE),
                      ("503", "https://example.com/path"), ("503", "https://github.com/settings"),
                      ("429", "http://www.gnu.org/"), ("429", "https://other.example/")):
            with self.subTest(other=other):
                report = failure_report(("503", GITHUB_SOURCE), other)
                code, _, _, _, run, sleep = self.run_gate(first_report=report)
                self.assertNotEqual(code, 0)
                run.assert_not_called()
                sleep.assert_not_called()
        self.assertIsNone(retry.retryable_failures(FIRST_FAILURE.replace("Errors | 1", "Errors | 2")))

    def test_github_source_unavailability_gets_one_strict_retry(self):
        report = failure_report(("503", GITHUB_SOURCE))
        for result in (0, 2):
            with self.subTest(result=result):
                code, _, _, _, run, sleep = self.run_gate(first_report=report, second_code=result)
                self.assertEqual(code, result)
                self.assertEqual(run.call_count, 2)
                sleep.assert_called_once_with(60)

    def test_verified_repeated_503_is_one_warning_with_original_reports_retained(self):
        report = github_report(("503", GITHUB_SOURCE), ("503", GITHUB_SOURCE))
        log = io.StringIO()
        with patch.object(retry, "urlopen", return_value=api_response(FILE_METADATA)) as get:
            code, first, second, final, *_ = self.run_gate(first_report=report, second_code=2,
                                                           second_report=report, output=log)
        self.assertEqual(code, 0)
        get.assert_called_once()
        self.assertEqual(get.call_args.args[0].full_url, API_URL)
        self.assertEqual(log.getvalue().count("::warning::"), 1)
        self.assertNotIn("::error::", log.getvalue())
        self.assertNotIn("| 🚫 Errors", final.with_name("summary.md").read_text())
        self.assertEqual(first.read_text(), report)
        self.assertEqual(second.read_text(), report)
        for evidence in (final, final.with_name("summary.md")):
            self.assertIn(f"Warning: HTTP 503 for {GITHUB_SOURCE}", evidence.read_text())
            self.assertIn(FILE_METADATA["sha"], evidence.read_text())

    def test_api_failure_or_mismatched_file_keeps_gate_failed(self):
        failures = [api_response({**FILE_METADATA, field: value}) for field, value in (
            ("type", "dir"), ("path", "other.c"), ("html_url", GITHUB_SOURCE.replace("V_10_2_P1", "main")),
            ("sha", ""), ("submodule_git_url", "git://example.org/submodule"))]
        failures += [api_response([]), api_response(FILE_METADATA, status=203),
                     api_response(FILE_METADATA, endpoint=API_URL.replace("ssh.c", "other.c"))]
        malformed = api_response({})
        malformed.read.return_value = b"invalid JSON"
        failures += [malformed, TimeoutError(), HTTPError(API_URL, 404, "missing ref or path", {}, None),
                     HTTPError(API_URL, 403, "rate limited", {}, None)]
        for failure in failures:
            with self.subTest(failure=failure), patch.object(retry, "urlopen", side_effect=[failure]):
                code, evidence = retry.resolve_github_failures(GITHUB_503, GITHUB_503)
                self.assertEqual(code, 2)
                self.assertIn("Unverified HTTP 503", evidence)

    def test_verified_file_cannot_mask_a_broken_link(self):
        mixed = github_report(("503", GITHUB_SOURCE), ("404", GNU_URL))
        log = io.StringIO()
        with patch.object(retry, "urlopen", return_value=api_response(FILE_METADATA)):
            code, _, _, final, *_ = self.run_gate(first_report=GITHUB_503, second_code=2,
                                                  second_report=mixed, output=log)
        self.assertEqual(code, 2)
        self.assertIn("::error::", log.getvalue())
        self.assertIn("[404]", final.with_name("summary.md").read_text())
        self.assertIn("[404]", final.read_text())
        self.assertIn("Warning: HTTP 503", final.read_text())

    def test_only_repeated_plain_file_urls_from_complete_reports_use_api(self):
        with patch.object(retry, "urlopen") as get:
            for suffix in ("#L10", "?plain=1", "%2Fextra", "/../other"):
                report = github_report(("503", GITHUB_SOURCE + suffix))
                self.assertEqual(retry.resolve_github_failures(report, report), (2, ""))
            for report in (GITHUB_503.replace("Unknown | 0", "Unknown | 1"),
                           GITHUB_503.replace("Errors | 1", "Errors | 2"),
                           GITHUB_503.replace("Total | 2", "Total | 1"),
                           GITHUB_503.replace("Successful | 1", "Successful | 0"),
                           GITHUB_503.replace("| Timeouts | 0 |", ""),
                           GITHUB_503.replace(GITHUB_SOURCE, GITHUB_SOURCE + ".new")):
                self.assertEqual(retry.resolve_github_failures(GITHUB_503, report), (2, ""))
            code, *_ = self.run_gate(first_report=GITHUB_503, second_code=1, second_report=GITHUB_503)
            self.assertEqual(code, 1)
            get.assert_not_called()

    def test_unpinned_version_is_rejected_before_retry(self):
        code, first, second, final, run, sleep = self.run_gate(version="lychee 0.25.0\n")
        self.assertNotEqual(code, 0)
        self.assertEqual(run.call_count, 1)
        sleep.assert_not_called()


if __name__ == "__main__":
    unittest.main()
