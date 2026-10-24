"""Apply one bounded GNU rate-limit retry and retain both Lychee reports.

The initial action remains strict but defers the job result to this gate. Only
GNU HTTP 429 failures qualify for a retry; the retry checks every link again,
reusing successful responses through the normal Lychee cache configuration.
"""

import argparse
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
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


def gnu_rate_limited_urls(report):
    """Extract unique GNU HTTPS targets from Lychee's Markdown 429 entries."""
    urls = []
    for url in re.findall(r"\[429\]\s+<([^>]+)>", report):
        parsed = urlsplit(url)
        if (parsed.scheme == "https" and parsed.netloc == "www.gnu.org"
                and url not in urls):
            urls.append(url)
    return urls


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


def finish(first_outcome, lychee="lychee"):
    """Return the final check status, retrying at most once after a GNU 429.

    Reports are never used as success evidence without the corresponding process
    success. Missing reports, version mismatches and timeouts fail this gate.
    """
    REPORT_DIRECTORY.mkdir(parents=True, exist_ok=True)
    # A report from an earlier local invocation cannot prove this retry succeeded.
    SECOND_REPORT.unlink(missing_ok=True)
    if not FIRST_REPORT.is_file():
        print("Initial Lychee report is missing; failing without a retry.", flush=True)
        return 1
    shutil.copyfile(FIRST_REPORT, FINAL_REPORT)
    if first_outcome == "success":
        return 0
    urls = gnu_rate_limited_urls(FIRST_REPORT.read_text(encoding="utf-8"))
    if not urls:
        print("Initial failure has no GNU HTTP 429; failing without a retry.", flush=True)
        return 1
    version = subprocess.run([lychee, "--version"], capture_output=True, text=True, timeout=10, check=True)
    if version.stdout.strip() != "lychee 0.24.2":
        raise ValueError(f"Expected lychee 0.24.2, got {version.stdout.strip()!r}")
    with (REPORT_DIRECTORY / "gnu-response-headers.txt").open("w", encoding="utf-8") as evidence:
        # At most two diagnostic requests; additional failures remain in the report.
        delays = []
        for url in urls[:2]:
            time.sleep(10)
            delays.append(probe_retry_after(url, evidence))
        delay = retry_delay(delays)
        evidence.write(f"\nCooldown before the only retry: {delay} seconds\n")
    print(f"GNU rate limited the initial check. Waiting {delay}s before the only retry.", flush=True)
    time.sleep(delay)
    command = [lychee, "--config", "lychee.toml", "--no-progress", "--format", "markdown",
               "--output", str(SECOND_REPORT), "**/*.md"]
    try:
        with (REPORT_DIRECTORY / "documentation-links-attempt-2.log").open("w", encoding="utf-8") as log:
            result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, timeout=RETRY_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        SECOND_REPORT.write_text("# Retry failed\n\nLychee exceeded the 180-second retry runtime limit.\n", encoding="utf-8")
        shutil.copyfile(SECOND_REPORT, FINAL_REPORT)
        return 1
    if not SECOND_REPORT.is_file():
        SECOND_REPORT.write_text("# Retry failed\n\nLychee did not produce a report; inspect the attempt log.\n", encoding="utf-8")
        result_code = 1
    else:
        result_code = result.returncode
        total = re.search(r"\|[^|]*Total\s*\|\s*(\d+)\s*\|", SECOND_REPORT.read_text(encoding="utf-8"))
        if not total or int(total.group(1)) == 0:
            print("Retry produced no verifiable link count; failing the check.", flush=True)
            result_code = 1
    shutil.copyfile(SECOND_REPORT, FINAL_REPORT)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with Path(summary).open("a", encoding="utf-8") as output:
            output.write("\n## Documentation links: final retry\n\n" + SECOND_REPORT.read_text(encoding="utf-8"))
    print(SECOND_REPORT.read_text(encoding="utf-8"), flush=True)
    return result_code


def main():
    """Read the initial action outcome and expose the final failure as an exit code."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--first-outcome", required=True, choices=["success", "failure"])
    parser.add_argument("--lychee", default="lychee", help="Pinned Lychee executable")
    args = parser.parse_args()
    try:
        return finish(args.first_outcome, args.lychee)
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        print(f"Documentation link gate failed: {error}", flush=True)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
