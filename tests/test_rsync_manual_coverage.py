"""Reconcile rsync declarations and exercise packaged transfers and the bundled menu."""

import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

from test_terminal_screen import ROOT, TMUX_AVAILABLE, TerminalTestCase

sys.path.insert(0, str(ROOT / "cli_help"))
from presentation import option_label, option_text
from ui import Browser


def rsync_profile():
    """Load the bundled profile from the current test snapshot."""
    return json.loads((ROOT / "profiles/rsync.json").read_text(encoding="utf-8"))


def inventory_rows():
    """Read the independent declarations from the versioned manual comparison."""
    audit = (ROOT / "docs/rsync-manual-coverage.md").read_text(encoding="utf-8")
    for line in audit.splitlines():
        if line.startswith("| `-"):
            flag, aliases, operand, mode, releases = line.strip("| ").split(" | ")
            yield (flag.strip("`"), re.findall(r"`([^`]+)`", aliases), operand,
                   mode, releases)


def help_declarations(text):
    """Read option headings without interpreting option examples in the prose."""
    for line in text.splitlines():
        if line.startswith("-"):
            heading = re.split(r"\s{2,}", line)[0]
            fields = heading.removesuffix(" (*)").split(", ")
            names = [field.partition("=")[0] for field in fields]
            yield names, "=" in heading


class RsyncInventoryTests(unittest.TestCase):
    def test_manual_declarations_and_aliases_match_the_menu(self):
        """Compare literal insertion, operand arity, scope and discoverability."""
        profile = rsync_profile()
        browser = Browser(profile)
        rows = [(option, category["name"]) for category in profile["categories"]
                for option in category["options"]]
        by_flag = {option["flag"].removesuffix("="): (option, category)
                   for option, category in rows}
        primary = []
        spellings = []
        for name, aliases, operand, mode, releases in inventory_rows():
            with self.subTest(flag=name):
                primary.append(name)
                spellings.extend([name, *aliases])
                option, category = by_flag[name]
                takes_value = operand != "—"
                self.assertEqual(option["flag"], name + ("=" if takes_value else ""))
                self.assertEqual(option.get("argument"), operand.strip("`") if takes_value else None)
                self.assertFalse(option.get("argument_optional"))
                self.assertIn(mode, {"client", "daemon", "both"})
                visible = " ".join((category, *browser.text(option).details))
                if mode in {"daemon", "both"}:
                    self.assertIn("daemon", visible.lower())
                self.assertIn(releases, {"all", "upstream only"})
                if releases == "upstream only":
                    self.assertIn("3.5", visible)
                for alias in aliases:
                    self.assertRegex(visible, r"(?<![\w-])" + re.escape(alias) + r"(?![\w-])")
                    self.assertIn(alias.casefold(), browser.text(option).searchable)
        self.assertCountEqual(primary, [option["flag"].removesuffix("=") for option, _ in rows])
        self.assertEqual(len(primary), len(set(primary)))
        self.assertEqual((len(primary), len(spellings), len(set(spellings))), (216, 308, 306))
        self.assertNotIn("--no-OPTION", primary)

    def test_both_release_captures_agree_with_inventory(self):
        """A packaged declaration must resolve in its own mode with matching arity."""
        rows = list(inventory_rows())
        for release in ("noble", "resolute"):
            for mode in ("client", "daemon"):
                with self.subTest(release=release, mode=mode):
                    capture = ROOT / f"tests/fixtures/rsync/{release}-{mode}.txt"
                    declarations = list(help_declarations(capture.read_text(encoding="utf-8")))
                    self.assertEqual(len(declarations), 144 if mode == "client" else 14)
                    for names, takes_value in declarations:
                        if names == ["--no-OPTION"]:
                            self.assertEqual(mode, "client")
                            continue
                        matches = [(name, operand) for name, aliases, operand, applies, releases in rows
                                   if applies in {mode, "both"} and releases != "upstream only"
                                   and set(names) <= {name, *aliases}]
                        self.assertEqual(len(matches), 1, (release, mode, names))
                        self.assertEqual(takes_value, matches[0][1] != "—", names)


class PackagedRsyncTests(unittest.TestCase):
    def setUp(self):
        """Use a private tree and a clean client environment for every local transfer."""
        self.binary = os.environ.get("RSYNC_TEST_BINARY") or shutil.which("rsync")
        if not self.binary:
            self.skipTest("Local rsync executable unavailable")
        tmp = tempfile.TemporaryDirectory(prefix="cli-help-rsync-")
        self.addCleanup(tmp.cleanup)
        self.folder = Path(tmp.name)
        self.src = self.folder / "src"
        self.dst = self.folder / "dest"
        self.src.mkdir()
        self.dst.mkdir()

    def rsync(self, *args):
        """Only fixed arguments and paths within the disposable tree reach the client."""
        env = {key: value for key, value in os.environ.items() if not key.startswith("RSYNC_")}
        env.update(HOME=str(self.folder), LC_ALL="C")
        return subprocess.run([self.binary, *args], cwd=self.folder, env=env,
                              check=True, capture_output=True, text=True, timeout=15).stdout

    def test_packaged_help_matches_captured_declarations(self):
        """Check both fixed help modes on a release covered by the captured evidence."""
        version = re.search(r"rsync +version ([0-9.]+)", self.rsync("--version")).group(1)
        release = {"3.2.7": "noble", "3.4.1": "resolute"}.get(version)
        if release is None:
            self.skipTest(f"No release-matched help capture for rsync {version}")
        for mode, args in (("client", ["--help"]), ("daemon", ["--daemon", "--help"])):
            with self.subTest(mode=mode):
                capture = ROOT / f"tests/fixtures/rsync/{release}-{mode}.txt"
                expected = list(help_declarations(capture.read_text(encoding="utf-8")))
                self.assertEqual(list(help_declarations(self.rsync(*args))), expected)

        for unsupported in ("--no-OPTION", "--no-archive"):
            with self.subTest(unsupported=unsupported):
                with self.assertRaises(subprocess.CalledProcessError) as failure:
                    self.rsync(unsupported, "-rni", "src/", "dest/")
                self.assertIn("unknown option", failure.exception.stderr)
        if "no crtimes" in self.rsync("--version"):
            with self.assertRaises(subprocess.CalledProcessError) as failure:
                self.rsync("--crtimes", "-rni", "src/", "dest/")
            self.assertIn("does not support --crtimes", failure.exception.stderr)

    def test_client_and_daemon_bandwidth_grammars(self):
        """Exercise both rate parsers without opening a network connection."""
        for rate in ("0.1B", "0", "512B"):
            with self.subTest(client=rate):
                self.rsync("-rni", "--bwlimit=" + rate, "src/", "dest/")
        for rate in ("1B", "511B"):
            with self.subTest(client=rate), self.assertRaises(subprocess.CalledProcessError) as error:
                self.rsync("-rni", "--bwlimit=" + rate, "src/", "dest/")
            self.assertIn("too small", error.exception.stderr)
        self.assertIn("--daemon", self.rsync("--daemon", "--bwlimit=2", "--help"))
        for rate in ("1K", "1.5"):
            with self.subTest(daemon=rate), self.assertRaises(subprocess.CalledProcessError) as error:
                self.rsync("--daemon", "--bwlimit=" + rate, "--help")
            self.assertIn("invalid numeric value", error.exception.stderr)

    def test_negation_order_changes_directory_recursion(self):
        (self.src / "leaf").touch()
        self.rsync("-a", "--no-recursive", "src", "dest/")
        self.assertEqual(list(self.dst.iterdir()), [])
        self.rsync("--no-recursive", "-a", "src", "dest/")
        self.assertTrue((self.dst / "src/leaf").is_file())

    def test_source_directory_versus_its_contents(self):
        (self.src / "leaf").touch()
        self.rsync("-r", "src", "dest/")
        self.assertEqual(list(self.dst.iterdir()), [self.dst / "src"])
        self.assertTrue((self.dst / "src/leaf").is_file())
        self.rsync("-r", "src/", "dest/")
        self.assertTrue((self.dst / "leaf").is_file())

    def test_archive_files_from_requires_explicit_recursion(self):
        (self.src / "subdir").mkdir()
        (self.src / "subdir/leaf").touch()
        (self.folder / "names").write_text("subdir\n", encoding="utf-8")
        self.rsync("-a", "--files-from=names", "src/", "dest/")
        self.assertEqual(list((self.dst / "subdir").iterdir()), [])
        self.rsync("-ar", "--files-from=names", "src/", "dest/")
        self.assertTrue((self.dst / "subdir/leaf").is_file())

    def test_receiver_protection_during_deletion_preview(self):
        protected = self.dst / "excluded"
        extraneous = self.dst / "other"
        protected.touch()
        extraneous.touch()
        flags = ["-rni", "--delete", "--exclude=excluded"]
        ordinary = self.rsync(*flags, "src/", "dest/")
        self.assertRegex(ordinary, r"\*deleting\s+other")
        self.assertNotIn("excluded", ordinary)
        preview = self.rsync(*flags, "--delete-excluded", "src/", "dest/")
        self.assertRegex(preview, r"\*deleting\s+excluded")
        self.assertRegex(preview, r"\*deleting\s+other")
        self.assertTrue(protected.exists() and extraneous.exists())


@unittest.skipUnless(TMUX_AVAILABLE, "Rendered-screen tests require Linux and tmux")
class RsyncMenuTests(TerminalTestCase):
    def pending_rsync(self, columns, rows):
        """Place the cursor in an empty option slot before two quoted operands."""
        shell = self.start()
        shell.resize(columns, rows)
        prefix, suffix = "rsync ", " 'source dir/' 'destination dir/'"
        shell.text(prefix + suffix)
        shell.keys(*(["Left"] * len(suffix)))
        return shell, prefix, suffix

    def test_each_summary_and_complete_details_are_visible(self):
        profile = rsync_profile()
        shell, prefix, suffix = self.pending_rsync(210, 110)
        shell.verify_profile(profile)
        shell.cancel()
        self.assertEqual(shell.read_buffer(), (prefix + suffix, len(prefix)))
        self.assertFalse(shell.executed.exists())

    def find_option(self, shell, query, flag):
        """Search an unfiltered 60-column menu and navigate to the matching row."""
        menu = shell.open_menu()
        self.assertEqual(menu.cells[2].rstrip(), "Filter:")
        shell.keys("/")
        shell.text(query)
        shell.keys("Enter")
        state = shell.wait_for(lambda s: s.cells[2] == "Filter: " + query)
        browser = Browser(rsync_profile(), query=query)
        for category in range(len(browser.profile["categories"])):
            for index, option in enumerate(browser.options(category)):
                if option["flag"] == flag:
                    current = int(state.cells[1].split()[1].split("/")[0]) - 1
                    moves = ["Right" if category > current else "Left"] * abs(category - current)
                    shell.keys(*moves, "Home", *(["Down"] * index))
                    return shell.wait_for(lambda s: s.selected_row.startswith("> " + flag))
        self.fail(f"Search for {query!r} omitted {flag}")

    def test_small_menu_search_scroll_restore_and_literal_insertion(self):
        shell, prefix, suffix = self.pending_rsync(60, 16)
        for query, flag in (("sender I/O errors", "--delete"), ("rsyncd.conf", "--config="),
                            ("--protect-args", "--secluded-args"), ("--files-from", "--files-from=")):
            with self.subTest(query=query):
                state = self.find_option(shell, query, flag)
                if flag == "--delete":
                    expected = "Sender I/O errors stop deletions unless --ignore-errors is set."
                    shell.find_detail(expected)
                shell.cancel()
                self.assertEqual(shell.read_buffer(), (prefix + suffix, len(prefix)))
                self.assertFalse(shell.executed.exists())
        self.find_option(shell, "--files-from", "--files-from=")
        shell.cancel("Enter")
        inserted = prefix + "--files-from="
        self.assertEqual(shell.read_buffer(), (inserted + suffix, len(inserted)))
        self.assertFalse(shell.executed.exists())
