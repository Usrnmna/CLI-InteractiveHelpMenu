"""Retry transient documentation failures once and retain both Lychee reports."""

import argparse
import base64
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import hashlib
from http.client import HTTPException
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen


MINIMUM_DELAY_SECONDS = 60
MAXIMUM_DELAY_SECONDS = 120
RETRY_AFTER_MARGIN_SECONDS = 5
HEADER_TIMEOUT_SECONDS = 20
RETRY_TIMEOUT_SECONDS = 180
API_BUDGET_SECONDS = 120
TIMEOUT_HOSTS = {"anongit.mindrot.org", "manpages.ubuntu.com", "packages.ubuntu.com", "www.gnu.org"}
# Keep GNU diagnostics consistent with the GNU-only header in lychee.toml.
GNU_USER_AGENT = "CLI-InteractiveHelpMenu-link-check (+https://github.com/Usrnmna/CLI-InteractiveHelpMenu)"
REPORT_DIRECTORY = Path("tests/reports")
FIRST_REPORT = REPORT_DIRECTORY / "documentation-links-attempt-1.md"
SECOND_REPORT = REPORT_DIRECTORY / "documentation-links-attempt-2.md"
FINAL_REPORT = REPORT_DIRECTORY / "documentation-links.md"


def retry_after_seconds(value, now):
    """Parse Retry-After delta-seconds or an HTTP date; invalid values use fallback."""
    if value is None:
        return None
    value = value.strip()
    if value.isascii() and value.isdigit():
        return int(value)
    try:
        deadline = parsedate_to_datetime(value)
        if deadline.tzinfo is None:
            deadline = deadline.replace(tzinfo=timezone.utc)
        return max(0, math.ceil((deadline - now).total_seconds()))
    except (TypeError, ValueError, OverflowError):
        return None


def reported_failures(report):
    """Read Lychee failure entries only when they account for its error and timeout counts."""
    rows = re.findall(r"^\* \[([^\]\n]+)\] <([^>\n]+)>(.*)$", report, re.MULTILINE)
    entries = [("CACHED_ERROR" if status == "ERROR" and detail.endswith(" | Error (cached)") else status, url)
               for status, url, detail in rows]
    errors = re.search(r"\|[^|\n]*Errors\s*\|\s*(\d+)\s*\|", report)
    timeouts = re.search(r"\|[^|\n]*Timeouts\s*\|\s*(\d+)\s*\|", report)
    timeout_count = sum(status == "TIMEOUT" for status, _ in entries)
    if (not entries or not errors or len(entries) - timeout_count != int(errors.group(1))
            or timeout_count != (int(timeouts.group(1)) if timeouts else 0)):
        return None
    return entries


def retryable_failures(report):
    """Return GNU URLs to probe, or None if any reported failure cannot be retried."""
    entries = reported_failures(report)
    if entries is None:
        return None
    # Lychee can report a repeated occurrence of a timed-out URL as a cached error.
    # Only the live timeout for that exact URL establishes what can be retried.
    timeouts = {url for status, url in entries if status == "TIMEOUT"}
    gnu_urls = []
    for status, url in entries:
        target = urlsplit(url)
        if target.scheme != "https":
            return None
        if status in ("TIMEOUT", "CACHED_ERROR") and url in timeouts and target.netloc in TIMEOUT_HOSTS:
            continue
        if status == "429" and target.netloc == "www.gnu.org":
            if url not in gnu_urls:
                gnu_urls.append(url)
        elif not (status == "503" and target.netloc == "github.com"
                  and re.fullmatch(r"/[^/]+/[^/]+/blob/.+", target.path)):
            return None
    return gnu_urls


def probe_retry_after(url, evidence):
    """Record one GNU GET's headers and return its requested delay on HTTP 429.

    A successful diagnostic request never substitutes for a successful Lychee
    check. Network errors leave the fixed cooldown in effect.
    """
    evidence.write(f"\nURL: {url}\n")
    request = Request(url, headers={"User-Agent": GNU_USER_AGENT})
    try:
        response = urlopen(request, timeout=HEADER_TIMEOUT_SECONDS)
    except HTTPError as error:
        response = error
    except (URLError, TimeoutError, OSError) as error:
        evidence.write(f"Header request failed: {error}\n")
        return None
    with response:
        evidence.write(f"HTTP status: {response.code}\n{response.headers}\n")
        if response.code == 429:
            return retry_after_seconds(response.headers.get("Retry-After"), datetime.now(timezone.utc))
    return None


def retry_delay(delays):
    """Choose a bounded cooldown; refuse to retry earlier than a long server delay."""
    delay = max([MINIMUM_DELAY_SECONDS] + [
        seconds + RETRY_AFTER_MARGIN_SECONDS for seconds in delays if seconds is not None
    ])
    if delay > MAXIMUM_DELAY_SECONDS:
        raise ValueError(f"Retry-After exceeds the {MAXIMUM_DELAY_SECONDS}-second wait budget; no retry performed")
    return delay


def fetch_github_file(match, timeout, token):
    """Return Contents API metadata for the exact repository, revision and file or raise."""
    repo, ref, path = match.groups()
    api_url = f"https://api.github.com/repos/{repo}/contents/{path}?ref={ref}"
    request = Request(api_url, headers={"Accept": "application/vnd.github.object+json",
                                       "User-Agent": "CLI-InteractiveHelpMenu-link-check"})
    if token:
        request.add_unredirected_header("Authorization", f"Bearer {token}")
    with urlopen(request, timeout=timeout) as response:
        if response.status != 200 or response.geturl() != api_url:
            raise ValueError("unexpected API status or redirect")
        metadata = json.load(response)
    if (not isinstance(metadata, dict) or metadata.get("type") != "file"
            or metadata.get("path") != path or metadata.get("html_url") != match.group()
            or metadata.get("submodule_git_url") or not isinstance(metadata.get("sha"), str)
            or not re.fullmatch(r"[0-9a-f]{40}", metadata["sha"])):
        raise ValueError("API metadata did not identify the exact linked file")
    return metadata


def verify_github_lines(metadata, lines):
    """Check a one-based inclusive line range against the complete UTF-8 Git blob."""
    encoded = metadata.get("content")
    if metadata.get("encoding") != "base64" or not isinstance(encoded, str):
        raise ValueError("API response lacks inline file contents")
    content = base64.b64decode(encoded.replace("\n", ""), validate=True)
    header = f"blob {len(content)}\0".encode("ascii")
    if metadata.get("size") != len(content) or hashlib.sha1(header + content).hexdigest() != metadata["sha"]:
        raise ValueError("file contents do not match the reported size and blob SHA")
    text = content.decode("utf-8")
    if "\0" in text:
        raise ValueError("binary file has no verifiable source lines")
    # A final newline terminates a line. It does not create another source line.
    count = text.count("\n") + int(bool(text) and not text.endswith("\n"))
    first, last = lines.groups()
    if not 1 <= int(first) <= int(last or first) <= count:
        raise ValueError(f"cited line range is outside the file's {count} lines or reversed")


def resolve_github_failures(first_report, retry_report, token=None):
    """Resolve repeated blob-page 503s in a complete retry report. Return exit code and evidence."""
    entries = reported_failures(retry_report)
    counts = dict(re.findall(r"^\|[^|\n]*?\b(Total|Successful|Timeouts|Errors|Unknown|Unsupported|Excluded)"
                             r"\s*\|\s*(\d+)\s*\|$", retry_report, re.MULTILINE))
    first_total = re.search(r"^\|[^|\n]*\bTotal\s*\|\s*(\d+)\s*\|$", first_report, re.MULTILINE)
    required = {"Total", "Successful", "Timeouts", "Errors", "Unknown", "Unsupported", "Excluded"}
    if not entries or counts.keys() != required or not first_total or counts["Total"] != first_total[1]:
        return 2, ""
    accounted = int(counts["Successful"]) + int(counts["Excluded"]) + len(entries)
    if int(counts["Unknown"]) or int(counts["Unsupported"]) or int(counts["Total"]) != accounted:
        return 2, ""

    initial = set(reported_failures(first_report) or [])
    unresolved = False
    evidence = []
    files = {}
    deadline = time.monotonic() + API_BUDGET_SECONDS
    for status, url in dict.fromkeys(entries):
        page, separator, fragment = url.partition("#")
        match = re.fullmatch(r"https://github\.com/([\w.-]+/[\w.-]+)/blob/([\w.-]+)/"
                             r"([\w.-]+(?:/[\w.-]+)*)", page, re.ASCII)
        lines = re.fullmatch(r"L([1-9][0-9]*)(?:-L([1-9][0-9]*))?", fragment)
        if (status != "503" or (status, url) not in initial or not match
                or (separator and not lines) or {".", ".."}.intersection(page.split("/"))):
            unresolved = True
            continue
        try:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError("API time budget exhausted")
            if page not in files:
                files[page] = fetch_github_file(match, min(HEADER_TIMEOUT_SECONDS, remaining), token)
            metadata = files[page]
            if lines:
                verify_github_lines(metadata, lines)
        except (OSError, ValueError, HTTPException) as error:
            evidence.append(f"- Unverified HTTP 503: <{url}> ({error})")
            unresolved = True
        else:
            detail = f" and source lines {fragment}" if lines else ""
            message = f"HTTP 503 for {url}. GitHub Contents API verified blob {metadata['sha']}{detail}."
            evidence.append(f"- Warning: {message}")
    if not evidence:
        return 2, ""
    return (2 if unresolved else 0), "\n## GitHub exact-file verification\n\n" + "\n".join(evidence) + "\n"


def finish(first_outcome, lychee="lychee", first_exit_code=None, token=None):
    """Return the final check status after at most one eligible retry.

    A link-failure exit may pass with separate API evidence for every remaining
    failure. Missing reports, version mismatches and process timeouts fail the gate.
    """
    REPORT_DIRECTORY.mkdir(parents=True, exist_ok=True)
    # A report from an earlier local invocation cannot prove this retry succeeded.
    SECOND_REPORT.unlink(missing_ok=True)
    if not FIRST_REPORT.is_file():
        print("Initial Lychee report is missing; failing without a retry.", flush=True)
        return 1
    shutil.copyfile(FIRST_REPORT, FINAL_REPORT)
    first_report = FIRST_REPORT.read_text(encoding="utf-8")
    if first_exit_code is not None:
        # With the action's fail:false, link failures produce outcome=success, exit_code=2.
        # Empty reports and action setup failures can still fail the action itself.
        if first_outcome != "success" or first_exit_code not in ("0", "2"):
            print(f"Initial Lychee action outcome={first_outcome!r}, exit_code={first_exit_code!r}.", flush=True)
            return 1
        first_outcome = "success" if first_exit_code == "0" else "failure"
    if first_outcome == "success":
        return 0 if re.search(r"\|[^|\n]*\bTotal\s*\|\s*[1-9]\d*\s*\|", first_report) else 1
    for status, url in dict.fromkeys(reported_failures(first_report) or []):
        if status == "503" and urlsplit(url).netloc == "github.com":
            # Escape workflow-command data so encoded URL characters stay literal.
            escaped_url = url.replace("%", "%25").replace("\r", "%0D")
            print(f"::warning::Initial HTTP 503 for {escaped_url}.", flush=True)
    urls = retryable_failures(first_report)
    if urls is None:
        print("Initial report contains an ineligible or unidentified failure.", flush=True)
        return 1
    version = subprocess.run([lychee, "--version"], capture_output=True, text=True, timeout=10, check=True)
    if version.stdout.strip() != "lychee 0.24.2":
        raise ValueError(f"Expected lychee 0.24.2, got {version.stdout.strip()!r}")
    delays = []
    delay = MINIMUM_DELAY_SECONDS
    if urls:
        with (REPORT_DIRECTORY / "gnu-response-headers.txt").open("w", encoding="utf-8") as evidence:
            for url in urls[:2]:
                time.sleep(10)
                delays.append(probe_retry_after(url, evidence))
            delay = retry_delay(delays)
            evidence.write(f"\nCooldown before the only retry: {delay} seconds\n")
    print(f"Waiting {delay}s before rechecking documentation links.", flush=True)
    time.sleep(delay)
    command = [lychee, "--config", "lychee.toml", "--no-progress", "--format", "markdown",
               "--output", str(SECOND_REPORT), "**/*.md", ".github/CONTRIBUTING.md", ".github/pull_request_template.md"]
    try:
        with (REPORT_DIRECTORY / "documentation-links-attempt-2.log").open("w", encoding="utf-8") as log:
            result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, timeout=RETRY_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        SECOND_REPORT.write_text("# Retry failed\n\nLychee exceeded the 180-second retry runtime limit.\n", encoding="utf-8")
        shutil.copyfile(SECOND_REPORT, FINAL_REPORT)
        return 1
    appendix = ""
    if not SECOND_REPORT.is_file():
        SECOND_REPORT.write_text("# Retry failed\n\nLychee did not produce a report; inspect the attempt log.\n", encoding="utf-8")
        result_code = 1
    else:
        result_code = result.returncode
        retry_report = SECOND_REPORT.read_text(encoding="utf-8")
        total = re.search(r"\|[^|]*Total\s*\|\s*(\d+)\s*\|", retry_report)
        if not total or int(total.group(1)) == 0:
            print("Retry produced no verifiable link count; failing the check.", flush=True)
            result_code = 1
        elif result_code == 2:
            result_code, appendix = resolve_github_failures(first_report, retry_report, token)
    final_report = SECOND_REPORT.read_text(encoding="utf-8") + appendix
    FINAL_REPORT.write_text(final_report, encoding="utf-8")
    print(final_report, flush=True)
    return result_code


def main():
    """Read the initial action outcome and expose the final failure as an exit code."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--first-outcome", required=True, choices=["success", "failure", "skipped", "cancelled"])
    parser.add_argument("--first-exit-code", help="Raw Lychee exit_code output when the action uses fail:false")
    parser.add_argument("--lychee", default="lychee", help="Pinned Lychee executable")
    args = parser.parse_args()
    try:
        # Keep the workflow credential out of Lychee's inherited environment.
        token = os.environ.pop("DOCS_GITHUB_TOKEN", None)
        code = finish(args.first_outcome, args.lychee, args.first_exit_code, token)
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        print(f"Documentation link gate failed: {error}", flush=True)
        code = 1
    if code:
        print("::error::Documentation link verification failed. See the final report for unresolved links or checker failures.", flush=True)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        details = FINAL_REPORT.read_text(encoding="utf-8") if FINAL_REPORT.is_file() else ""
        verdict = "Failed" if code else "Passed"
        if not code and SECOND_REPORT.is_file():
            verdict = "Passed after retry"
            # Raw Lychee error counts precede exact-file verification in the artifact.
            # Show the resolved outcome on the job summary.
            _, heading, verification = details.partition("## GitHub exact-file verification")
            if heading:
                details = heading + verification
        with Path(summary).open("a", encoding="utf-8") as output:
            output.write(f"\n## Documentation links — {verdict}\n\n{details}")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
