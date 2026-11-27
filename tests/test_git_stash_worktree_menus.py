"""Exercise the bundled Git menus with discovery disabled and pending commands held in Readline."""

import json
import re
import shlex
import sys
import time
import unittest

from test_terminal_screen import PROMPT, ROOT, TMUX_AVAILABLE, TerminalTestCase

sys.path.insert(0, str(ROOT / "cli_help"))
from core import HelpError, find_context, insert_option
from presentation import option_label, option_text
from ui import ellipsize_cells

# Original selectable literals, in display order. A colon separates a required placeholder.
PUSH = ("-p --patch -S --staged -k --keep-index --no-keep-index -u --include-untracked "
        "-a --all -m:MESSAGE --message:MESSAGE -q --quiet --pathspec-from-file:FILE --pathspec-file-nul")
STASH_WORKTREE = {
    "stash": PUSH,
    "stash push": PUSH,
    "stash apply": "--index -q --quiet",
    "stash pop": "--index -q --quiet",
    "stash list": "--oneline --stat -p --patch -n:COUNT --max-count=:COUNT --format=:FORMAT --date=:FORMAT --grep=:PATTERN",
    "stash show": "-p --patch --stat --name-only --name-status -u --include-untracked --only-untracked --binary",
    "worktree": "-h add list remove prune",
    "worktree add": "-f --force --detach -b:BRANCH -B:BRANCH --checkout --no-checkout --lock --reason:REASON -q --quiet",
    "worktree list": "--porcelain -z -v --verbose",
    "worktree prune": "-n --dry-run -v --verbose --expire:TIME",
    "worktree remove": "-f --force",
}

ORIGINAL = {
    **STASH_WORKTREE,
    "commit": "--message:MESSAGE --file:FILE --edit --all --patch --amend --dry-run --verbose --short",
    "log": ("--oneline --graph --decorate --stat --patch --max-count=:COUNT "
            "--author=:PATTERN --grep=:PATTERN --since=:DATE --all"),
}


def profile(path):
    """Load the exact bundled command path, including its local value definitions."""
    name = "git-" + path.replace(" ", "-") + ".json"
    return json.loads((ROOT / "profiles" / name).read_text(encoding="utf-8"))


def options(data):
    return [row for category in data["categories"] for row in category["options"]]


class GitInventoryTests(unittest.TestCase):
    def test_original_literals_placeholders_order_and_cursor(self):
        """Pin the original edits independently of additions and new optional operands."""
        for path, declarations in ORIGINAL.items():
            data = profile(path)
            original = dict(declaration.partition(":")[::2] for declaration in declarations.split())
            rows = options(data)
            indexed = {row["flag"]: row for row in rows}
            self.assertEqual(len(rows), len(indexed), path)
            self.assertEqual([row["flag"] for row in rows if row["flag"] in original], list(original), path)
            prefix, suffix = f"git {path} ", '  "quoted suffix"'
            context = find_context(prefix + suffix, len(prefix), [data])
            for flag, placeholder in original.items():
                row = indexed[flag]
                with self.subTest(path=path, flag=flag):
                    if placeholder:
                        self.assertEqual(row.get("argument"), placeholder)
                        self.assertFalse(row.get("argument_optional"))
                    self.assertEqual(insert_option(context, row),
                                     (prefix + flag + suffix, len(prefix + flag) + int(not flag.endswith("="))))

    def test_release_usage_and_root_dispatch(self):
        """Compare root keywords with captured synopses, then follow every promoted keyword."""
        profiles = [profile(path) for path in STASH_WORKTREE]
        for release in ("noble", "resolute"):
            capture = json.loads((ROOT / "tests/fixtures/git-stash-worktree" /
                                  (release + "-usage.json")).read_text(encoding="utf-8"))
            for path in STASH_WORKTREE:
                item = capture["usage"][path]
                self.assertEqual(item["argv"], ["git", *path.split(), "-h"])
                self.assertEqual(item["status"], 129)
                self.assertEqual(item["stderr"], "")
                self.assertTrue(item["stdout"].startswith("usage: git " + path.split()[0]))
            for root in ("stash", "worktree"):
                synopsis = capture["usage"][root]["stdout"].split("\n\n", 1)[0]
                keywords = set(re.findall(r"git " + root + r" \[?([a-z]+)", synopsis))
                bundled = {row["flag"] for row in options(profile(root)) if row.get("kind") == "keyword"}
                self.assertEqual(keywords, bundled - ({"export", "import"} if release == "noble" and root == "stash" else set()))
                for keyword in keywords:
                    line = f"git {root} {keyword} "
                    if root + " " + keyword in ORIGINAL:
                        selected = find_context(line, len(line), profiles)
                        self.assertEqual(selected.profile["command"], line.split())
                    else:
                        with self.assertRaises(HelpError) as error:
                            find_context(line, len(line), profiles)
                        self.assertEqual(error.exception.code, "unsupported_subcommand")


@unittest.skipUnless(TMUX_AVAILABLE, "Rendered-screen tests require Linux and tmux")
class GitMenuTests(TerminalTestCase):
    def pending(self, prefix, suffix, columns, rows):
        """Install an execution marker before entering the pending line at its edit point."""
        shell = self.start()
        shell.text("git() { printf executed > " + shlex.quote(str(shell.executed)) + "; }")
        shell.keys("Enter")
        shell.wait_for(lambda screen: screen.cells[screen.y] == PROMPT.rstrip())
        shell.resize(columns, rows)
        shell.text(prefix + suffix)
        if suffix:
            shell.keys(*(["Left"] * len(suffix)))
        return shell

    def test_all_rows_summaries_and_complete_details(self):
        for path in STASH_WORKTREE:
            self.check_rendered_rows(path)

    def test_commit_rows_and_details(self):
        self.check_rendered_rows("commit")

    def test_log_rows_and_details(self):
        self.check_rendered_rows("log")

    def check_rendered_rows(self, path):
        """Read the selected row and every visible Details line, including formatted value guidance."""
        data = profile(path)
        prefix, suffix = f"git {path} ", ' "quoted suffix"'
        shell = self.pending(prefix, suffix, 240, 150)
        shell.verify_profile(data)
        shell.cancel()
        self.assertEqual(shell.read_buffer(), (prefix + suffix, len(prefix)))
        self.assertFalse(shell.executed.exists())

    def test_root_keyword_and_end_of_options_in_readline(self):
        """Select a child command, open its own menu and stop at the pathspec separator."""
        shell = self.pending("git stash pu", "", 60, 16)
        shell.open_menu()
        shell.keys("Right")
        shell.wait_for(lambda state: state.selected_row.startswith("> push "))
        shell.cancel("Enter")
        self.assertEqual(shell.read_buffer(), ("git stash push ", len("git stash push ")))
        self.assertTrue(shell.open_menu().cells[0].startswith("Interactive help | git stash push "))
        shell.cancel()
        shell.text("-- 'a path' ")
        shell.keys("Escape", "h")
        shell.wait_for(lambda state: state.alternate == 0 and "end_of_options" in " ".join(state.cells))
        line = "git stash push -- 'a path' "
        self.assertEqual(shell.read_buffer(), (line, len(line)))
        self.assertFalse(shell.executed.exists())

    def test_log_original_bare_optional_insertions(self):
        """Select the two original optional flags before an existing revision and path."""
        for flag in ("--decorate", "--stat"):
            prefix, suffix = "git log ", ' HEAD -- "quoted suffix"'
            shell = self.pending(prefix + flag, suffix, 60, 16)
            screen = shell.open_menu()
            self.assertIn("> " + flag, screen.cells[4])
            shell.cancel("Enter")
            self.assertEqual(shell.read_buffer(), (prefix + flag + suffix, len(prefix + flag) + 1))
            self.assertFalse(shell.executed.exists())

    def test_log_count_optional_arguments_and_path_boundary(self):
        """Open log after complete options and reject edits inside its path operands."""
        prefix = "git log -2 --decorate=full --stat=30 HEAD "
        suffix = ' -- "quoted suffix"'
        shell = self.pending(prefix, suffix, 60, 16)
        self.assertTrue(shell.open_menu().cells[0].startswith("Interactive help | git log "))
        shell.cancel()
        self.assertEqual(shell.read_buffer(), (prefix + suffix, len(prefix)))
        shell.keys("C-e", "Space", "Escape", "h")
        shell.wait_for(lambda state: state.alternate == 0 and "end_of_options" in " ".join(state.cells))
        line = prefix + suffix + " "
        self.assertEqual(shell.read_buffer(), (line, len(line)))
        self.assertFalse(shell.executed.exists())

    def test_commit_pathspec_input_file(self):
        self.check_search_and_insert("commit", "pathspec input file", "--pathspec-from-file=",
                                     "Omit command-line pathspecs.", ' "names list"')

    def test_log_line_history(self):
        self.check_search_and_insert("log", "line history", "-L",
                                     "Pathspec arguments are incompatible.", ' "1,3:file name"')

    def test_new_manual_terms_scroll_cancel_and_literal_operands(self):
        cases = (
            ("worktree list", "list annotation", "--expire", "No registrations are deleted.", ' "2 weeks ago"'),
            ("stash show", "tree comparison descends", "--max-depth=", "Ubuntu 24.04 rejects this option.", ' "stash@{0}"'),
        )
        for path, query, literal, qualification, suffix in cases:
            self.check_search_and_insert(path, query, literal, qualification, suffix)

    def check_search_and_insert(self, path, query, literal, qualification, suffix):
        """Scroll to a qualification before cancelling and selecting the same option."""
        prefix = f"git {path} "
        shell = self.pending(prefix, suffix, 60, 16)
        for action in ("Escape", "Enter"):
            with self.subTest(path=path, action=action):
                self.assertEqual(shell.open_menu().cells[2].rstrip(), "")
                shell.keys("/")
                shell.text(query)
                shell.keys("Enter")
                screen = shell.wait_for(lambda state: state.cells[2] == "Filter: " + query)
                self.assertTrue(screen.selected_row.startswith("> " + ellipsize_cells(literal.rstrip("="), 15)),
                                screen.selected_row)
                shell.find_detail(qualification)
                shell.cancel(action)
                if action == "Escape":
                    self.assertEqual(shell.read_buffer(), (prefix + suffix, len(prefix)))
                else:
                    point = len(prefix + literal) + int(not literal.endswith("="))
                    self.assertEqual(shell.read_buffer(), (prefix + literal + suffix, point))
        self.assertFalse(shell.executed.exists())
