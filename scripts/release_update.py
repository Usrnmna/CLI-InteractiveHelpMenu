"""Download verified GitHub releases and upgrade through the managed update workflow."""

import argparse
import gzip
import hashlib
import http.client
import json
import os
from pathlib import Path, PurePosixPath
import platform
import re
import shlex
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request

# Read-only checks must not create bytecode inside an installed runtime.
sys.dont_write_bytecode = True

import installation
from update_review import ReviewSession, display


REPOSITORY = "Usrnmna/CLI-InteractiveHelpMenu"
API = "https://api.github.com/repos/" + REPOSITORY
MAX_METADATA = 4 * 1024 * 1024
MAX_PACKAGE = 64 * 1024 * 1024
MAX_EXPANDED = 128 * 1024 * 1024
MAX_MEMBER = 32 * 1024 * 1024
MAX_MEMBERS = 10000
MAX_PAGES = 10
REQUEST_TIMEOUT = 15
DOWNLOAD_SECONDS = 120
DOWNLOAD_HOSTS = {"api.github.com", "github.com", "release-assets.githubusercontent.com", "objects.githubusercontent.com"}
VERSION_PATTERN = re.compile(r"v?(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
                             r"(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?"
                             r"(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?")


def version_key(value):
    """Return SemVer precedence, ignoring build metadata and rejecting ambiguous versions."""
    match = VERSION_PATTERN.fullmatch(value) if isinstance(value, str) and len(value) <= 100 else None
    if match is None:
        raise ValueError("Expected a semantic version such as v0.1.2 or v0.1.2-alpha.1.")
    major, minor, patch, prerelease, _ = match.groups()
    identifiers = []
    for item in prerelease.split(".") if prerelease else []:
        if item.isdecimal() and len(item) > 1 and item.startswith("0"):
            raise ValueError("Numeric prerelease identifiers cannot have leading zeros.")
        identifiers.append((0, int(item)) if item.isdecimal() else (1, item))
    return int(major), int(minor), int(patch), prerelease is None, tuple(identifiers)


def valid_url(url):
    """Restrict transport and redirect destinations to GitHub's HTTPS download hosts."""
    parsed = urllib.parse.urlsplit(url)
    if (parsed.scheme != "https" or parsed.hostname not in DOWNLOAD_HOSTS or parsed.port not in (None, 443)
            or parsed.username or parsed.password or parsed.fragment
            or any(ord(char) < 32 or ord(char) == 127 for char in url)):
        raise ValueError("Release downloads require an approved GitHub HTTPS URL.")
    return url


class GitHubRedirects(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, response, code, message, headers, new_url):
        """Validate each redirect before urllib can issue the next request."""
        valid_url(new_url)
        return super().redirect_request(request, response, code, message, headers, new_url)


class GitHubClient:
    """Use unauthenticated, bounded HTTPS requests for public release assets."""

    def __init__(self):
        self.opener = urllib.request.build_opener(GitHubRedirects())

    def fetch(self, url, limit):
        """Read a bounded response with TLS validation, timeouts, and redirect checks."""
        request = urllib.request.Request(valid_url(url), headers={
            "Accept": "application/vnd.github+json" if url.startswith(API) else "application/octet-stream",
            "User-Agent": "CLI-InteractiveHelpMenu-updater", "X-GitHub-Api-Version": "2022-11-28"})
        deadline = time.monotonic() + DOWNLOAD_SECONDS
        try:
            with self.opener.open(request, timeout=REQUEST_TIMEOUT) as response:
                valid_url(response.geturl())
                if response.status != 200:
                    raise ValueError("GitHub did not return a complete response.")
                length = response.headers.get("Content-Length")
                if length is not None and (not length.isdecimal() or int(length) > limit):
                    raise ValueError("Download exceeds its size limit or has an invalid length.")
                data = bytearray()
                while True:
                    if time.monotonic() > deadline:
                        raise ValueError("Download exceeded its total time limit.")
                    block = response.read1(min(65536, limit + 1 - len(data)))
                    if not block:
                        break
                    data.extend(block)
                    if len(data) > limit:
                        raise ValueError("Download exceeds its size limit.")
                if length is not None and len(data) != int(length):
                    raise ValueError("Download was truncated.")
                return bytes(data)
        except urllib.error.HTTPError as error:
            if error.code in (403, 429):
                raise ValueError("GitHub denied the request or its public API rate limit was reached; retry later.") from error
            raise ValueError(f"GitHub request failed (HTTP {error.code}).") from error
        except (urllib.error.URLError, TimeoutError, http.client.HTTPException) as error:
            raise ValueError("GitHub connection failed or timed out; no unverified package was applied.") from error

    def metadata(self, url):
        """Decode bounded API metadata without using release descriptions as commands."""
        return json.loads(self.fetch(url, MAX_METADATA))


def select_release(client, prerelease=False, requested=None):
    """Choose the highest eligible SemVer; never rely on publication order."""
    if requested is not None:
        version_key(requested)
        releases = [client.metadata(API + "/releases/tags/" + urllib.parse.quote(requested, safe=""))]
    else:
        releases = []
        for page in range(1, MAX_PAGES + 1):
            batch = client.metadata(API + f"/releases?per_page=100&page={page}")
            if not isinstance(batch, list) or len(batch) > 100:
                raise ValueError("Invalid GitHub release list.")
            releases.extend(batch)
            if len(batch) < 100:
                break
        else:
            raise ValueError("Release listing exceeded its page limit; select an explicit --version tag.")
    eligible = []
    for release in releases:
        if not isinstance(release, dict):
            raise ValueError("Invalid GitHub release metadata.")
        if requested is not None and release.get("tag_name") != requested:
            raise ValueError("GitHub returned a different release tag.")
        if type(release.get("draft")) is not bool or type(release.get("prerelease")) is not bool:
            raise ValueError("Release visibility metadata is missing or invalid.")
        try:
            key = version_key(release.get("tag_name"))
        except ValueError:
            if requested is not None:
                raise
            continue
        if release["draft"] or (not prerelease and (release["prerelease"] or not key[3])):
            continue
        eligible.append((key, release))
    if requested is not None and not eligible:
        raise ValueError("Requested release is a draft or requires --prerelease.")
    return max(eligible, key=lambda item: item[0])[1] if eligible else None


def native_compatible():
    """Use the published x86_64 launcher only on a supported glibc runtime."""
    library, version = platform.libc_ver()
    match = re.fullmatch(r"(\d+)\.(\d+)(?:\.\d+)*", version)
    return (platform.machine() in {"x86_64", "amd64"} and library == "glibc" and match is not None
            and tuple(map(int, match.groups())) >= (2, 34))


def select_assets(release, source=False):
    """Select a compatible archive and a mandatory matching checksum asset."""
    tag = release["tag_name"]
    version_key(tag)
    version = tag.removeprefix("v")
    base = "cli-interactive-help-v" + version
    assets = release.get("assets")
    if not isinstance(assets, list):
        raise ValueError("Release has no asset list.")
    by_name = {}
    for asset in assets:
        if not isinstance(asset, dict) or not isinstance(asset.get("name"), str) or asset["name"] in by_name:
            raise ValueError("Invalid or duplicate release assets.")
        by_name[asset["name"]] = asset
    native = base + "-linux-x86_64.tar.gz"
    name = native if not source and native_compatible() and native in by_name else base + "-source.tar.gz"
    if name not in by_name:
        raise ValueError("Release has no compatible runtime/source archive.")
    checksum_name = name + ".checksum"
    if checksum_name not in by_name:
        checksum_name = "SHA256SUMS.checksum"
    if checksum_name not in by_name:
        raise ValueError("Release is missing the required checksum asset.")
    selected = [by_name[name], by_name[checksum_name]]
    for asset, limit in zip(selected, (MAX_PACKAGE, 65536)):
        expected_url = ("https://github.com/" + REPOSITORY + "/releases/download/"
                        + urllib.parse.quote(tag, safe="") + "/" + urllib.parse.quote(asset["name"], safe=""))
        if (asset.get("browser_download_url") != expected_url or asset.get("state") != "uploaded"
                or type(asset.get("size")) is not int or not 0 < asset["size"] <= limit):
            raise ValueError("Release asset URL, upload state, or size is invalid.")
        digest = asset.get("digest")
        if digest is not None and (not isinstance(digest, str) or not re.fullmatch(r"sha256:[a-fA-F0-9]{64}", digest)):
            raise ValueError("Unsupported or invalid GitHub asset digest.")
    return selected


def download_asset(client, asset, limit):
    """Verify the API size and its SHA-256 digest when GitHub supplies one."""
    data = client.fetch(asset["browser_download_url"], limit)
    if len(data) != asset["size"]:
        raise ValueError("Release asset size does not match GitHub metadata.")
    if asset.get("digest") and "sha256:" + hashlib.sha256(data).hexdigest() != asset["digest"].lower():
        raise ValueError("Release asset does not match GitHub's SHA-256 digest.")
    return data


def download_package(client, package, checksum):
    """Require exactly one checksum entry for the selected package before extraction."""
    text = download_asset(client, checksum, 65536).decode("utf-8")
    entries = {}
    for line in text.splitlines():
        match = re.fullmatch(r"([0-9A-Fa-f]{64}) [ *]([^\r\n]+)", line)
        if not match or match[2] in entries:
            raise ValueError("Invalid or duplicate checksum entries.")
        entries[match[2]] = match[1].lower()
    if package["name"] not in entries:
        raise ValueError("Checksum file does not identify the selected package.")
    data = download_asset(client, package, MAX_PACKAGE)
    if hashlib.sha256(data).hexdigest() != entries[package["name"]]:
        raise ValueError("Package SHA-256 verification failed; installation was not changed.")
    return data


def extract_package(archive, destination, version):
    """Expand a verified archive into a private directory without links or special files.

    Bound decompression before tar parsing, including metadata and padding, then
    copy regular members explicitly. Archive modes never retain special bits.
    """
    top = "cli-interactive-help-v" + version
    expanded = destination / "expanded.tar"
    total = 0
    with gzip.open(archive, "rb") as compressed, expanded.open("xb") as output:
        while True:
            data = compressed.read(min(65536, MAX_EXPANDED + 1 - total))
            if not data:
                break
            total += len(data)
            if total > MAX_EXPANDED:
                raise ValueError("Expanded release exceeds its size limit.")
            output.write(data)
    seen = set()
    with tarfile.open(expanded, "r:") as bundle:
        for member in bundle:
            name = member.name
            path = PurePosixPath(name)
            if (len(seen) >= MAX_MEMBERS or len(name) > 1024 or str(path) in seen or "\\" in name
                    or any(ord(char) < 32 or ord(char) == 127 for char in name)
                    or path.is_absolute() or ".." in path.parts or not path.parts or path.parts[0] != top
                    or str(path) != name.rstrip("/") or not (member.isfile() or member.isdir())
                    or member.issparse() or member.size < 0 or member.size > MAX_MEMBER
                    or (name.endswith("/") and not member.isdir())
                    or (len(path.parts) == 1 and not member.isdir())):
                raise ValueError("Unsafe, duplicate, or oversized release archive member.")
            seen.add(str(path))
            target = destination.joinpath(*path.parts)
            if member.isdir():
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                with bundle.extractfile(member) as source, target.open("xb") as output:
                    shutil.copyfileobj(source, output, 65536)
                target.chmod(0o755 if member.mode & 0o111 else 0o644)
    expanded.unlink()
    runtime = destination / top
    version_file = runtime / "VERSION"
    if not version_file.is_file() or version_file.stat().st_size > 256 or version_file.read_text().strip() != version:
        raise ValueError("Package VERSION does not match the selected release.")
    for name in ("scripts/installation.py", "scripts/update_review.py", "scripts/guided_merge.py", "update.sh", "review-update.sh"):
        if not (runtime / name).is_file():
            raise ValueError("Release is missing a required update/review component.")
    return runtime


def installed_version(prefix):
    """Read a managed, unmodified version marker before considering an upgrade."""
    manifest = installation.load_manifest(prefix)
    path = installation.safe_path(prefix / "VERSION")
    if not path.is_file() or path.stat().st_size > 256:
        raise ValueError("Installation has no usable VERSION marker; update from a source checkout first.")
    data = path.read_bytes()
    if installation.digest(data) != manifest["files"].get("VERSION"):
        raise ValueError("Installed VERSION was edited; inspect it or update from a source checkout.")
    value = data.decode("utf-8").strip()
    version_key(value)
    return value


def run_update(prefix, client, *, check=False, prerelease=False, requested=None, source=False, no_review=False):
    """Apply a verified incoming updater, retaining its source for conflict recovery."""
    current = installed_version(prefix)
    release = select_release(client, prerelease, requested)
    if release is None:
        print("No eligible published release; use --prerelease to include alpha/beta releases.")
        return 0
    tag = release["tag_name"]
    if version_key(tag) <= version_key(current):
        print(f"Already at {current} or newer than eligible release {tag}; no update applied.")
        return 0
    package, checksum = select_assets(release, source)
    print(f"Installed: {current}; available: {tag}; package: {package['name']}", flush=True)
    if check:
        return 0
    data = download_package(client, package, checksum)
    stage = Path(tempfile.mkdtemp(prefix=prefix.name + ".release-update-", dir=prefix.parent))
    retain = False
    try:
        archive = stage / package["name"]
        archive.write_bytes(data)
        runtime = extract_package(archive, stage, tag.removeprefix("v"))
        # Recheck the managed version after network I/O and before the incoming
        # updater acquires the existing installation lock and stages local edits.
        if installed_version(prefix) != current:
            raise ValueError("Installed version changed during download; retry the update.")
        environment = {key: value for key, value in os.environ.items()
                       if not key.startswith("CLI_HELP_") and key not in {"BASH_ENV", "ENV", "PYTHONPATH", "PYTHONHOME"}}
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        result_file = stage / "update-result.json"
        retain = True  # A failed or interrupted updater may already have created recovery files.
        process = subprocess.run([sys.executable, str(runtime / "scripts/installation.py"), "update",
                                  "--prefix", str(prefix), "--result-file", str(result_file),
                                  "--expected-version", current], env=environment)
        if process.returncode in (130, -2):
            return 130
        if process.returncode not in (0, 2):
            raise ValueError("Incoming updater failed; inspect the retained source and any printed backup path.")
        if not result_file.is_file() or result_file.stat().st_size > 65536:
            raise ValueError("Incoming updater did not produce a valid completion report.")
        result = json.loads(result_file.read_text())
        if (not isinstance(result, dict) or result.get("schema_version") != 1
                or type(result.get("status")) is not int or result["status"] != process.returncode):
            raise ValueError("Incoming updater completion status does not match its exit status.")
        if process.returncode == 0:
            retain = False
            return 0
        if not isinstance(result.get("report"), str):
            raise ValueError("Incoming updater omitted its conflict report path.")
        report = installation.safe_path(result["report"])
        session = ReviewSession(report)
        if session.prefix != prefix:
            raise ValueError("Incoming updater report belongs to another installation.")
        command = [sys.executable, str(runtime / "scripts/update_review.py"), str(report)]
        print("Resume guided conflict review: " + shlex.join(command), flush=True)
        if no_review or not (sys.stdin.isatty() and sys.stdout.isatty()):
            print("Conflicts preserved. Run the review command in a terminal; choose g for guided changes.")
            return 2
        print("Opening conflict review. Select an entry, then g for guided changes.", flush=True)
        review = subprocess.run(command, env=environment)
        if review.returncode != 0:
            return 130 if review.returncode == 130 else 2
        session = ReviewSession(report)
        return 0 if all(session.status(name).startswith("saved ") for name in session.records) else 2
    finally:
        if retain:
            print("Retained verified release source: " + display(stage), flush=True)
        else:
            shutil.rmtree(stage)


def main(argv=None):
    """Expose release checks and explicit upgrades without changing Bash configuration."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prefix", help="Managed installation (defaults to this installed runtime or XDG data directory)")
    parser.add_argument("--check", action="store_true", help="Report an eligible update without downloading or applying it")
    parser.add_argument("--prerelease", action="store_true", help="Include alpha, beta, and other prereleases")
    parser.add_argument("--version", help="Select an exact GitHub release tag; downgrades and reinstalls are refused")
    parser.add_argument("--source", action="store_true", help="Use the architecture-independent source archive")
    parser.add_argument("--no-review", action="store_true", help="Retain conflicts and print a review command without opening it")
    args = parser.parse_args(argv)
    try:
        if sys.version_info < (3, 10) or not sys.platform.startswith("linux"):
            raise ValueError("Release updating requires Linux and Python 3.10 or newer.")
        data = Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local/share")
        default = installation.ROOT if (installation.ROOT / installation.MARKER).exists() else data / installation.APPLICATION
        if not args.prefix and not default.is_absolute():
            raise ValueError("XDG_DATA_HOME must be absolute.")
        prefix = installation.safe_path(args.prefix or default)
        return run_update(prefix, GitHubClient(), check=args.check, prerelease=args.prerelease,
                          requested=args.version, source=args.source, no_review=args.no_review)
    except KeyboardInterrupt:
        print("\nRelease update interrupted; inspect any printed recovery paths.", file=sys.stderr)
        return 130
    except (OSError, ValueError, EOFError, tarfile.TarError, RecursionError) as error:
        print("Release update: " + display(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
