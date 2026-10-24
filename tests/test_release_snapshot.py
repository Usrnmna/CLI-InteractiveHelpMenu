"""Verify release selection boundaries and actual packaged foundational workflows."""

import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch

from test_discovery import ROOT

sys.path.insert(0, str(ROOT / "scripts"))
import build_release
import installation
import release_update
import update_review
import test_release_update as release_fixtures


REQUIRED_SOURCE = {
    "cli_help/arguments.py", "cli_help/collection.py", "cli_help/diagnostics.py", "cli_help/invocation.py",
    "cli_help/core.py", "cli_help/discovery.py", "cli_help/ui.py", "cli_help/review_forms.py",
    "profiles/7z-x.json", "profiles/7zz-x.json", "config/drivers.example/docker.json",
    "update-from-github.sh", "scripts/release_update.py", "scripts/update_review.py",
    "tests/test_syntax_collection_review.py", "tests/fixtures/help/syntax-7zip-captured.json",
    "docs/argument-syntax.md", "docs/collection-recovery.md", "docs/assets/option-insertion.gif",
    ".github/workflows/ci.yml", ".gitignore", ".gitattributes", ".editorconfig", "lychee.toml",
}


def verify_candidate(directory):
    """Require current-source provenance and local checksums before testing a candidate."""
    version = (ROOT / "VERSION").read_text().strip()
    info = json.loads((directory / "BUILD-INFO.json").read_text())
    if info["version"] != version or not REQUIRED_SOURCE <= set(info["source_files"]):
        raise AssertionError("Candidate version or required source inventory differs")
    selected = {path.relative_to(ROOT).as_posix() for path in build_release.source_files(ROOT)}
    if set(info["source_files"]) != selected:
        raise AssertionError("Candidate source inventory differs from the current maintained inputs")
    source_contents = {}
    for name, digest in info["source_files"].items():
        path = Path(name)
        if path.is_absolute() or ".." in path.parts or path.as_posix() != name:
            raise AssertionError("Noncanonical candidate source name")
        source_contents[name] = build_release.read_source(ROOT, path)
        if hashlib.sha256(source_contents[name]).hexdigest() != digest:
            raise AssertionError("Candidate is stale relative to the selected source: " + name)
    base = "cli-interactive-help-v" + version
    expected = {"BUILD-INFO.json", "cli-help-v" + version + "-linux-x86_64",
                base + "-source.tar.gz", base + "-linux-x86_64.tar.gz", base + "-linux-x86_64.run"}
    lines = (directory / "SHA256SUMS.checksum").read_text().splitlines()
    if len(lines) != len(expected) or {line.split("  ", 1)[1] for line in lines} != expected:
        raise AssertionError("Candidate aggregate checksum inventory differs")
    if {path.name for path in directory.iterdir()} != expected | {name + ".checksum" for name in expected} | {"SHA256SUMS.checksum"}:
        raise AssertionError("Candidate artifact inventory differs")
    for line in lines:
        digest, name = line.split("  ", 1)
        if Path(name).name != name or hashlib.sha256((directory / name).read_bytes()).hexdigest() != digest:
            raise AssertionError("Candidate checksum mismatch")
        if (directory / (name + ".checksum")).read_text() != line + "\n":
            raise AssertionError("Candidate per-artifact checksum differs")
    native = (directory / ("cli-help-v" + version + "-linux-x86_64")).read_bytes()
    if not native.startswith(b"\x7fELF"):
        raise AssertionError("Candidate launcher is not an ELF executable")
    runtime = (directory / (base + "-linux-x86_64.tar.gz")).read_bytes()
    # Check the actual payload and reviewed wrapper before any caller can run
    # an installer. Checksums alone permit a coherently rechecksummed mismatch.
    if (directory / (base + "-linux-x86_64.run")).read_bytes() != build_release.installer(runtime, base):
        raise AssertionError("Candidate installer wrapper or payload differs")
    for filename, expected_contents in ((base + "-source.tar.gz", source_contents),
                                        (base + "-linux-x86_64.tar.gz", {**source_contents, "cli-help": native})):
        seen = set()
        with tarfile.open(directory / filename) as archive:
            for member in archive:
                name = member.name.removeprefix(base + "/")
                if (member.name != base + "/" + name or name not in expected_contents or name in seen
                        or not member.isfile() or member.issparse()):
                    raise AssertionError("Candidate archive contains an unexpected or duplicate member")
                expected = expected_contents[name]
                mode = 0o755 if name.endswith(".sh") or name == "cli-help" else 0o644
                if (member.size != len(expected) or member.mode != mode or member.mtime != 0
                        or (member.uid, member.gid, member.uname, member.gname) != (0, 0, "", "")):
                    raise AssertionError("Candidate archive metadata differs")
                if archive.extractfile(member).read(len(expected) + 1) != expected:
                    raise AssertionError("Candidate archive source or launcher differs")
                seen.add(name)
        if seen != set(expected_contents):
            raise AssertionError("Candidate archive is incomplete")
    return info


class ReleaseInventoryTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="cli-help-build-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        for name in build_release.SOURCE_FILES:
            (self.root / name).write_text("0.1.2-alpha\n" if name == "VERSION" else "fixture\n")

    def put(self, name, content=b"PRIVATE_PACKAGE_SENTINEL"):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)

    def test_private_nested_inputs_are_excluded_and_public_inputs_remain(self):
        private = {
            "cli_help/.env", "cli_help/.env.local", "docs/.cache/private.md", "tools/.aws/credentials",
            "config/.ssh/id_ed25519", "tests/.venv/bin/private", "tests/reports/private.json",
            "profiles/.review-backups/saved/0.json", "config/.import.lock", "config/.scan.lock",
            "profiles/.cli-help-write-interrupted.tmp", "docs/cli-help-installer.Ab12Cd34/private.md",
            "tools/tool.update-backup-private/previous/VERSION", "docs/.git/config", "tools/node_modules/private.js",
            "tests/session.pyc", "docs/guide.md.swp", "config/.netrc", "private-notes.md",
            "tools/.config/gcloud/credentials.db", "tools/.config/gh/hosts.yml",
            "tests/.config/cli-help/profiles/private.json", "tools/.config/containers/auth.json",
            "tools/.local/share/containers/storage/private", "tests/htmlcov/index.html", "docs/.DS_Store",
        }
        public = {"cli_help/added_module.py", "tests/fixtures/help/captured.txt", "docs/assets/example.gif",
                  "config/.env.example", "config/.env.development.sample", "config/.env.template",
                  "docs/cli-help-installer.md", ".github/workflows/fixture.yml"}
        for name in private | public:
            self.put(name)
        selected = {path.relative_to(self.root).as_posix() for path in build_release.source_files(self.root)}
        self.assertFalse(selected & private)
        self.assertTrue(public <= selected)

    @unittest.skipUnless(sys.platform.startswith("linux"), "POSIX source-file boundaries")
    def test_maintained_links_and_special_files_are_rejected(self):
        self.put("docs/public.md")
        (self.root / "docs/link.md").symlink_to(self.root / "docs/public.md")
        with self.assertRaises(ValueError):
            build_release.source_files(self.root)
        (self.root / "docs/link.md").unlink()
        os.mkfifo(self.root / "docs/pipe")
        with self.assertRaises(ValueError):
            build_release.source_files(self.root)

    @unittest.skipUnless(sys.platform.startswith("linux"), "Linux release builder")
    def test_output_cannot_become_a_maintained_source_input(self):
        with self.assertRaisesRegex(ValueError, "source director"):
            build_release.build(self.root, self.root / "docs/candidate")
        self.assertFalse((self.root / "docs/candidate").exists())

    @unittest.skipUnless(sys.platform.startswith("linux"), "POSIX capture boundaries")
    def test_source_file_swap_cannot_capture_an_external_canary(self):
        self.check_capture_swap(directory=False)

    @unittest.skipUnless(sys.platform.startswith("linux"), "POSIX capture boundaries")
    def test_source_directory_swap_cannot_capture_an_external_canary(self):
        self.check_capture_swap(directory=True)

    def check_capture_swap(self, directory):
        """Replace an enumerated input with a link before its capture starts."""
        self.put("native/cli_help.c", (ROOT / "native/cli_help.c").read_bytes())
        self.put("docs/canary.txt", b"Public placeholder")
        self.put("outside/canary.txt", b"SOURCE_PRIVATE_SENTINEL")
        original = build_release.source_files
        def replace(selected_root):
            selected = original(selected_root)
            if directory:
                (self.root / "docs").rename(self.root / "original-docs")
                (self.root / "docs").symlink_to(self.root / "outside", target_is_directory=True)
            else:
                (self.root / "docs/canary.txt").unlink()
                (self.root / "docs/canary.txt").symlink_to(self.root / "outside/canary.txt")
            return selected
        output = self.root / "candidate"
        with patch.object(build_release, "source_files", side_effect=replace):
            with self.assertRaisesRegex(ValueError, "Release source") as rejected:
                build_release.build(self.root, output)
        self.assertNotIn("SOURCE_PRIVATE_SENTINEL", str(rejected.exception))
        self.assertFalse(output.exists())
        self.assertEqual((self.root / "outside/canary.txt").read_bytes(), b"SOURCE_PRIVATE_SENTINEL")

    @unittest.skipUnless(sys.platform.startswith("linux"), "POSIX capture boundaries")
    def test_fifo_capture_is_bounded_and_rejected_before_reading(self):
        (self.root / "docs").mkdir()
        os.mkfifo(self.root / "docs/pending.txt")
        script = ("import sys\nfrom pathlib import Path\nsys.path.insert(0,sys.argv[1])\n"
                  "from build_release import read_source\nread_source(Path(sys.argv[2]),Path('docs/pending.txt'))\n")
        result = subprocess.run([sys.executable, "-B", "-c", script, str(ROOT / "scripts"), str(self.root)],
                                capture_output=True, text=True, timeout=5)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Release source is unsafe", result.stderr)

    @unittest.skipUnless(sys.platform.startswith("linux"), "POSIX capture boundaries")
    def test_input_changes_during_read_are_rejected(self):
        for replace in (False, True):
            with self.subTest(replace=replace):
                self.put("docs/changing.txt", b"Public placeholder")
                original = os.read
                changed = False
                def change_after_read(descriptor, size):
                    nonlocal changed
                    data = original(descriptor, size)
                    if not changed:
                        changed = True
                        target = self.root / "docs/changing.txt"
                        if replace:
                            incoming = self.root / "incoming"
                            incoming.write_bytes(b"Changed source bytes")
                            incoming.replace(target)
                        else:
                            target.write_bytes(b"Changed source bytes")
                    return data
                with patch.object(build_release.os, "read", side_effect=change_after_read):
                    with self.assertRaisesRegex(ValueError, "changed"):
                        build_release.read_source(self.root, Path("docs/changing.txt"))
                self.assertTrue(changed)
                self.assertEqual((self.root / "docs/changing.txt").read_bytes(), b"Changed source bytes")

    @unittest.skipUnless(sys.platform.startswith("linux"), "POSIX capture boundaries")
    def test_pinned_directory_replacement_during_read_is_rejected(self):
        self.put("docs/changing.txt", b"Public placeholder")
        original = os.read
        changed = False
        def replace_parent(descriptor, size):
            nonlocal changed
            data = original(descriptor, size)
            if not changed:
                changed = True
                (self.root / "docs").rename(self.root / "original-docs")
                self.put("docs/changing.txt", b"Changed source bytes")
            return data
        with patch.object(build_release.os, "read", side_effect=replace_parent):
            with self.assertRaisesRegex(ValueError, "changed"):
                build_release.read_source(self.root, Path("docs/changing.txt"))
        self.assertEqual((self.root / "original-docs/changing.txt").read_bytes(), b"Public placeholder")

    @unittest.skipUnless(sys.platform.startswith("linux"), "POSIX capture boundaries")
    def test_capture_does_not_follow_an_unbounded_growing_file(self):
        self.put("docs/growing.txt", b"seed")
        def growing_read(descriptor, size):
            if size != 5:
                raise AssertionError("Capture must stop at the observed size plus one detection byte")
            return b"extra"
        with patch.object(build_release.os, "read", side_effect=growing_read) as read:
            with self.assertRaisesRegex(ValueError, "changed"):
                build_release.read_source(self.root, Path("docs/growing.txt"))
        self.assertEqual(read.call_count, 1)

    def test_source_names_match_the_updater_path_contract(self):
        for name in ("docs/back\\slash.txt", "docs/control\nname.txt"):
            with self.subTest(name=name):
                self.put(name)
                with self.assertRaisesRegex(ValueError, "paths must not"):
                    build_release.source_files(self.root)
                (self.root / name).unlink()


class CandidatePackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.version = (ROOT / "VERSION").read_text().strip()
        cls.base = "cli-interactive-help-v" + cls.version
        cls.build_folder = tempfile.TemporaryDirectory(prefix="cli-help-build-")
        cls.addClassCleanup(cls.build_folder.cleanup)
        selected = os.environ.get("CLI_HELP_TEST_RELEASE_DIR")
        cls.output = Path(selected).resolve(strict=True) if selected else Path(cls.build_folder.name) / "candidate"
        if not selected:
            build_release.build(ROOT, cls.output)
        cls.info = verify_candidate(cls.output)
        cls.bundle = cls.output / (cls.base + "-linux-x86_64.tar.gz")
        cls.source = cls.output / (cls.base + "-source.tar.gz")
        cls.installer = cls.output / (cls.base + "-linux-x86_64.run")

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="cli-help-build-")
        self.addCleanup(self.temporary.cleanup)
        self.home = Path(self.temporary.name)
        self.prefix = self.home / "installed runtime's literal path"
        self.environment = {key: value for key, value in os.environ.items() if not key.startswith("CLI_HELP_")
                            and key not in {"BASH_ENV", "ENV", "PYTHONPATH", "PYTHONHOME", "XDG_DATA_HOME", "TMPDIR"}}
        self.environment.update(HOME=str(self.home), XDG_CONFIG_HOME=str(self.home / "config-home"),
            XDG_CACHE_HOME=str(self.home / "cache-home"), XDG_DATA_HOME=str(self.home / "data-home"),
            TMPDIR=str(self.home), CLI_HELP_PYTHON=sys.executable, CLI_HELP_DISCOVERY="off", PYTHONDONTWRITEBYTECODE="1")

    def run_command(self, arguments, status=0, environment=None):
        result = subprocess.run(list(map(str, arguments)), env=environment or self.environment,
                                capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, status, result.stdout + result.stderr)
        return result

    def extract(self, archive=None, name="extracted"):
        folder = self.home / name
        folder.mkdir()
        self.run_command(["tar", "-xzf", archive or self.bundle, "-C", folder])
        return folder / self.base

    def install(self):
        self.run_command(["bash", self.installer, "install", "--prefix", self.prefix, "--no-rc"])
        return self.prefix

    def rewrite_checksum(self, directory, name):
        """Rechecksum synthetic inconsistent artifacts to isolate provenance checks."""
        line = hashlib.sha256((directory / name).read_bytes()).hexdigest() + "  " + name + "\n"
        (directory / (name + ".checksum")).write_text(line)
        aggregate = directory / "SHA256SUMS.checksum"
        aggregate.write_text("".join(line if item.split("  ", 1)[1] == name else item + "\n"
                                     for item in aggregate.read_text().splitlines()))

    def assert_passive_verification_rejects(self, directory):
        """Reject altered bytes without execution, writes, or echoed canaries."""
        before = installation.tree_state(directory)
        with patch.object(subprocess, "Popen", side_effect=AssertionError("Verifier started a process")) as launch:
            with self.assertRaises(AssertionError) as rejected:
                verify_candidate(directory)
        launch.assert_not_called()
        self.assertNotIn("PACKAGE_PRIVATE_SENTINEL", str(rejected.exception))
        self.assertEqual(installation.tree_state(directory), before)

    def test_verifier_rejects_a_rechecksummed_unrelated_installer(self):
        directory = self.home / "changed-installer"
        shutil.copytree(self.output, directory)
        name = self.installer.name
        (directory / name).write_bytes(b"#!/bin/bash\nprintf 'PACKAGE_PRIVATE_SENTINEL\\n'\n")
        self.rewrite_checksum(directory, name)
        self.assert_passive_verification_rejects(directory)

    def test_verifier_rejects_rechecksummed_stale_archive_bytes(self):
        for suffix in ("-source.tar.gz", "-linux-x86_64.tar.gz"):
            with self.subTest(archive=suffix):
                directory = self.home / suffix[1:]
                shutil.copytree(self.output, directory)
                name = self.base + suffix
                members = []
                with tarfile.open(directory / name) as archive:
                    for member in archive:
                        data = archive.extractfile(member).read()
                        if member.name == self.base + "/VERSION":
                            data = b"0.1.1-alpha\n"
                            member.size = len(data)
                        members.append((member, data))
                with tarfile.open(directory / name, "w:gz") as archive:
                    for member, data in members:
                        archive.addfile(member, io.BytesIO(data))
                self.rewrite_checksum(directory, name)
                if suffix == "-linux-x86_64.tar.gz":
                    (directory / self.installer.name).write_bytes(build_release.installer((directory / name).read_bytes(), self.base))
                    self.rewrite_checksum(directory, self.installer.name)
                self.assert_passive_verification_rejects(directory)

    def test_verifier_rejects_duplicate_archive_members(self):
        directory = self.home / "duplicate-members"
        shutil.copytree(self.output, directory)
        name = self.source.name
        with tarfile.open(directory / name) as archive:
            members = [(member, archive.extractfile(member).read()) for member in archive]
        with tarfile.open(directory / name, "w:gz") as archive:
            for member, data in [*members, members[0]]:
                archive.addfile(member, io.BytesIO(data))
        self.rewrite_checksum(directory, name)
        self.assert_passive_verification_rejects(directory)

    def historical_installer(self):
        directory = Path(os.environ.get("CLI_HELP_TEST_HISTORICAL_DIR", ROOT / "releases/v0.1.1-alpha"))
        path = directory / "cli-interactive-help-v0.1.1-alpha-linux-x86_64.run"
        if not path.is_file():
            self.skipTest("Preserved v0.1.1-alpha artifact is unavailable; legacy package upgrade remains unverified")
        digest, name = (directory / (path.name + ".checksum")).read_text().strip().split("  ", 1)
        self.assertEqual(name, path.name)
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), digest)
        return path

    def test_archives_manifest_modes_and_current_source_agree(self):
        sources = {}
        for path in (self.source, self.bundle):
            with tarfile.open(path) as archive:
                names = archive.getnames()
                self.assertEqual(names, sorted(names))
                content = {}
                for member in archive.getmembers():
                    self.assertTrue(member.isfile())
                    self.assertEqual(member.mtime, 0)
                    self.assertEqual((member.uid, member.gid, member.uname, member.gname), (0, 0, "", ""))
                    self.assertTrue(member.name.startswith(self.base + "/"))
                    name = member.name[len(self.base) + 1:]
                    self.assertEqual(member.mode, 0o755 if name.endswith(".sh") or name == "cli-help" else 0o644)
                    content[name] = archive.extractfile(member).read()
                sources[path] = content
        binary = sources[self.bundle].pop("cli-help")
        self.assertTrue(binary.startswith(b"\x7fELF"))
        self.assertEqual(sources[self.source], sources[self.bundle])
        self.assertEqual(set(sources[self.source]), set(self.info["source_files"]))
        self.assertTrue(REQUIRED_SOURCE <= set(sources[self.source]))
        for name, data in sources[self.source].items():
            self.assertEqual(hashlib.sha256(data).hexdigest(), self.info["source_files"][name])

    def test_compiler_uses_captured_source_bytes(self):
        source = self.extract(self.source)
        expected = (source / "native/cli_help.c").read_bytes()
        original_run = subprocess.run
        altered = False
        def change_checkout(arguments, **keywords):
            nonlocal altered
            if "-std=c11" in arguments and not altered:
                altered = True
                (source / "native/cli_help.c").write_text("INVALID_MUTATED_SOURCE_SENTINEL")
            return original_run(arguments, **keywords)
        output = self.home / "frozen-source"
        with patch.object(build_release.subprocess, "run", side_effect=change_checkout):
            build_release.build(source, output)
        self.assertTrue(altered)
        manifest = json.loads((output / "BUILD-INFO.json").read_text())
        self.assertEqual(manifest["source_files"]["native/cli_help.c"], hashlib.sha256(expected).hexdigest())

    def test_version_change_during_capture_refuses_artifacts(self):
        source = self.extract(self.source)
        original = build_release.source_files
        def change_version(root):
            selected = original(root)
            (root / "VERSION").write_text("99.0.0\n")
            return selected
        with patch.object(build_release, "source_files", side_effect=change_version), self.assertRaisesRegex(ValueError, "VERSION changed"):
            build_release.build(source, self.home / "inconsistent")
        self.assertFalse((self.home / "inconsistent").exists())

    def test_relocated_native_and_installed_passive_modes(self):
        runtime = self.extract()
        moved = self.home / "relocated runtime's path"
        runtime.rename(moved)
        self.assertEqual(self.run_command([moved / "cli-help", "--version"]).stdout.strip(), "CLI Interactive Help Menu " + self.version)
        self.run_command([moved / "cli-help", "install", "--prefix", self.prefix, "--no-rc"])
        for name in ("arguments.py", "collection.py", "diagnostics.py", "invocation.py"):
            self.assertTrue((self.prefix / "cli_help" / name).is_file())
        self.assertFalse((self.prefix / "tools").exists())
        self.assertFalse((self.prefix / "tests").exists())
        binaries = self.home / "bin"
        binaries.mkdir()
        marker = self.home / "target-started"
        for name in ("docker", "kubectl", "7z"):
            program = binaries / name
            program.write_text("#!" + sys.executable + "\nfrom pathlib import Path\nPath(" + repr(str(marker)) + ").touch()\n")
            program.chmod(0o700)
        environment = dict(self.environment, PATH=str(binaries) + os.pathsep + self.environment["PATH"],
                           CLI_HELP_DRIVERS=str(self.prefix / "config/drivers.example"), CLI_HELP_ESCAPE_DELAY="250")
        before = installation.tree_state(self.home)
        doctor = json.loads(self.run_command([self.prefix / "cli-help", "--doctor"], environment=environment).stdout)
        self.assertTrue(doctor["configuration"]["driver_selection"]["supplied_selected"])
        self.assertEqual(doctor["configuration"]["escape_delay_ms"], 250)
        secret = "PACKAGED_PRIVATE_SENTINEL"
        line = "docker compose -f " + secret + " --profile debug up --det"
        environment.update(CLI_HELP_LINE=line, CLI_HELP_POINT=str(len(line)))
        explanation = self.run_command([self.prefix / "cli-help", "--explain"], environment=environment)
        self.assertNotIn(secret, explanation.stdout + explanation.stderr)
        self.assertEqual(json.loads(explanation.stdout)["resolved_command"], ["docker", "compose", "up"])
        line = "kubectl --token=" + secret + " get --"
        environment.update(CLI_HELP_LINE=line, CLI_HELP_POINT=str(len(line)))
        for mode in ("--explain", "--bash"):
            result = self.run_command([self.prefix / "cli-help", mode], status=1, environment=environment)
            self.assertNotIn(secret, result.stdout + result.stderr)
        self.assertEqual(installation.tree_state(self.home), before)
        self.assertFalse(marker.exists())
        self.assertFalse((self.home / ".bashrc").exists())

    def test_native_failure_omits_interpreter_setting_and_pending_input(self):
        runtime = self.extract()
        secret = "PACKAGE_PRIVATE_SENTINEL"
        line = "kubectl --token=" + secret + " get --"
        environment = dict(self.environment, CLI_HELP_PYTHON=str(self.home / ("missing-" + secret)),
                           CLI_HELP_LINE=line, CLI_HELP_POINT=str(len(line)))
        before = installation.tree_state(self.home)
        for mode in ("--doctor", "--explain", "--bash"):
            result = self.run_command([runtime / "cli-help", mode], status=127, environment=environment)
            self.assertNotIn(secret, result.stdout + result.stderr)
            self.assertIn("cannot start Python interpreter", result.stderr)
        self.assertEqual(installation.tree_state(self.home), before)

    def test_packaged_collection_inspection_and_explicit_recovery(self):
        self.install()
        collection = self.home / "collection"
        (collection / "profiles").mkdir(parents=True)
        (collection / "drivers").mkdir()
        profile = {"command": ["fixture"], "description": "Original", "categories": [{"name": "Options", "options": [
            {"flag": "-o", "argument": "DIR", "argument_style": "attached_only", "summary": "Output"}]}]}
        original = (json.dumps(profile, ensure_ascii=False, indent=2) + "\n").encode()
        (collection / "profiles/fixture.json").write_bytes(original)
        (collection / "drivers/fixture.json").write_text(json.dumps({"command": "fixture", "paths": [{"command": [], "man": "fixture"}]}))
        report = collection / "scan-report.json"
        report.write_text(json.dumps({"schema_version": 1, "finished": True, "records": [
            {"command": ["fixture"], "status": "needs_adjustment", "generated": True}]}))
        helper = self.home / "save-review.py"
        helper.write_text("import json,sys\nfrom pathlib import Path\nsys.path.insert(0,sys.argv[1])\nfrom review import ReviewSession\n"
            "with ReviewSession(Path(sys.argv[2])) as session:\n draft=session.open_draft(0)\n document=draft.document()\n"
            " document['profile']['description']='Changed'\n draft.text=json.dumps(document)\n session.save(draft)\n")
        self.run_command([sys.executable, helper, self.prefix / "cli_help", report])
        (collection / "profiles/fixture.json").write_text("PACKAGED_PRIVATE_SENTINEL")
        before = installation.tree_state(self.home)
        result = self.run_command([self.prefix / "cli-help", "--check-collection", collection], status=1)
        self.assertNotIn("PACKAGED_PRIVATE_SENTINEL", result.stdout + result.stderr)
        self.assertEqual(installation.tree_state(self.home), before)
        state = json.loads(result.stdout)
        result = self.run_command([self.prefix / "cli-help", "--recover-collection", collection,
            "--restore-backup", state["review_backups"][0], "--expect-snapshot", state["snapshot"]])
        self.assertEqual(json.loads(result.stdout)["status"], "restored")
        self.assertNotIn("PACKAGED_PRIVATE_SENTINEL", result.stdout + result.stderr)
        self.assertEqual((collection / "profiles/fixture.json").read_bytes(), original)

    def test_historical_install_upgrade_and_source_only_lifecycle(self):
        self.run_command(["bash", self.historical_installer(), "install", "--prefix", self.prefix, "--no-rc"])
        self.assertFalse((self.prefix / "cli_help/arguments.py").exists())
        before = installation.tree_state(self.prefix)
        self.run_command(["bash", self.installer, "update", "--prefix", self.prefix])
        backup = next(self.home.glob(self.prefix.name + ".update-backup-*"))
        self.assertEqual(installation.tree_state(backup / "previous"), before)
        self.assertEqual((self.prefix / "VERSION").read_text().strip(), self.version)
        self.run_command([self.prefix / "cli-help", "--check"])
        self.run_command(["bash", self.installer, "update", "--prefix", self.prefix])
        source = self.extract(self.source, name="source-only")
        self.run_command(["bash", source / "update.sh", "--prefix", self.prefix])
        self.assertFalse((self.prefix / "cli-help").exists())
        self.run_command([sys.executable, self.prefix / "cli_help/main.py", "--check"])
        self.run_command(["bash", self.prefix / "uninstall.sh", "--prefix", self.prefix])
        self.assertFalse(self.prefix.exists())
        self.run_command(["bash", source / "install.sh", "--prefix", self.prefix, "--no-rc"])
        self.run_command(["bash", self.prefix / "uninstall.sh", "--prefix", self.prefix])
        self.assertFalse(self.prefix.exists())
        self.assertFalse((self.home / ".bashrc").exists())

    def test_conflict_source_choices_backups_and_unrelated_files_survive(self):
        self.install()
        profile = self.prefix / "profiles/rsync.json"
        driver = self.prefix / "config/drivers.example/docker.json"
        profile.write_bytes(profile.read_bytes() + b"\n ")
        driver.write_bytes(driver.read_bytes() + b"\n ")
        custom = self.prefix / "custom/preferences.json"
        custom.parent.mkdir()
        custom.write_text("private settings")
        external = self.home / "external-collection"
        external.mkdir()
        (external / "custom.json").write_text("external bytes")
        local_driver = driver.read_bytes()
        local_profile = profile.read_bytes()
        result = self.run_command(["bash", self.installer, "update", "--prefix", self.prefix], status=2)
        self.assertEqual(profile.read_bytes(), local_profile)
        self.assertEqual(driver.read_bytes(), local_driver)
        resume = next(line.removeprefix("Review conflicts: ") for line in result.stdout.splitlines() if line.startswith("Review conflicts: "))
        import shlex
        command = shlex.split(resume)
        self.assertTrue(Path(command[1]).is_file())
        self.run_command([*command, "--help"])
        report = Path(command[2])
        helper = self.home / "choose-conflicts.py"
        helper.write_text("import sys\nfrom pathlib import Path\nsys.path.insert(0,sys.argv[1])\nfrom update_review import ReviewSession\n"
            "session=ReviewSession(Path(sys.argv[2]))\nsession.choose('profiles/rsync.json','incoming')\n"
            "session.choose('config/drivers.example/docker.json','local')\n"
            "if sys.argv[3]=='save': print(session.save())\n")
        before = installation.tree_state(self.prefix)
        self.run_command([sys.executable, helper, Path(command[1]).parent / "scripts", report, "cancel"])
        self.assertEqual(installation.tree_state(self.prefix), before)
        self.run_command([sys.executable, helper, Path(command[1]).parent / "scripts", report, "save"])
        self.assertEqual(driver.read_bytes(), local_driver)
        self.assertNotEqual(profile.read_bytes(), local_profile)
        self.assertTrue(list(self.home.glob(self.prefix.name + ".update-review-backup-*")))
        self.assertEqual(custom.read_text(), "private settings")
        self.assertEqual((external / "custom.json").read_text(), "external bytes")
        self.run_command(["bash", self.prefix / "uninstall.sh", "--prefix", self.prefix])
        self.assertEqual(driver.read_bytes(), local_driver)
        self.assertEqual(custom.read_text(), "private settings")

    def test_built_archive_github_update_uses_fixtures_and_rejects_tampering(self):
        self.run_command(["bash", self.historical_installer(), "install", "--prefix", self.prefix, "--no-rc"])
        tag = "v" + self.version
        data = self.bundle.read_bytes()
        value, blobs = release_fixtures.package_release(data, tag=tag, native=True)
        archive_asset = value["assets"][0]
        before = installation.tree_state(self.prefix)
        client = release_fixtures.FakeClient([value], dict(blobs))
        client.blobs[archive_asset["browser_download_url"]] = b"x" * len(data)
        with patch.dict(os.environ, self.environment, clear=True), contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaises(ValueError):
                release_update.run_update(self.prefix, client, prerelease=True, no_review=True)
            self.assertEqual(installation.tree_state(self.prefix), before)
            valid = release_fixtures.FakeClient([value], blobs)
            self.assertEqual(release_update.run_update(self.prefix, valid, prerelease=True, no_review=True), 0)
            current = installation.tree_state(self.prefix)
            equal = release_fixtures.FakeClient([value], blobs)
            self.assertEqual(release_update.run_update(self.prefix, equal, prerelease=True, no_review=True), 0)
        self.assertEqual(len(equal.calls), 1)
        self.assertEqual(installation.tree_state(self.prefix), current)
        self.assertEqual((self.prefix / "VERSION").read_text().strip(), self.version)
