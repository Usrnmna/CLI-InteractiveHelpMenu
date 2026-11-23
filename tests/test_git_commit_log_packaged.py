"""Exercise commit selection, history walks and fixed usage in disposable Git repositories."""

import json
import os
import shutil
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures"


class PackagedGitTests(unittest.TestCase):
    def setUp(self):
        """Use a private home, empty template and deterministic fixture-local identities."""
        scratch = tempfile.TemporaryDirectory(prefix="cli-help-commit-log-")
        self.addCleanup(scratch.cleanup)
        self.base = Path(scratch.name)
        self.repo = self.base / "repository"
        self.repo.mkdir()
        home = self.base / "home"
        home.mkdir()
        self.env = {
            "HOME": str(home), "LC_ALL": "C", "PATH": os.defpath,
            "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_ATTR_NOSYSTEM": "1", "GIT_ALLOW_PROTOCOL": "", "GIT_TERMINAL_PROMPT": "0",
            "GIT_EDITOR": "true", "GIT_PAGER": "cat",
            "GIT_AUTHOR_DATE": "1999-01-01T00:00:00Z",
            "GIT_COMMITTER_DATE": "2020-01-01T00:00:00Z",
        }
        self.git("init", "-q", "-b", "main", "--template=")
        self.git("config", "user.name", "Fixture")
        self.git("config", "user.email", "fixture@example.invalid")
        self.git("config", "gc.auto", "0")

    def invoke(self, *args, data=b""):
        """Run Git against this test's repository, retaining stdout, stderr and exit status."""
        return subprocess.run(["git", *args], cwd=self.repo, env=self.env, input=data,
                              capture_output=True, timeout=10)

    def git(self, *args, data=b""):
        """Require success and return stdout, preserving newlines and embedded NULs."""
        result = self.invoke(*args, data=data)
        self.assertEqual(result.returncode, 0, (args, result.stdout, result.stderr))
        return result.stdout

    def release(self):
        """Select a retained capture only for a matching packaged Git version."""
        version = self.git("--version").decode().strip()
        by_version = {"git version 2.43.0": "noble", "git version 2.53.0": "resolute"}
        if version not in by_version:
            self.skipTest(f"No matching release capture for {version}")
        return by_version[version]

    def test_fixed_help_and_historical_sources(self):
        """The live fixed invocation preserves the original stream, status and literal spellings."""
        capture = json.loads((FIXTURES / "git-commit-log" / (self.release() + "-usage.json")).read_text())
        historical = json.loads((FIXTURES / "help/captured.json").read_text())
        for command, original in (("commit", ("-m", "--amend", "--dry-run")),
                                  ("log", ("--all", "--oneline", "--max-count="))):
            with self.subTest(command=command):
                record = capture["usage"][command]
                self.assertEqual(record["argv"], ["git", command, "-h"])
                self.assertEqual(record["status"], 129)
                result = self.invoke(command, "-h")
                self.assertEqual((result.returncode, result.stdout.decode(), result.stderr.decode()),
                                 (record["status"], record["stdout"], record["stderr"]))
                excerpt = historical["git " + command]
                self.assertEqual(excerpt["source"], ["man", "git-" + command])
                self.assertEqual(excerpt["version"], "git version 2.43.0")
                specimen = (FIXTURES / "help" / ("git-" + command + ".txt")).read_text()
                for spelling in original:
                    self.assertIn(spelling, excerpt["text"])
                    self.assertIn(spelling, specimen)

    def test_staged_snapshot_explicit_path_include_all_and_patch(self):
        """Compare every tracked blob in HEAD and the remaining index after each selection mode."""
        paths = ("staged", "chosen", "deleted")
        for path in paths:
            (self.repo / path).write_bytes(b"base\n")
        self.git("add", ".")
        self.git("commit", "-qm", "base")
        base = self.git("rev-parse", "HEAD").decode().strip()
        cases = [
            ((), ("staged",), ()),
            (("--", "chosen"), ("chosen",), ("staged",)),
            (("--only", "--", "chosen"), ("chosen",), ("staged",)),
            (("--include", "--", "chosen"), ("staged", "chosen"), ()),
            (("--all",), ("staged", "chosen", "deleted"), ()),
            (("--patch", "--", "chosen"), ("staged", "chosen"), ()),
            (("--interactive",), ("staged",), ()),
        ]
        for args, changed, remaining in cases:
            with self.subTest(args=args):
                # Each case branches from identical contents in this disposable repository.
                self.git("switch", "--detach", "--discard-changes", base)
                (self.repo / "staged").write_bytes(b"index\n")
                self.git("add", "staged")
                (self.repo / "chosen").write_bytes(b"worktree\n")
                (self.repo / "deleted").unlink()
                (self.repo / "loose").write_bytes(b"untracked\n")
                data = b"q\n" if "--interactive" in args else b"y\n"
                self.git("commit", "-qm", "selected", *args, data=data)
                self.assertEqual(set(self.git("diff", "--name-only", base, "HEAD").decode().splitlines()),
                                 set(changed))
                self.assertEqual(set(self.git("diff", "--cached", "--name-only").decode().splitlines()),
                                 set(remaining))
                for path in paths:
                    if path == "deleted" and path in changed:
                        self.assertEqual(self.git("ls-files", "--", path), b"")
                        continue
                    blob = b"base\n"
                    if path in changed:
                        blob = b"index\n" if path == "staged" else b"worktree\n"
                    self.assertEqual(self.git("show", "HEAD:" + path), blob)
                    self.assertEqual(self.git("show", ":" + path), b"index\n" if path in remaining else blob)
                self.assertEqual(self.git("ls-files", "--", "loose"), b"")

    def test_include_unmatched_path_with_unrelated_staging(self):
        """Check whether an unmatched include path stops a prepared commit on each package."""
        release = self.release()
        path = self.repo / "staged"
        path.write_bytes(b"base")
        self.git("add", "staged")
        self.git("commit", "-qm", "base")
        original = self.git("rev-parse", "HEAD")
        path.write_bytes(b"pending")
        self.git("add", "staged")
        result = self.invoke("commit", "--include", "-m", "selection", "--", "absent")
        self.assertEqual(self.git("show", ":staged"), b"pending")
        if release == "noble":
            self.assertEqual(result.returncode, 0)
            self.assertEqual(self.git("rev-parse", "HEAD^"), original)
            self.assertEqual(self.git("show", "HEAD:staged"), b"pending")
        else:
            self.assertEqual(result.returncode, 128)
            self.assertEqual(self.git("rev-parse", "HEAD"), original)
            self.assertEqual(self.git("show", "HEAD:staged"), b"base")

    def test_amend_only_and_nul_pathspec(self):
        """Message-only amendment preserves the staged change; a NUL pathspec can name a newline."""
        name = "line\nbreak"
        for path in ("staged", name):
            (self.repo / path).write_bytes(b"base\n")
        self.git("add", ".")
        self.git("commit", "-qm", "base")
        original_tree = self.git("rev-parse", "HEAD^{tree}")
        (self.repo / "staged").write_bytes(b"index\n")
        self.git("add", "staged")
        self.assertEqual(self.invoke("commit", "--only", "-m", "invalid").returncode, 128)
        self.git("commit", "--amend", "--only", "-qm", "new subject")
        self.assertEqual(self.git("rev-parse", "HEAD^{tree}"), original_tree)
        self.assertEqual(self.git("show", ":staged"), b"index\n")
        (self.repo / name).write_bytes(b"selected\n")
        self.git("commit", "-qm", "newline", "--pathspec-from-file=-", "--pathspec-file-nul",
                 data=os.fsencode(name) + b"\0")
        self.assertEqual(self.git("show", "HEAD:" + name), b"selected\n")
        self.assertEqual(self.git("show", "HEAD:staged"), b"base\n")
        self.assertEqual(self.git("diff", "--cached", "--name-only"), b"staged\n")

    def test_status_formats_signoff_and_verification(self):
        """Distinguish status previews, actual commit, message trailer and hook bypass."""
        (self.repo / "tracked").write_bytes(b"new\n")
        self.git("add", "tracked")
        for args in [("-z",), ("--null",), ("--porcelain",), ("--short",), ("--long",)]:
            preview = self.git("commit", *args, "-m", "unused")
            if args in (("-z",), ("--null",)):
                self.assertEqual(preview, b"A  tracked\0")
            self.assertNotEqual(self.invoke("rev-parse", "--verify", "HEAD").returncode, 0)
        for version in ("v1", "v2"):
            self.assertEqual(self.invoke("commit", "--porcelain=" + version).returncode, 129)
        hooks = self.base / "hooks"
        hooks.mkdir()
        veto = hooks / "pre-commit"
        veto.write_text("#!/bin/sh\necho fixture-veto >&2\nexit 1\n")
        veto.chmod(0o700)
        self.git("config", "core.hooksPath", str(hooks))
        blocked = self.invoke("commit", "-n", "--verify", "-m", "blocked")
        self.assertEqual((blocked.returncode, blocked.stderr), (1, b"fixture-veto\n"))
        self.git("commit", "--verify", "-n", "--branch", "-s", "-qm", "signed off")
        self.assertIn(b"Signed-off-by: Fixture <fixture@example.invalid>", self.git("show", "-s", "--format=%B"))
        self.assertNotIn(b"gpgsig ", self.git("cat-file", "commit", "HEAD"))

    def test_patch_context_counts_and_modes(self):
        """Check operand attachment, default sentinels and the hunk actually offered."""
        release = self.release()
        original = "".join(f"line {i}\n" for i in range(20))
        path = self.repo / "tracked"
        path.write_text(original)
        self.git("add", "tracked")
        self.git("commit", "-qm", "base")
        path.write_text(original.replace("line 10\n", "changed\n"))
        for flag in ("-U", "--unified", "--inter-hunk-context"):
            self.assertEqual(self.invoke("commit", "-p", "-m", "context", flag).returncode, 129)
        forms = [("-U1",), ("-U", "1"), ("--unified", "1"), ("--unified=1",)]
        if release == "noble":
            for args in [*forms, ("--inter-hunk-context=0",)]:
                self.assertEqual(self.invoke("commit", "-p", "-m", "context", *args).returncode, 129)
            return
        for args in forms:
            self.assertEqual(self.invoke("commit", "-m", "ordinary", *args).returncode, 128)
            declined = self.invoke("commit", "-p", "-m", "declined", *args, data=b"n\n")
            self.assertEqual(declined.returncode, 1)
            self.assertIn(b"@@ -10,3 +10,3 @@", declined.stdout)
        for flag in ("--unified", "--inter-hunk-context"):
            self.assertEqual(self.invoke("commit", "-p", "-m", "invalid", flag + "=-2").returncode, 128)
            self.assertEqual(self.invoke("commit", "-m", "invalid", flag + "=0").returncode, 128)
        declined = self.invoke("commit", "-p", "-m", "default", "-U-1", data=b"n\n")
        self.assertIn(b"@@ -8,7 +8,7 @@", declined.stdout)
        self.assertIn(b"@@ -11 +11 @@", self.invoke("commit", "-p", "-m", "zero", "-U0", data=b"n\n").stdout)
        self.git("commit", "-a", "-qm", "sentinels", "-U-1", "--inter-hunk-context=-1")
        self.assertEqual(self.git("show", "HEAD:tracked").decode(), path.read_text())

    def test_counts_dates_optional_values_and_paths(self):
        """Distinguish early traversal termination, output counts and optional attached values."""
        for subject, year in [("ancestor", 2010), ("barrier", 2000), ("tip", 2011)]:
            self.env["GIT_COMMITTER_DATE"] = f"{year}-01-01T00:00:00Z"
            (self.repo / "tracked").write_text(subject)
            self.git("add", "tracked")
            self.git("commit", "-qm", subject)
        log = ("log", "--format=%s")
        self.assertEqual(self.git(*log, "-2"), b"tip\nbarrier\n")
        self.assertEqual(self.git(*log, "--max-count=-2"), b"tip\nbarrier\nancestor\n")
        self.assertEqual(self.git(*log, "-0"), b"")
        self.assertEqual(self.git(*log, "-2", "--reverse"), b"barrier\ntip\n")
        self.assertEqual(self.git(*log, "--since=2005-01-01T00:00:00Z"), b"tip\n")
        self.assertEqual(self.git(*log, "--since-as-filter=2005-01-01T00:00:00Z"), b"tip\nancestor\n")
        self.assertEqual(self.git(*log, "HEAD~1..HEAD", "--", "tracked"), b"tip\n")
        self.assertEqual(self.git(*log, "HEAD", "--", "-2"), b"")
        for args in (("--decorate", "full"), ("--stat", "20")):
            self.assertEqual(self.invoke(*log, *args).returncode, 128)
        self.assertIn(b"refs/heads/main", self.git("log", "-1", "--oneline", "--decorate=full"))
        self.assertIn(b"tracked |", self.git(*log, "-1", "--stat=20"))
        self.assertEqual(self.invoke(*log, "--grep-reflog=barrier").returncode, 128)
        self.assertEqual(self.git(*log, "-g", "--grep-reflog=barrier"), b"barrier\n")

    def test_merge_traversal_and_diff(self):
        """Separate first-parent traversal from requesting a merge's first-parent patch."""
        self.git("commit", "-qm", "base", "--allow-empty")
        self.git("switch", "-qc", "topic")
        (self.repo / "topic").write_bytes(b"topic\n")
        self.git("add", "topic")
        self.git("commit", "-qm", "topic")
        self.git("switch", "-q", "main")
        self.git("commit", "-qm", "main work", "--allow-empty")
        self.git("merge", "-q", "--no-ff", "-m", "merge", "topic")
        self.assertEqual(self.git("log", "--format=%s", "--first-parent"), b"merge\nmain work\nbase\n")
        self.assertNotIn(b"diff --git", self.git("log", "-1", "--patch"))
        self.assertIn(b"diff --git a/topic b/topic",
                      self.git("log", "-1", "--patch", "--diff-merges=first-parent"))

    def test_pickaxe_line_history_and_reflog_walk(self):
        """Keep an occurrence count stable across an edit, then compare walks of the same history."""
        path = self.repo / "tracked"
        for subject, line in (("introduce", "first needle"), ("rewrite", "revised needle"),
                              ("remove", "absent")):
            path.write_text(line + "\n")
            self.git("add", "tracked")
            self.git("commit", "-qm", subject)
        log = ("log", "--format=%s")
        self.assertEqual(self.git(*log, "-Sneedle"), b"remove\nintroduce\n")
        self.assertEqual(self.git(*log, "-Gneedle"), b"remove\nrewrite\nintroduce\n")
        self.assertEqual(self.git(*log, "--reverse", "HEAD~2..HEAD"), b"rewrite\nremove\n")
        self.assertEqual(self.invoke(*log, "-g", "--reverse").returncode, 128)
        self.assertEqual(self.invoke(*log, "-g", "HEAD~2..HEAD").returncode, 128)
        history = self.git(*log, "-L1,1:tracked", "HEAD")
        self.assertIn(b"rewrite\n", history)
        self.assertIn(b"+revised needle", history)
        self.assertEqual(self.invoke(*log, "-L1,1:tracked", "HEAD", "--", "tracked").returncode, 128)

    def test_help_all_and_manual_viewer(self):
        """An inert man viewer identifies long-help dispatch without starting a real pager."""
        viewer_dir = self.base / "viewer"
        viewer_dir.mkdir()
        viewer = viewer_dir / "man"
        viewer.write_text("#!/bin/sh\nprintf 'manual %s\\n' \"$@\"\n")
        viewer.chmod(0o700)
        # Git looks up its manual viewer in PATH, independently of the repository's help text.
        executable = shutil.which("git", path=self.env["PATH"])
        for command in ("commit", "log"):
            with self.subTest(command=command):
                result = subprocess.run([executable, command, "--help"], cwd=self.repo,
                                        env={**self.env, "PATH": str(viewer_dir)}, capture_output=True, timeout=10)
                self.assertEqual((result.returncode, result.stdout), (0, f"manual git-{command}\n".encode()))
                short = self.invoke(command, "-h")
                extended = self.invoke(command, "--help-all")
                # Built-in help returns 129 on the two Ubuntu packages and 0 on Git 2.56.
                self.assertIn(short.returncode, (0, 129))
                self.assertEqual(extended.returncode, short.returncode)
                for usage in (short, extended):
                    self.assertIn(f"usage: git {command}".encode(), usage.stdout + usage.stderr)
                self.assertGreaterEqual(len(extended.stdout + extended.stderr), len(short.stdout + short.stderr))

    def test_fixup_reword_preserves_staged_content(self):
        """Plain fixup records the index; reword amends a message while preserving that index."""
        path = self.repo / "tracked"
        path.write_bytes(b"base\n")
        self.git("add", "tracked")
        self.git("commit", "-qm", "subject", "-m", "original body")
        base = self.git("rev-parse", "HEAD").decode().strip()
        path.write_bytes(b"pending\n")
        self.git("add", "tracked")
        self.git("commit", "--fixup=reword:" + base)
        self.assertEqual(self.git("show", "-s", "--format=%s"), b"amend! subject\n")
        self.assertIn(b"original body", self.git("show", "-s", "--format=%b"))
        self.assertEqual(self.git("show", "HEAD:tracked"), b"base\n")
        self.assertEqual(self.git("show", ":tracked"), b"pending\n")
        self.git("commit", "--fixup=" + base, "-m", "comment")
        self.assertEqual(self.git("show", "-s", "--format=%s"), b"fixup! subject\n")
        self.assertIn(b"comment", self.git("show", "-s", "--format=%b"))
        self.assertEqual(self.git("show", "HEAD:tracked"), b"pending\n")
