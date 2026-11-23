"""Compare stash list with its manual inventory and exercise delegated Git behavior."""

import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cli_help"))
from arguments import value_forms
from core import find_context


class ListInventoryTests(unittest.TestCase):
    def test_manual_inventory_and_accepted_argument_forms(self):
        """Every documented list spelling has a unique row with the correct operand boundary."""
        profile = json.loads((ROOT / "profiles/git-stash-list.json").read_text())
        rows = {row["flag"]: row for cat in profile["categories"] for row in cat["options"]}
        inventory = (ROOT / "docs/git-stash-list-inventory.md").read_text()
        table = inventory.split("## Selectable inventory\n", 1)[1].split("\n## ", 1)[0]
        encountered = []
        for line in table.splitlines():
            if not line.startswith("| `-"):
                continue
            spellings, operand, attachment, _ = line.strip("| ").split(" | ")
            for flag in re.findall(r"`([^`]+)`", spellings):
                encountered.append(flag)
                with self.subTest(flag=flag):
                    row = rows[flag]
                    self.assertEqual(bool(row.get("argument")), operand != "—")
                    if operand != "—":
                        expected = operand.strip("`")
                        if flag == "--stat":
                            expected = "[=" + expected + "]"
                        elif attachment == "short attached, long =" and not flag.startswith("--"):
                            expected = "[" + expected + "]"
                        self.assertEqual(row["argument"], expected)
                        self.assertEqual(row.get("argument_optional", False),
                                         "optional" in attachment or attachment == "short attached, long =")
                        if attachment == "= only":
                            self.assertEqual(value_forms(row), {"equals"})
                        elif attachment == "= or separate":
                            self.assertEqual(value_forms(row), {"equals", "separate"})
                        elif attachment == "attached or separate":
                            self.assertEqual(value_forms(row), {"attached", "separate"})
                        self.assertIn("value_semantics", row)
        self.assertCountEqual(encountered, rows.keys())
        for edited in ("-3", "-0", "-n -1", "-n3", "--max-count=-2", "-U0", "--stat=20,10,1"):
            line = f"git stash list {edited} --"
            self.assertEqual(find_context(line, len(line), [profile]).profile["command"],
                             ["git", "stash", "list"], edited)


class StashListBehaviorTests(unittest.TestCase):
    def setUp(self):
        """Create two distinguishable stashes and a separate ref log in a private repository."""
        scratch = tempfile.TemporaryDirectory(prefix="git-stash-list-")
        self.addCleanup(scratch.cleanup)
        root = Path(scratch.name)
        self.repo = root / "repo"
        self.repo.mkdir()
        self.env = {
            "PATH": os.defpath, "LC_ALL": "C", "HOME": str(root),
            "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_ALLOW_PROTOCOL": "", "GIT_TERMINAL_PROMPT": "0", "GIT_PAGER": "cat",
            "GIT_AUTHOR_DATE": "2020-01-01T00:00:00Z",
            "GIT_COMMITTER_DATE": "2020-01-01T00:00:00Z",
        }
        self.git("init", "--quiet", "-b", "main")
        self.git("config", "user.name", "Stash Fixture")
        self.git("config", "user.email", "fixture@example.invalid")
        for name in ("one", "two"):
            (self.repo / name).write_text("base\n")
        self.git("add", ".")
        self.git("commit", "--quiet", "-m", "base")
        (self.repo / "one").write_text("first\n")
        self.git("stash", "push", "-qm", "first")
        for name in ("one", "two"):
            (self.repo / name).write_text("second\n")
        (self.repo / "extra").write_text("untracked\n")
        self.git("stash", "push", "-qu", "-m", "second")
        # Change the reflog subject without changing the stash commit's message.
        object_id = self.git("rev-parse", "refs/stash").stdout.strip()
        self.git("stash", "drop", "-q")
        self.git("stash", "store", "-m", "reflog-marker", object_id)

    def git(self, *args, data=None, check=True):
        """Run Git with isolated configuration and capture both streams and the child status."""
        return subprocess.run(["git", *args], cwd=self.repo, env=self.env, input=data,
                              capture_output=True, check=check, timeout=10)

    def test_entry_count_message_and_reflog_controls(self):
        def run(*args):
            return self.git("stash", "list", *args).stdout

        self.assertEqual(run("--grep-reflog=reflog-marker", "--format=%s"), b"On main: second\n")
        self.assertEqual(run("--grep=reflog-marker"), b"")
        self.assertEqual(run("--grep=second", "--format=%gs"), b"reflog-marker\n")
        self.assertEqual(run("--skip=1", "--max-count=1", "--format=%s"), b"On main: first\n")
        self.assertEqual(run("--skip=-1"), run("-n", "-1"))
        self.assertEqual(run("-0"), b"")
        self.assertIn(b"main@{0}", run("--branches"))
        self.assertEqual(run("--min-parents=3", "--format=%gs"), b"reflog-marker\n")

    def test_path_selection_and_patch_operand_boundaries(self):
        names = ["stash", "list", "--stdin", "--name-only", "--format=%s"]
        limited = self.git(*names, data=b"--\ntwo\n").stdout
        broadened = self.git(*names, "--full-diff", data=b"--\ntwo\n").stdout
        self.assertIn(b"two\n", limited)
        self.assertNotIn(b"one\n", limited)
        self.assertIn(b"one\n", broadened)
        self.assertNotIn(b"On main: first", broadened)
        self.assertIn(b"diff --git", self.git("stash", "list", "-u").stdout)
        self.assertNotIn(b"extra", self.git("stash", "list", "-u").stdout)
        self.assertIn(b"diff --git", self.git("stash", "list", "-U0").stdout)
        for args in (("-U", "0"), ("--stat", "20"), ("--format", "%s"), ("--reverse",)):
            self.assertNotEqual(self.git("stash", "list", *args, check=False).returncode, 0, args)
        self.assertIn(b"files changed", self.git("stash", "list", "--stat=20,10,1").stdout)
        self.assertEqual(self.git("stash", "list", "--quiet").stdout, self.git("stash", "list").stdout)
        self.assertEqual(self.git("stash", "list", "--exit-code", check=False).returncode, 1)
