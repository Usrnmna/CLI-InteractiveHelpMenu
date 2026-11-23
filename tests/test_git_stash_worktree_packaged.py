"""Check direct Git declarations and exercise their effects in private temporary repositories."""

import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class DirectInventoryTests(unittest.TestCase):
    def test_manual_declarations_and_operand_ownership(self):
        """Compare every direct menu with the independent, release-qualified manual table."""
        table = (ROOT / "docs/git-stash-worktree-direct-inventory.md").read_text()
        expected = {}
        for line in table.splitlines():
            if not line.startswith("| `"):
                continue
            paths, spellings, operand, releases = (c.strip() for c in line.strip("|").split("|"))
            self.assertRegex(releases, r"^(NRU|RU|U)\b")
            for path in re.findall(r"`([^`]+)`", paths):
                options = expected.setdefault(path, {})
                for flag in re.findall(r"`([^`]+)`", spellings):
                    self.assertNotIn(flag, options)
                    options[flag] = operand
        self.assertEqual(len(expected), 9)
        for path, expected_options in expected.items():
            with self.subTest(path=path):
                profile = json.loads((ROOT / "profiles" / ("git-" + path.replace(" ", "-") + ".json")).read_text())
                rows = [o for c in profile["categories"] for o in c["options"]]
                self.assertEqual(len(rows), len(expected_options))
                self.assertEqual({o["flag"]: ("keyword" if o.get("kind") == "keyword" else
                                              o.get("argument") or "none") for o in rows}, expected_options)
                self.assertFalse(any(o.get("argument_optional") for o in rows))


class DirectPackagedGitTests(unittest.TestCase):
    def setUp(self):
        """Create an independent Git repository with isolated configuration and hooks."""
        temp = tempfile.TemporaryDirectory(prefix="cli-help-git-direct-")
        self.addCleanup(temp.cleanup)
        self.base = Path(temp.name)
        self.repo = self.base / "repo"
        self.repo.mkdir()
        home = self.base / "home"
        home.mkdir()
        self.env = {"HOME": str(home), "PATH": os.defpath, "LC_ALL": "C",
                    "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
                    "GIT_ATTR_NOSYSTEM": "1", "GIT_TERMINAL_PROMPT": "0",
                    "GIT_ALLOW_PROTOCOL": "", "GIT_PAGER": "cat",
                    "GIT_AUTHOR_DATE": "2026-01-01T00:00:00Z",
                    "GIT_COMMITTER_DATE": "2026-01-01T00:00:00Z"}
        binary = shutil.which("git", path=self.env["PATH"])
        if not binary:
            self.skipTest("Git unavailable")
        version = self.git("--version").decode()
        self.version = tuple(map(int, re.search(r"\d+\.\d+", version).group().split(".")))
        if self.version not in ((2, 43), (2, 53)):
            self.skipTest("Release observations cover Git 2.43 and 2.53")
        self.git("init", "--quiet", "--initial-branch=main", "--template=")
        for key, value in (("user.name", "Fixture"), ("user.email", "fixture@example.invalid"),
                           ("core.hooksPath", os.devnull), ("commit.gpgSign", "false"),
                           ("gc.auto", "0")):
            self.git("config", "--local", key, value)
        self.file = self.repo / "tracked"
        self.original = "".join(f"line {n}\n" for n in range(30))
        self.file.write_text(self.original)
        self.git("add", "tracked")
        self.git("commit", "-qm", "base")

    def invoke(self, *args, input_bytes=b""):
        """Run Git only against the disposable fixture and retain both streams and status."""
        return subprocess.run(["git", *args], cwd=self.repo, env=self.env, input=input_bytes,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=15)

    def git(self, *args, input_bytes=b""):
        """Require success and return the command's exact stdout."""
        result = self.invoke(*args, input_bytes=input_bytes)
        self.assertEqual(result.returncode, 0, (args, result.stderr, result.stdout))
        return result.stdout

    def test_help_ownership_against_fixed_usage(self):
        """An empty executable search path distinguishes manual dispatch from built-in usage."""
        empty = self.base / "empty"
        empty.mkdir()
        git = shutil.which("git", path=self.env["PATH"])
        env = {**self.env, "PATH": str(empty), "GIT_EXEC_PATH": str(empty)}
        release = "noble" if self.version == (2, 43) else "resolute"
        captures = json.loads((ROOT / "tests" / "fixtures" / "git-stash-worktree"
                               / f"{release}-usage.json").read_text())["usage"]
        paths = ("stash", "stash push", "stash apply", "stash pop", "stash list", "stash show",
                 "worktree", "worktree add", "worktree list", "worktree prune", "worktree remove")
        for path in paths:
            for flag in ("--help", "--help-all"):
                with self.subTest(path=path, flag=flag):
                    result = subprocess.run([git, *path.split(), flag], cwd=self.repo, env=env,
                                            capture_output=True, timeout=10)
                    if flag == "--help" and path in ("stash", "worktree"):
                        self.assertEqual(result.returncode, 128)
                        self.assertIn(b"no man viewer handled the request", result.stderr)
                    else:
                        record = captures[path]
                        self.assertEqual((result.returncode, result.stdout, result.stderr),
                                         (record["status"], record["stdout"].encode(),
                                          record["stderr"].encode()))

    def test_patch_context_parser_and_hunk_selection(self):
        self.file.write_text(self.original.replace("line 10\n", "changed\n"))
        for cmd in (("stash",), ("stash", "push")):
            for options in (("-U",), ("--unified",), ("--inter-hunk-context",)):
                result = self.invoke(*cmd, "-p", *options)
                self.assertEqual(result.returncode, 129, (cmd, options, result.stderr))
            if self.version == (2, 43):
                self.assertEqual(self.invoke(*cmd, "-p", "-U0").returncode, 129)
            else:
                self.assertEqual(self.invoke(*cmd, "-U0").returncode, 128)
                self.assertEqual(self.invoke(*cmd, "-p", "-U-2").returncode, 128)
                zero = self.invoke(*cmd, "-p", "-U0", input_bytes=b"y\n")
                self.assertEqual(zero.returncode, 1)
                self.assertIn(b"@@ -11 +11 @@", zero.stdout)
                self.assertIn(b"patch does not apply", zero.stderr)
                for form in (("-U1",), ("-U", "1"), ("--unified=1",), ("--unified", "1")):
                    out = self.git(*cmd, "-p", *form, "--inter-hunk-context=0", input_bytes=b"y\n")
                    self.assertIn(b"@@ -10,3 +10,3 @@", out)
                    self.git("stash", "pop", "-q")
                self.git(*cmd, "-U-1")  # Sentinel retains the normal, noninteractive default.
                self.git("stash", "pop", "-q")
            self.assertEqual(self.invoke(*cmd, "--no-auto-advance").returncode, 129)

    def test_implicit_push_boundary_and_untracked_negation(self):
        self.file.write_text("modified\n")
        untracked = self.repo / "loose"
        untracked.write_text("keep\n")
        self.assertNotEqual(self.invoke("stash", "tracked").returncode, 0)
        self.git("stash", "-u", "--no-include-untracked", "--", "tracked")
        self.assertTrue(untracked.is_file())
        self.assertEqual(self.file.read_text(), self.original)
        self.git("stash", "pop", "-q")
        for switch in ("-p", "--patch"):
            result = self.invoke("stash", switch, "tracked", input_bytes=b"y\n")
            self.assertEqual(result.returncode, 0 if self.version == (2, 53) else 128)
            if result.returncode == 0:
                self.git("stash", "pop", "-q")

    def test_saved_index_ignored_files_and_nul_pathspecs(self):
        self.file.write_text("staged\n")
        self.git("add", "tracked")
        other = self.repo / "line\nbreak"
        other.write_text("save separately\n")
        ignored = self.repo / "private.tmp"
        ignored.write_text("ignored\n")
        (self.repo / ".git/info").mkdir(exist_ok=True)
        (self.repo / ".git/info/exclude").write_text("*.tmp\n")
        self.git("stash", "push", "--keep-index", "-u")
        self.assertEqual(self.git("diff", "--cached", "--name-only"), b"tracked\n")
        self.assertEqual(self.git("show", "stash^2:tracked"), b"staged\n")
        self.assertFalse(other.exists())
        self.assertTrue(ignored.is_file())
        self.git("stash", "push", "--all", "--no-keep-index")
        self.assertFalse(ignored.exists())
        self.assertEqual(self.git("diff", "--cached", "--name-only"), b"")
        self.assertEqual(self.git("show", "stash^2:tracked"), b"staged\n")
        other.write_text("tracked at base\n")
        self.git("add", "--", other.name)
        self.git("commit", "-qm", "newline path")
        other.write_text("new file contents\n")
        self.file.write_text("unstaged unrelated\n")
        self.git("stash", "push", "--pathspec-from-file=-", "--pathspec-file-nul",
                 input_bytes=b"line\nbreak\0")
        self.assertEqual(other.read_text(), "tracked at base\n")
        self.assertEqual(self.file.read_text(), "unstaged unrelated\n")
        other.write_text("staged separately\n")
        self.git("add", "--", other.name)
        self.git("stash", "push", "--staged")
        self.assertEqual(self.git("diff", "--cached", "--name-only"), b"")
        self.assertEqual(self.file.read_text(), "unstaged unrelated\n")

    def test_index_configuration_pop_conflict_and_labels(self):
        self.file.write_text("stash version\n")
        self.git("add", "tracked")
        self.git("stash", "push", "-qm", "index fixture")
        saved = self.git("rev-parse", "stash")
        self.git("config", "stash.index", "true")
        self.git("stash", "apply")
        self.assertEqual(bool(self.git("diff", "--cached", "--name-only")), self.version == (2, 53))
        self.git("restore", "--source=HEAD", "--staged", "--worktree", "tracked")
        self.git("stash", "apply", "--no-index")
        self.assertEqual(self.git("diff", "--cached", "--name-only"), b"")
        self.assertEqual(self.git("rev-parse", "stash"), saved)
        self.file.write_text("competing\n")
        self.git("commit", "-qam", "competing edit")
        for action in ("apply", "pop"):
            for label in ("--label-ours", "--label-theirs", "--label-base"):
                self.assertEqual(self.invoke("stash", action, label + "=custom").returncode, 129)
        self.assertEqual(self.invoke("stash", "pop", "--no-index").returncode, 1)
        self.assertTrue(self.git("ls-files", "-u"))
        self.assertEqual(self.git("rev-parse", "stash"), saved)

    def test_export_import_ownership_and_round_trip(self):
        self.file.write_text("for export\n")
        self.git("stash", "push", "-qm", "export fixture")
        saved = self.git("rev-parse", "stash")
        self.assertNotEqual(self.invoke("stash", "--print").returncode, 0)
        if self.version == (2, 43):
            self.assertNotEqual(self.invoke("stash", "export", "--print").returncode, 0)
            self.assertNotEqual(self.invoke("stash", "import", "HEAD").returncode, 0)
            return
        self.assertNotEqual(self.invoke("stash", "export", "--to-ref").returncode, 0)
        tip = self.git("stash", "export", "--print").strip()
        self.git("stash", "export", "--to-ref", "refs/fixture/exported")
        self.assertEqual(self.git("rev-parse", "refs/fixture/exported").strip(), tip)
        self.git("stash", "clear")
        self.git("stash", "import", tip.decode())
        self.assertEqual(self.git("rev-parse", "stash"), saved)

    def test_new_branch_and_existing_branch_reset(self):
        base = self.git("rev-parse", "HEAD")
        self.git("branch", "topic")
        self.file.write_text("new tip\n")
        self.git("commit", "-qam", "tip")
        tip = self.git("rev-parse", "HEAD")
        self.assertNotEqual(base, tip)
        worktree = self.base / "topic-worktree"
        self.assertNotEqual(self.invoke("worktree", "add", "-b", "topic", worktree).returncode, 0)
        self.assertEqual(self.git("rev-parse", "topic"), base)
        self.git("worktree", "add", "-B", "topic", worktree)
        self.assertEqual(self.git("-C", worktree, "rev-parse", "HEAD"), tip)
        self.assertEqual(self.git("rev-parse", "topic"), tip)

    def test_tracking_operand_orphan_and_relative_link_files(self):
        track = self.base / "tracked-branch"
        for arg in ("--track=direct", "--track=inherit"):
            self.assertEqual(self.invoke("worktree", "add", arg, "-b", "topic", track, "main").returncode, 129)
        self.git("worktree", "add", "--track", "-b", "topic", track, "main")
        self.assertEqual(self.git("config", "branch.topic.merge").strip(), b"refs/heads/main")
        orphan = self.base / "unborn"
        self.git("worktree", "add", "--orphan", orphan)
        self.assertEqual(self.git("-C", orphan, "ls-files"), b"")
        self.assertNotEqual(self.invoke("-C", orphan, "rev-parse", "--verify", "HEAD").returncode, 0)
        rel = self.base / "relative"
        result = self.invoke("worktree", "add", "--relative-paths", "-d", rel)
        if self.version == (2, 43):
            self.assertEqual(result.returncode, 129)
        else:
            self.assertEqual(result.returncode, 0, result.stderr)
            target = (rel / ".git").read_text().strip().removeprefix("gitdir: ")
            self.assertFalse(Path(target).is_absolute())
            self.assertEqual(self.git("config", "extensions.relativeWorktrees").strip(), b"true")
            self.git("config", "worktree.useRelativePaths", "true")
            absolute = self.base / "absolute"
            self.git("worktree", "add", "--no-relative-paths", "-d", absolute)
            self.assertTrue(Path((absolute / ".git").read_text().strip().removeprefix("gitdir: ")).is_absolute())

    def test_expiry_annotation_and_locked_removal(self):
        missing = self.base / "missing"
        self.git("worktree", "add", "-d", missing)
        shutil.rmtree(missing)
        records = self.git("worktree", "list", "--porcelain", "-z", "--expire", "now")
        self.assertIn(b"\0prunable ", records)
        self.assertTrue(records.endswith(b"\0\0"))
        self.assertIn(b"\0\0worktree ", records)
        self.assertNotIn(b"prunable", self.git("worktree", "list", "--porcelain", "--no-expire"))
        self.git("worktree", "prune", "--no-expire")
        self.assertIn(os.fsencode(missing), self.git("worktree", "list", "--porcelain"))
        self.git("worktree", "prune", "--expire", "now")
        self.assertNotIn(os.fsencode(missing), self.git("worktree", "list", "--porcelain"))
        locked = self.base / "locked"
        self.git("worktree", "add", "-d", "--lock", "--reason", "fixture lock", locked)
        self.assertNotEqual(self.invoke("worktree", "remove", "--force", locked).returncode, 0)
        self.assertTrue(locked.is_dir())
        self.git("worktree", "remove", "--force", "--force", locked)
        self.assertFalse(locked.exists())
