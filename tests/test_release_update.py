"""Exercise release selection, hostile downloads, managed upgrades, and terminal review."""

import contextlib
import copy
import gzip
import hashlib
import http.client
import io
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch
import urllib.error
import urllib.request

from test_bash_pty import BashSession
from test_discovery import ROOT

sys.path.insert(0, str(ROOT / "scripts"))
import build_release
import installation
import release_update as updater
import update_review


def asset(name, data, tag="v0.1.2"):
    return {"name": name, "size": len(data), "state": "uploaded",
            "digest": "sha256:" + hashlib.sha256(data).hexdigest(),
            "browser_download_url": "https://github.com/" + updater.REPOSITORY + "/releases/download/" + tag + "/" + name}


def release(tag="v0.1.2", assets=None, **values):
    return {"tag_name": tag, "prerelease": "-" in tag, "draft": False, "assets": assets or [], **values}


def package_release(data=b"archive", tag="v0.1.2", native=False):
    name = "cli-interactive-help-" + tag + ("-linux-x86_64.tar.gz" if native else "-source.tar.gz")
    checksum = (hashlib.sha256(data).hexdigest() + "  " + name + "\n").encode()
    archive_asset = asset(name, data, tag)
    checksum_asset = asset(name + ".checksum", checksum, tag)
    return release(tag, [archive_asset, checksum_asset]), {
        archive_asset["browser_download_url"]: data, checksum_asset["browser_download_url"]: checksum}


class FakeClient:
    """Represent GitHub responses without making any network requests."""

    def __init__(self, releases, blobs=None):
        self.releases = releases
        self.blobs = blobs or {}
        self.calls = []

    def metadata(self, url):
        self.calls.append(url)
        if "/tags/" in url:
            return self.releases[0]
        page = int(url.rsplit("=", 1)[1])
        return self.releases[(page - 1) * 100:page * 100]

    def fetch(self, url, limit):
        self.calls.append(url)
        return self.blobs[url]


class ReleaseSelectionTests(unittest.TestCase):
    def test_semver_order_numeric_prereleases_and_metadata(self):
        ordered = ["v1.0.0-alpha", "1.0.0-alpha.2", "1.0.0-alpha.10", "1.0.0-beta", "1.0.0-rc.1", "1.0.0", "1.0.1", "1.10.0", "2.0.0"]
        self.assertEqual(sorted(reversed(ordered), key=updater.version_key), ordered)
        self.assertEqual(updater.version_key("1.0.0+build.7"), updater.version_key("v1.0.0+other"))

    def test_invalid_versions_and_shell_syntax_are_rejected(self):
        for value in [None, 1, "", "1.2", "01.2.3", "1.2.3-alpha.01", "1.2.3;touch x", "$(id)", "1.2.3\n", "v" * 101]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                updater.version_key(value)

    def test_stable_default_ignores_prereleases_drafts_and_publication_order(self):
        client = FakeClient([release("v5.0.0", draft=True), release("v3.0.0-beta"), release("v1.10.0"), release("v1.9.0"), release("snapshot")])
        self.assertEqual(updater.select_release(client)["tag_name"], "v1.10.0")
        self.assertEqual(updater.select_release(client, prerelease=True)["tag_name"], "v3.0.0-beta")

    def test_tag_prerelease_cannot_bypass_channel_with_false_api_flag(self):
        self.assertIsNone(updater.select_release(FakeClient([release("v9.0.0-alpha", prerelease=False)])))

    def test_exact_tag_requires_prerelease_opt_in_and_matching_response(self):
        client = FakeClient([release("v1.2.0-alpha")])
        with self.assertRaises(ValueError):
            updater.select_release(client, requested="")
        self.assertFalse(client.calls)
        with self.assertRaisesRegex(ValueError, "requires --prerelease"):
            updater.select_release(client, requested="v1.2.0-alpha")
        self.assertEqual(updater.select_release(client, True, "v1.2.0-alpha")["tag_name"], "v1.2.0-alpha")
        with self.assertRaisesRegex(ValueError, "different release"):
            updater.select_release(client, requested="v1.3.0")

    def test_pagination_and_page_limit_fail_closed(self):
        client = FakeClient([release("snapshot")] * 100 + [release("v2.0.0")])
        self.assertEqual(updater.select_release(client)["tag_name"], "v2.0.0")
        self.assertEqual(len(client.calls), 2)
        with patch.object(updater, "MAX_PAGES", 1), self.assertRaisesRegex(ValueError, "page limit"):
            updater.select_release(client)

    def test_malformed_metadata_and_visibility_fail(self):
        for value in [None, [], {"tag_name": "v1.2.3"}, release(draft=0), release(prerelease="false")]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                updater.select_release(FakeClient([value]))
        with patch.object(FakeClient, "metadata", return_value={}), self.assertRaises(ValueError):
            updater.select_release(FakeClient([]))

    def test_native_selection_and_source_fallback(self):
        source, _ = package_release()
        native, _ = package_release(native=True)
        combined = release(assets=source["assets"] + native["assets"])
        with patch.object(updater, "native_compatible", return_value=True):
            self.assertIn("linux-x86_64", updater.select_assets(combined)[0]["name"])
            self.assertIn("source", updater.select_assets(combined, source=True)[0]["name"])
            self.assertIn("source", updater.select_assets(source)[0]["name"])
        with patch.object(updater, "native_compatible", return_value=False):
            self.assertIn("source", updater.select_assets(combined)[0]["name"])
            with self.assertRaisesRegex(ValueError, "compatible"):
                updater.select_assets(native)

    def test_native_libc_and_architecture_boundaries(self):
        for machine, libc, expected in [("x86_64", ("glibc", "2.34"), True), ("x86_64", ("glibc", "2.33"), False),
                                        ("aarch64", ("glibc", "2.39"), False), ("x86_64", ("musl", "1.2"), False),
                                        ("x86_64", ("", ""), False)]:
            with self.subTest(machine=machine, libc=libc), patch.object(updater.platform, "machine", return_value=machine), patch.object(updater.platform, "libc_ver", return_value=libc):
                self.assertEqual(updater.native_compatible(), expected)

    def test_missing_duplicate_and_untrusted_assets_fail(self):
        original, _ = package_release()
        for change in [lambda r: r.update(assets=[]), lambda r: r["assets"].pop(),
                       lambda r: r["assets"].append(r["assets"][0]),
                       lambda r: r["assets"][0].update(browser_download_url="https://evil.example/package"),
                       lambda r: r["assets"][0].update(size=True), lambda r: r["assets"][0].update(size=updater.MAX_PACKAGE + 1),
                       lambda r: r["assets"][0].update(state="new"), lambda r: r["assets"][0].update(digest="md5:abcd")]:
            value = copy.deepcopy(original)
            change(value)
            with self.subTest(value=value), self.assertRaises(ValueError):
                updater.select_assets(value, source=True)

    def test_aggregate_checksums_are_supported(self):
        value, _ = package_release()
        value["assets"][1] = asset("SHA256SUMS.checksum", b"checksums")
        self.assertEqual(updater.select_assets(value, source=True)[1]["name"], "SHA256SUMS.checksum")


class Response(io.BytesIO):
    def __init__(self, data, length=None, url="https://api.github.com/test", status=200):
        super().__init__(data)
        self.headers = {} if length is None else {"Content-Length": length}
        self.url = url
        self.status = status

    def geturl(self):
        return self.url


class ReleaseDownloadTests(unittest.TestCase):
    def fetch(self, response, limit=32):
        client = updater.GitHubClient()
        with patch.object(client.opener, "open", return_value=response) as opened:
            data = client.fetch("https://api.github.com/test", limit)
            self.assertEqual(opened.call_args.kwargs["timeout"], updater.REQUEST_TIMEOUT)
            self.assertIsNone(opened.call_args.args[0].get_header("Authorization"))
            return data

    def test_bounded_transport_accepts_exact_limit_and_missing_length(self):
        self.assertEqual(self.fetch(Response(b"x" * 32, "32")), b"x" * 32)
        self.assertEqual(self.fetch(Response(b"hello")), b"hello")

    def test_transport_rejects_oversize_truncation_bad_lengths_and_partial_status(self):
        for response in [Response(b"x" * 33), Response(b"", "33"), Response(b"abc", "4"), Response(b"", "-1"), Response(b"", "bad"), Response(b"x", status=206)]:
            with self.subTest(response=response), self.assertRaises(ValueError):
                self.fetch(response)

    def test_timeout_deadline_and_network_errors(self):
        with patch.object(updater.time, "monotonic", side_effect=[0, 121]), self.assertRaisesRegex(ValueError, "total time"):
            self.fetch(Response(b"hello"))
        client = updater.GitHubClient()
        for error in [TimeoutError(), urllib.error.URLError("unavailable"),
                      http.client.IncompleteRead(b"partial", 10),
                      urllib.error.HTTPError("url", 403, "rate limit", {}, None),
                      urllib.error.HTTPError("url", 404, "absent", {}, None)]:
            with self.subTest(error=error), patch.object(client.opener, "open", side_effect=error), self.assertRaises(ValueError):
                client.fetch("https://api.github.com/test", 32)

    def test_tls_redirect_destinations_are_restricted(self):
        urls = ["http://github.com/file", "file:///etc/passwd", "https://github.com.evil.test/x", "https://user@github.com/x",
                "https://github.com:8443/x", "https://github.com/x#fragment", "https://github.com/\nx", "https://127.0.0.1/x"]
        request = urllib.request.Request("https://github.com/test")
        for url in urls:
            with self.subTest(url=url), self.assertRaises(ValueError):
                updater.GitHubRedirects().redirect_request(request, None, 302, "redirect", {}, url)
        redirected = updater.GitHubRedirects().redirect_request(request, None, 302, "redirect", {}, "https://release-assets.githubusercontent.com/file?signature=value")
        self.assertEqual(redirected.host, "release-assets.githubusercontent.com")
        with self.assertRaises(ValueError):
            self.fetch(Response(b"", url="https://evil.example/file"))

    def test_checksum_and_api_digests_verified(self):
        value, blobs = package_release(b"verified")
        self.assertEqual(updater.download_package(FakeClient([], blobs), *value["assets"]), b"verified")
        for item in value["assets"]:
            item.pop("digest")
        self.assertEqual(updater.download_package(FakeClient([], blobs), *value["assets"]), b"verified")

    def test_corrupt_package_api_size_and_digest_fail(self):
        for field, bad in [("size", 100), ("digest", "sha256:" + "0" * 64)]:
            value, blobs = package_release()
            value["assets"][0][field] = bad
            with self.subTest(field=field), self.assertRaises(ValueError):
                updater.download_package(FakeClient([], blobs), *value["assets"])
        value, blobs = package_release()
        value["assets"][0].pop("digest")
        blobs[value["assets"][0]["browser_download_url"]] = b"changed"
        with self.assertRaisesRegex(ValueError, "SHA-256"):
            updater.download_package(FakeClient([], blobs), *value["assets"])

    def test_malformed_duplicate_missing_and_wrong_checksum_fail_before_archive_download(self):
        value, blobs = package_release()
        name = value["assets"][0]["name"]
        for content in [b"", b"bad\n", b"\xff", ("0" * 64 + "  other\n").encode(),
                        (("0" * 64 + "  " + name + "\n") * 2).encode()]:
            checksum = asset(name + ".checksum", content)
            client = FakeClient([], {checksum["browser_download_url"]: content})
            with self.subTest(content=content), self.assertRaises(ValueError):
                updater.download_package(client, value["assets"][0], checksum)
            self.assertEqual(len(client.calls), 1)

    def test_corrupt_checksum_asset_is_rejected(self):
        value, blobs = package_release()
        checksum = value["assets"][1]
        blobs[checksum["browser_download_url"]] = b"x" * checksum["size"]
        with self.assertRaisesRegex(ValueError, "GitHub's SHA-256"):
            updater.download_package(FakeClient([], blobs), *value["assets"])


class ReleaseArchiveTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.folder = Path(self.temporary.name)
        self.top = "cli-interactive-help-v0.1.2"
        self.files = {"VERSION": b"0.1.2\n", "scripts/installation.py": b"", "scripts/update_review.py": b"",
                      "scripts/guided_merge.py": b"", "update.sh": b"", "review-update.sh": b""}

    def extract(self, data):
        target = self.folder / ("case-" + str(len(list(self.folder.iterdir()))))
        target.mkdir()
        archive = target / "package.tar.gz"
        archive.write_bytes(data)
        return updater.extract_package(archive, target, "0.1.2")

    def special(self, name, kind=tarfile.REGTYPE, data=b"x", link="outside"):
        result = io.BytesIO()
        with tarfile.open(fileobj=result, mode="w:gz") as bundle:
            item = tarfile.TarInfo(name)
            item.type = kind
            item.linkname = link
            item.size = len(data) if kind == tarfile.REGTYPE else 0
            bundle.addfile(item, io.BytesIO(data))
        return result.getvalue()

    def test_valid_archive_preserves_bytes_and_normalizes_permissions(self):
        self.files["profiles/utf8.json"] = 'é\r\n'.encode()
        runtime = self.extract(build_release.archive(self.files, self.top))
        self.assertEqual((runtime / "profiles/utf8.json").read_bytes(), 'é\r\n'.encode())
        self.assertEqual((runtime / "update.sh").stat().st_mode & 0o777, 0o755)

    def test_paths_links_devices_and_fifos_are_rejected(self):
        for name in ["/outside", "../outside", self.top + "/../outside", self.top + "/a/../../outside",
                     self.top + "/./bad", self.top + "/a\\b", "wrong/VERSION", self.top + "/bad\x1b"]:
            with self.subTest(name=name), self.assertRaises(ValueError):
                self.extract(self.special(name))
        for kind in [tarfile.SYMTYPE, tarfile.LNKTYPE, tarfile.FIFOTYPE, tarfile.CHRTYPE, tarfile.BLKTYPE]:
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                self.extract(self.special(self.top + "/bad", kind))
        self.assertFalse((self.folder / "outside").exists())

    def test_duplicate_members_and_file_directory_collision_fail(self):
        for names in [[self.top + "/same"] * 2, [self.top + "/file", self.top + "/file/child"]]:
            data = io.BytesIO()
            with tarfile.open(fileobj=data, mode="w:gz") as bundle:
                for name in names:
                    item = tarfile.TarInfo(name)
                    item.size = 1
                    bundle.addfile(item, io.BytesIO(b"x"))
            with self.subTest(names=names), self.assertRaises((ValueError, OSError)):
                self.extract(data.getvalue())

    def test_expansion_member_and_count_limits(self):
        archive = build_release.archive(self.files, self.top)
        for field, limit in [("MAX_EXPANDED", 1024), ("MAX_MEMBER", 2), ("MAX_MEMBERS", 2)]:
            with self.subTest(field=field), patch.object(updater, field, limit), self.assertRaises(ValueError):
                self.extract(archive)

    def test_malformed_truncated_and_mismatched_version_fail(self):
        archive = build_release.archive(self.files, self.top)
        for data in [b"not gzip", archive[:20], gzip.compress(b"not tar")]:
            with self.subTest(data=data[:20]), self.assertRaises((ValueError, OSError, EOFError, tarfile.TarError)):
                self.extract(data)
        self.files["VERSION"] = b"99.0.0\n"
        with self.assertRaisesRegex(ValueError, "VERSION"):
            self.extract(build_release.archive(self.files, self.top))

    def test_missing_components_and_special_permission_bits(self):
        self.files.pop("scripts/update_review.py")
        with self.assertRaisesRegex(ValueError, "required"):
            self.extract(build_release.archive(self.files, self.top))
        data = io.BytesIO()
        self.files["scripts/update_review.py"] = b""
        with tarfile.open(fileobj=data, mode="w:gz") as bundle:
            for name, content in self.files.items():
                item = tarfile.TarInfo(self.top + "/" + name)
                item.mode = 0o6755
                item.size = len(content)
                bundle.addfile(item, io.BytesIO(content))
        runtime = self.extract(data.getvalue())
        self.assertEqual((runtime / "VERSION").stat().st_mode & 0o7777, 0o755)


class ReleaseUpdateTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.home = Path(self.temporary.name)
        self.prefix = self.home / "app's $(touch NEVER); runtime"
        self.rc = self.home / "bashrc"
        self.environment = {key: value for key, value in os.environ.items()
                            if not key.startswith("CLI_HELP_") and key not in {"BASH_ENV", "ENV", "PYTHONPATH", "PYTHONHOME"}}
        self.environment.update(HOME=str(self.home), PYTHONDONTWRITEBYTECODE="1", CLI_HELP_PYTHON=sys.executable)
        subprocess.run(["bash", str(ROOT / "install.sh"), "--prefix", str(self.prefix), "--rc-file", str(self.rc)],
                       env=self.environment, capture_output=True, check=True)
        self.current = (self.prefix / "VERSION").read_text().strip()
        self.files = {}
        for pattern in installation.PAYLOAD:
            for path in ROOT.glob(pattern):
                self.files[path.relative_to(ROOT).as_posix()] = path.read_bytes()
        self.files["VERSION"] = b"0.1.2\n"
        self.files["cli_help/release_fixture.py"] = b"# incoming first\n# stable\n# incoming last\n"

    def client(self):
        data = build_release.archive(self.files, "cli-interactive-help-v0.1.2")
        value, blobs = package_release(data)
        return FakeClient([value], blobs)

    def run_update(self, client=None, **options):
        with patch.dict(os.environ, self.environment, clear=True), contextlib.redirect_stdout(io.StringIO()) as output:
            status = updater.run_update(self.prefix, client or self.client(), source=True, **options)
        return status, output.getvalue()

    def stages(self):
        return list(self.home.glob(self.prefix.name + ".release-update-*"))

    def reports(self):
        return list(self.home.glob(self.prefix.name + ".update-backup-*/report.json"))

    def test_verified_update_backup_settings_and_cleanup(self):
        local = self.prefix / "custom/settings.json"
        local.parent.mkdir()
        local.write_text("settings")
        external = self.home / "keys.json"
        external.write_text("custom keys")
        self.environment["CLI_HELP_CONFIG"] = str(external)
        before = installation.tree_state(self.prefix)
        rc = self.rc.read_bytes()
        self.assertEqual(self.run_update()[0], 0)
        self.assertEqual((self.prefix / "VERSION").read_bytes(), b"0.1.2\n")
        self.assertEqual(installation.tree_state(self.reports()[0].parent / "previous"), before)
        self.assertEqual(self.rc.read_bytes(), rc)
        self.assertEqual(local.read_text(), "settings")
        self.assertEqual(external.read_text(), "custom keys")
        self.assertFalse(self.stages())
        self.assertFalse((self.home / "NEVER").exists())

    def test_check_only_reads_metadata_and_does_not_create_files(self):
        client = self.client()
        before = installation.tree_state(self.prefix)
        status, output = self.run_update(client, check=True)
        self.assertEqual(status, 0)
        self.assertIn("available: v0.1.2", output)
        self.assertEqual(len(client.calls), 1)
        self.assertFalse(self.stages())
        self.assertEqual(installation.tree_state(self.prefix), before)

    def test_equal_older_and_empty_releases_never_download(self):
        for values in [[release("v" + self.current)], [release("v0.0.1")], []]:
            client = FakeClient(values)
            with self.subTest(values=values):
                self.assertEqual(self.run_update(client, prerelease=True)[0], 0)
                self.assertEqual(len(client.calls), 1)
        self.assertFalse(self.reports())

    def test_unmanaged_edited_missing_and_symlinked_version_fail_before_network(self):
        version = self.prefix / "VERSION"
        original = version.read_bytes()
        for mutation in [lambda: version.write_text("9.0.0"), lambda: version.unlink(),
                         lambda: (version.unlink(), version.symlink_to(self.home / "missing"))]:
            client = self.client()
            mutation()
            with self.assertRaises(ValueError):
                self.run_update(client)
            self.assertFalse(client.calls)
            version.unlink(missing_ok=True)
            version.write_bytes(original)
        (self.prefix / installation.MARKER).unlink()
        with self.assertRaises(ValueError):
            self.run_update()

    def test_bad_checksum_and_archive_do_not_touch_installation(self):
        before = installation.tree_state(self.prefix)
        client = self.client()
        package = client.releases[0]["assets"][0]
        client.blobs[package["browser_download_url"]] = b"x" * package["size"]
        with self.assertRaises(ValueError):
            self.run_update(client)
        value, blobs = package_release(b"bad archive")
        with self.assertRaises(OSError):
            self.run_update(FakeClient([value], blobs))
        self.assertEqual(installation.tree_state(self.prefix), before)
        self.assertFalse(self.stages())
        self.assertFalse(self.reports())

    def test_pending_conflicts_keep_local_and_retain_verified_reviewer(self):
        local = self.prefix / "profiles/rsync.json"
        data = local.read_bytes() + b"\n "
        local.write_bytes(data)
        status, output = self.run_update(no_review=True)
        self.assertEqual(status, 2)
        self.assertEqual(local.read_bytes(), data)
        self.assertIn("Resume guided conflict review", output)
        self.assertTrue((self.stages()[0] / "cli-interactive-help-v0.1.2/scripts/update_review.py").is_file())
        self.assertEqual(update_review.ReviewSession(self.reports()[0]).status("profiles/rsync.json"), "pending")

    def test_nonterminal_conflicts_do_not_open_reviewer(self):
        (self.prefix / "profiles/rsync.json").write_text("custom")
        with patch.object(sys.stdin, "isatty", return_value=False), patch.object(updater.subprocess, "run", wraps=subprocess.run) as run:
            self.assertEqual(self.run_update()[0], 2)
        self.assertEqual(run.call_count, 1)

    def test_download_cancellation_leaves_installation_unchanged(self):
        before = installation.tree_state(self.prefix)
        client = self.client()
        with patch.object(client, "fetch", side_effect=KeyboardInterrupt), self.assertRaises(KeyboardInterrupt):
            self.run_update(client)
        self.assertFalse(self.stages())
        self.assertEqual(installation.tree_state(self.prefix), before)

    def test_interrupted_apply_retains_source(self):
        with patch.object(updater.subprocess, "run", side_effect=KeyboardInterrupt), self.assertRaises(KeyboardInterrupt):
            self.run_update()
        self.assertEqual(len(self.stages()), 1)
        self.assertEqual((self.prefix / "VERSION").read_text().strip(), self.current)

    def test_lock_and_invalid_incoming_validation_preserve_runtime(self):
        before = installation.tree_state(self.prefix)
        lock = self.prefix.with_name(self.prefix.name + ".install.lock")
        lock.touch()
        with self.assertRaisesRegex(ValueError, "Incoming updater failed"):
            self.run_update()
        lock.unlink()
        self.files["profiles/rsync.json"] = b"invalid JSON"
        with self.assertRaisesRegex(ValueError, "Incoming updater failed"):
            self.run_update()
        self.assertEqual(installation.tree_state(self.prefix), before)
        self.assertFalse(self.reports())

    def test_changed_version_during_download_stops_before_apply(self):
        client = self.client()
        original = client.fetch
        def changed(url, limit):
            data = original(url, limit)
            if url.endswith(".tar.gz"):
                (self.prefix / "VERSION").write_text("0.9.0")
            return data
        with patch.object(client, "fetch", side_effect=changed), self.assertRaises(ValueError):
            self.run_update(client)
        self.assertFalse(self.stages())
        self.assertFalse(self.reports())

    def test_expected_version_is_checked_under_install_lock(self):
        incoming = self.home / "incoming"
        incoming.mkdir()
        for name, data in self.files.items():
            path = incoming / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        result = subprocess.run([sys.executable, str(incoming / "scripts/installation.py"), "update", "--prefix", str(self.prefix),
                                 "--expected-version", "0.0.0", "--result-file", str(self.home / "result.json")],
                                env=self.environment, capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn("before the update lock", result.stderr)
        self.assertFalse(self.reports())
        self.assertFalse((self.home / "result.json").exists())

    def test_result_file_cannot_overwrite_or_enter_installation(self):
        existing = self.home / "existing.json"
        existing.write_text("original")
        for target in [existing, self.prefix / "result.json", self.home / "missing/result.json"]:
            result = subprocess.run([sys.executable, str(ROOT / "scripts/installation.py"), "update", "--prefix", str(self.prefix),
                                     "--result-file", str(target)], env=self.environment, capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)
        self.assertEqual(existing.read_text(), "original")
        self.assertFalse(self.reports())

    def test_result_noop_and_invalid_action_flags(self):
        target = self.home / "result.json"
        result = subprocess.run([sys.executable, str(ROOT / "scripts/installation.py"), "update", "--prefix", str(self.prefix),
                                 "--result-file", str(target)], env=self.environment, capture_output=True)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(json.loads(target.read_text()), {"schema_version": 1, "status": 0, "report": None})
        result = subprocess.run([sys.executable, str(ROOT / "scripts/installation.py"), "uninstall", "--prefix", str(self.prefix),
                                 "--expected-version", self.current], env=self.environment, capture_output=True)
        self.assertEqual(result.returncode, 2)

    def test_installed_wrapper_uses_custom_prefix_by_default(self):
        with patch.object(installation, "ROOT", self.prefix), patch.object(updater, "GitHubClient", return_value=FakeClient([])), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(updater.main(["--check"]), 0)
        environment = dict(self.environment)
        environment.pop("PYTHONDONTWRITEBYTECODE", None)
        before = installation.tree_state(self.prefix)
        result = subprocess.run(["bash", str(self.prefix / "update-from-github.sh"), "--help"], env=environment, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn("--prerelease", result.stdout)
        self.assertEqual(installation.tree_state(self.prefix), before)

    def test_locally_edited_installed_code_is_not_run_by_update_validation(self):
        marker = self.home / "executed-code"
        data = f"from pathlib import Path\nPath({str(marker)!r}).touch()\n".encode()
        (self.prefix / "cli_help/main.py").write_bytes(data)
        self.assertEqual(self.run_update(no_review=True)[0], 2)
        self.assertFalse(marker.exists())
        self.assertEqual((self.prefix / "cli_help/main.py").read_bytes(), data)

    def test_unverified_incoming_code_is_never_executed(self):
        marker = self.home / "unverified-code"
        self.files["scripts/installation.py"] = f"open({str(marker)!r}, 'w').write('executed')\n".encode()
        client = self.client()
        client.releases[0]["assets"][0]["digest"] = "sha256:" + "0" * 64
        with self.assertRaises(ValueError):
            self.run_update(client)
        self.assertFalse(marker.exists())
        self.assertFalse(self.stages())

    def test_completion_missing_invalid_schema_or_status_retains_recovery_source(self):
        values = [None, {}, {"schema_version": 1, "status": True}, {"schema_version": 1, "status": 2, "report": None}]
        for value in values:
            def completion(command, **kwargs):
                if value is not None:
                    Path(command[command.index("--result-file") + 1]).write_text(json.dumps(value))
                return subprocess.CompletedProcess(command, 2 if value and value.get("status") == 2 else 0)
            with self.subTest(value=value), patch.object(updater.subprocess, "run", side_effect=completion), self.assertRaises(ValueError):
                self.run_update()
        self.assertEqual(len(self.stages()), len(values))
        self.assertFalse(self.reports())

    def test_incoming_interrupt_exit_status_is_preserved(self):
        for status in [130, -2]:
            with self.subTest(status=status), patch.object(updater.subprocess, "run", return_value=subprocess.CompletedProcess([], status)):
                self.assertEqual(self.run_update()[0], 130)
        self.assertEqual(len(self.stages()), 2)

    def test_reviewer_exit_and_unsaved_decisions_leave_conflicts_pending(self):
        for review_status, expected in [(0, 2), (1, 2), (130, 130)]:
            # Each case uses the same partial update; reset only the managed version
            # to model a fresh older installation for the next isolated upgrade.
            (self.prefix / "profiles/rsync.json").write_text("local edit")
            (self.prefix / "VERSION").write_text(self.current + "\n")
            manifest = installation.load_manifest(self.prefix)
            manifest["files"]["VERSION"] = installation.digest((self.prefix / "VERSION").read_bytes())
            (self.prefix / installation.MARKER).write_text(json.dumps(manifest))
            runner = subprocess.run
            def dispatch(command, **kwargs):
                if command[1].endswith("update_review.py"):
                    return subprocess.CompletedProcess(command, review_status)
                return runner(command, **kwargs)
            output = io.StringIO()
            with self.subTest(status=review_status), patch.object(sys.stdin, "isatty", return_value=True), \
                    patch.object(output, "isatty", return_value=True), contextlib.redirect_stdout(output), \
                    patch.object(updater.subprocess, "run", side_effect=dispatch):
                self.assertEqual(updater.run_update(self.prefix, self.client(), source=True), expected)
            self.assertIn("Opening conflict review", output.getvalue())
            self.assertEqual((self.prefix / "profiles/rsync.json").read_text(), "local edit")

    def test_completion_write_failure_after_switch_keeps_install_and_backup(self):
        self.files["scripts/installation.py"] = self.files["scripts/installation.py"].replace(
            b'with result_file.open("x", encoding="utf-8") as stream:', b'raise OSError("completion write failed")\n        with result_file.open("x", encoding="utf-8") as stream:')
        with self.assertRaisesRegex(ValueError, "Incoming updater failed"):
            self.run_update()
        self.assertEqual((self.prefix / "VERSION").read_bytes(), b"0.1.2\n")
        self.assertEqual((self.reports()[0].parent / "previous/VERSION").read_text().strip(), self.current)
        self.assertTrue(self.stages())

    def test_cli_errors_interruptions_and_relative_xdg(self):
        with patch.object(updater, "GitHubClient", return_value=self.client()), patch.object(updater, "run_update", side_effect=EOFError), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(updater.main(["--prefix", str(self.prefix)]), 1)
        with patch.object(updater, "run_update", side_effect=KeyboardInterrupt), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(updater.main(["--prefix", str(self.prefix)]), 130)
        with patch.dict(os.environ, {"XDG_DATA_HOME": "relative"}), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(updater.main(["--check"]), 1)
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
            updater.main(["--unknown"])
        self.assertEqual(error.exception.code, 2)

    def test_real_terminal_download_update_guided_merge_and_safe_insertion(self):
        local = self.prefix / "cli_help/release_fixture.py"
        local.write_bytes(b"# local first\n# stable\n# local last\n")
        client = self.client()
        datafile = self.home / "responses.json"
        datafile.write_text(json.dumps({"releases": client.releases, "blobs": {url: data.hex() for url, data in client.blobs.items()}}))
        harness = self.home / "terminal_update.py"
        harness.write_text("import sys,json\nfrom pathlib import Path\n"
                           + "sys.path.insert(0, " + repr(str(ROOT / "tests")) + ")\n"
                           + "from test_release_update import FakeClient,updater\n"
                           + "data=json.loads(Path(" + repr(str(datafile)) + ").read_text())\n"
                           + "client=FakeClient(data['releases'], {url:bytes.fromhex(value) for url,value in data['blobs'].items()})\n"
                           + "status=updater.run_update(Path(" + repr(str(self.prefix)) + "),client,source=True)\n"
                           + "print('RELEASE_STATUS',status)\n")
        folder = self.home / "terminal"
        folder.mkdir()
        shell = BashSession(folder, extra_environment=self.environment)
        try:
            shell.send(shlex.join([sys.executable, str(harness)]) + "\n")
            shell.expect(b"Opening conflict review", timeout=15)
            shell.expect(b"Review >")
            shell.send("1\n")
            shell.expect(b"Choice >")
            shell.send("g\n")
            shell.expect(b"Guided >")
            shell.send("a\n")
            shell.expect(b"Guided change 2/2")
            shell.expect(b"Guided >")
            shell.send("r\n")
            shell.expect(b"Guided >")
            shell.send("d\n")
            shell.expect(b"Choice >")
            shell.send("b\n")
            shell.expect(b"Review >")
            shell.send("s\n")
            shell.expect(b"Apply queued choices with backups?")
            shell.send("y\n")
            shell.expect(b"Choices saved.")
            shell.expect(b"Review >")
            shell.send("q\n")
            shell.expect(b"RELEASE_STATUS 0")
            shell.expect(b"__HELP_TEST_PROMPT__")
            self.assertEqual(local.read_bytes(), b"# incoming first\n# stable\n# local last\n")
            shell.send("cli_help_unbind; source " + shlex.quote(str(self.prefix / "bash/interactive-help.bash")) + "\n")
            shell.expect(b"__HELP_TEST_PROMPT__")
            shell.open("rsync --ar")
            shell.finish("\n")
            self.assertEqual(shell.read_buffer(), ("rsync --archive ", 16))
            self.assertFalse(shell.executed.exists())
        finally:
            shell.close()


if __name__ == "__main__":
    unittest.main()
