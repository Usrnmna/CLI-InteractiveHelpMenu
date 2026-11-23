"""Pin the manual forms and observe stash show in a repository created for the test."""

import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cli_help"))
from core import HelpError, find_context, insert_option


class StashShowCoverageTests(unittest.TestCase):
    def setUp(self):
        self.profile = json.loads((ROOT / "profiles/git-stash-show.json").read_text())
        self.rows = [row for category in self.profile["categories"] for row in category["options"]]

    def test_manual_inventory_and_release_captures(self):
        """Compare independent manual syntax, including arity, with every menu declaration."""
        manual = (ROOT / "docs/git-stash-show-inventory.md").read_text().split("## Ownership")[0]
        declarations = {}
        for line in manual.splitlines():
            if not line.startswith("| `"):
                continue
            spellings, release, _ = line.strip("|").split("|")
            for spelling in re.findall(r"`([^`]+)`", spellings):
                flag, operand = re.fullmatch(r"(--[a-z-]+|-[a-zA-Z])(.*)", spelling).groups()
                self.assertNotIn(flag, declarations)
                declarations[flag] = operand
                self.assertEqual(release.strip(), "Resolute and upstream" if flag == "--max-depth" else "All")
        self.assertCountEqual(declarations, [row["flag"] for row in self.rows])
        for row in self.rows:
            flag = row["flag"]
            operand = declarations[flag]
            with self.subTest(flag=flag):
                self.assertEqual(bool(row.get("argument")), bool(operand))
                self.assertEqual(row.get("argument_optional", False), operand.startswith("["))
                if operand:
                    self.assertIn("value_semantics", row)
                    if flag == "--stat":
                        self.assertEqual(row["argument"], operand)
                    else:
                        self.assertEqual(row["argument_style"], "equals" if flag.startswith("--") else "attached_only")
                        expected = operand[1:-1] if operand.startswith("[") else operand
                        placeholder = row["argument"]
                        if not flag.startswith("--") and operand.startswith("["):
                            placeholder = placeholder[1:-1]
                        self.assertEqual(placeholder, expected.removeprefix("="))
        for release in ("noble", "resolute"):
            capture = json.loads((ROOT / "tests/fixtures/git-stash-worktree" / (release + "-usage.json")).read_text())
            record = capture["usage"]["stash show"]
            self.assertEqual((record["argv"], record["status"], record["stderr"]), (["git", "stash", "show", "-h"], 129, ""))
            self.assertIn("[<diff-options>]", record["stdout"])
            self.assertIn("--only-untracked", record["stdout"])

    def test_bare_stat_and_attached_operands(self):
        options = {row["flag"]: row for row in self.rows}
        prefix, suffix = "git stash show ", " 'stash@{0}'"
        edit = find_context(prefix + suffix, len(prefix), [self.profile])
        self.assertEqual(insert_option(edit, options["--stat"]), (prefix + "--stat" + suffix, len(prefix + "--stat ")))
        self.assertEqual(insert_option(edit, options["--output"]), (prefix + "--output=" + suffix, len(prefix + "--output=")))
        for done in ("-U0", "--stat=78,20,3", "-G'new lines'", "--output='new file'"):
            line = prefix + done + " -"
            self.assertEqual(find_context(line, len(line), [self.profile]).profile, self.profile)
        for done in ("-G", "--output"):
            line = prefix + done + " word -"
            with self.assertRaises(HelpError):
                find_context(line, len(line), [self.profile])


@unittest.skipUnless(shutil.which("git"), "Git executable required")
class StashShowPackagedTests(unittest.TestCase):
    def test_stash_diff_operands_and_depth(self):
        """Check the comparison result, changed-path set and return status on a two-depth stash."""
        with tempfile.TemporaryDirectory(prefix="cli-help-git-show-") as directory:
            base = Path(directory)
            repo = base / "repo"
            repo.mkdir()
            env = {"HOME": directory, "PATH": os.defpath, "LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1",
                   "GIT_CONFIG_GLOBAL": os.devnull, "GIT_ATTR_NOSYSTEM": "1", "GIT_PAGER": "cat",
                   "GIT_ALLOW_PROTOCOL": "", "GIT_TERMINAL_PROMPT": "0"}

            def git(*args, check=True):
                return subprocess.run(["git", *args], cwd=repo, env=env, stdin=subprocess.DEVNULL,
                                      capture_output=True, check=check, timeout=15)

            git("init", "--quiet", "--template=", "--initial-branch=main")
            git("config", "core.hooksPath", os.devnull)
            git("config", "user.name", "Fixture")
            git("config", "user.email", "fixture@example.invalid")
            (repo / "data").mkdir()
            for name in ("top", "data/deep"):
                (repo / name).write_text("a\nb\nc\nd\n")
            git("add", ".")
            git("commit", "-qm", "base")
            for name in ("top", "data/deep"):
                (repo / name).write_text("a\nb\nc\nchanged\n")
            (repo / "new").write_text("untracked\n")
            git("stash", "push", "-qu", "-m", "fixture")

            def show(*args, check=True):
                return git("stash", "show", *args, check=check)

            self.assertEqual(show("--only-untracked", "--name-only").stdout, b"new\n")
            self.assertIn(b":040000 040000 ", show("-t", "--raw").stdout)
            self.assertEqual(show("-t", "--name-status").stdout, b"M\tdata\nM\tdata/deep\nM\ttop\n")
            self.assertEqual(show("-r", "--raw").stdout, show("--raw").stdout)
            self.assertIn(b" new ", show("-u").stdout)
            self.assertNotIn(b"b/new", show("-U").stdout)
            self.assertIn(b"@@ -4 +4 @@", show("-U0").stdout)
            self.assertEqual(show("-U", "0").stdout, show("-U").stdout)
            self.assertIn(b"...\n", show("--stat=30,10,1").stdout)
            self.assertEqual(show("--stat", "30", check=False).returncode, 128)
            # The separate word selects a stash. Compare with the same lookup
            # directly because Git releases assign different failure statuses.
            direct = show("nonexistent", check=False)
            separate = show("--output", "nonexistent", check=False)
            self.assertNotEqual(direct.returncode, 0)
            self.assertIn(b"nonexistent is not a valid reference", direct.stderr)
            self.assertEqual((separate.returncode, separate.stdout, separate.stderr),
                             (direct.returncode, b"", direct.stderr))
            self.assertFalse((repo / "nonexistent").exists())
            self.assertNotEqual(show("--", "top", check=False).returncode, 0)
            show("--output=diff.txt", "-p")
            self.assertIn(b"diff --git", (repo / "diff.txt").read_bytes())
            self.assertEqual(show("--quiet", check=False).returncode, 1)
            self.assertEqual(show("--exit-code", check=False).returncode, 1)
            git("config", "stash.showIncludeUntracked", "true")
            self.assertEqual(show("--name-only").stdout, b"data/deep\nnew\ntop\n")
            self.assertEqual(show("--no-include-untracked", "--name-only").stdout, b"data/deep\ntop\n")
            git("config", "stash.showIncludeUntracked", "false")
            version = git("--version").stdout
            if b" 2.43." in version:
                self.assertEqual(show("--max-depth=0", check=False).returncode, 129)
                self.assertEqual(show("-Gchanged", "--name-only").stdout, b"data/deep\ntop\n")
            elif b" 2.53." in version:
                self.assertEqual(show("--max-depth=0", "--name-only").stdout, b"data\ntop\n")
                self.assertEqual(show("--max-depth=1", "--name-only").stdout, b"data/deep\ntop\n")
                self.assertEqual(show("--max-depth=0", "-u", check=False).returncode, 128)
                self.assertEqual(show("--max-depth=0", "--only-untracked", "--name-only").stdout, b"new\n")
