"""Root declarations from versioned Ubuntu providers sharing manuals, launchers or multicall binaries."""

import csv
import hashlib
import json
import re
import shlex
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from test_terminal_screen import PROMPT, ROOT, TMUX_AVAILABLE, TerminalTestCase

sys.path.insert(0, str(ROOT / "cli_help"))
from core import HelpError, find_context, insert_option, validate_profile
from discovery import Settings, build_profile, discover
from ubuntu_reference import lookup_record, reference_profile


def menu(command, target, edition):
    """Read a reference for the supplied executable identity and flatten its rendered rows."""
    record = lookup_record(command, edition, str(Path(target).parent), target)
    profile = reference_profile(record, build_profile, validate_profile)
    return profile, {row["flag"]: row for category in profile["categories"] for row in category["options"]}


class UbuntuProviderRootTests(unittest.TestCase):
    def test_fixed_help_documents_and_alias_ownership(self):
        """Compare every advertised spelling with three independent, successful fixed replies."""
        for name, target in (("apport-bug", "/usr/bin/apport-bug"),
                             ("apport-collect", "/usr/bin/apport-bug"),
                             ("dbxtool", "/usr/bin/dbxtool")):
            with self.subTest(name=name):
                capture = (ROOT / "tests/fixtures/ubuntu-coverage/provider-help" / name).read_bytes()
                profile, options = menu(name, target, "resolute")
                self.assertEqual(profile["discovery"]["reference_sha256"], hashlib.sha256(capture).hexdigest())
                advertised = set()
                for line in capture.decode().splitlines():
                    if line.startswith("  -"):
                        advertised.update(re.findall(r"--?[a-zA-Z][a-zA-Z-]*", line.partition("    ")[0]))
                self.assertEqual(set(options), advertised)
        for edition in ("noble", "resolute"):
            with self.subTest(edition=edition):
                filing = menu("apport-bug", "/usr/bin/apport-bug", edition)[1]
                collecting = menu("apport-collect", "/usr/bin/apport-bug", edition)[1]
                self.assertEqual(collecting["--package"]["argument_count"], 1)
                self.assertNotIn("--package", filing)
                self.assertNotIn("--save", collecting)
                self.assertEqual(filing["--save"]["argument_style"], "separate")

    def test_root_words_and_flag_value_boundaries(self):
        """Exercise one-word choices, leaf-only syntax, separated values and literal insertions."""
        for edition in ("noble", "resolute"):
            for name, target, flag, excluded in (
                ("axfer", "/usr/bin/axfer", "transfer", "capture"),
                ("gnome-keyring", "/usr/bin/gnome-keyring-3", "import", "certificate-exception"),
                ("linux-version", "/usr/bin/linux-version", "compare", "--reverse"),
                ("lpc", "/usr/sbin/lpc", "status", "?"),
            ):
                with self.subTest(edition=edition, name=name):
                    profile, options = menu(name, target, edition)
                    self.assertNotIn(excluded, options)
                    self.assertEqual(options[flag]["kind"], "keyword")
                    line = name + " " + flag[:2] + "\t'preserve this'"
                    ctx = find_context(line, line.index("\t"), [profile])
                    self.assertEqual(insert_option(ctx, options[flag])[0], name + " " + flag + "\t'preserve this'")
            with self.subTest(edition=edition, name="Yelp aliases"):
                for name in ("yelp", "gnome-help"):
                    _, options = menu(name, "/usr/bin/yelp", edition)
                    self.assertEqual(set(options), {"-h", "--help", "--editor-mode", "--version"})
            for name, path, flag, style in (
                ("git-shell", "/usr/bin/git-shell", "-c", "separate"),
                ("create-cracklib-dict", "/usr/sbin/create-cracklib-dict", "--output", "separate"),
                ("lesskey", "/usr/bin/lesskey", "--output", "equals"),
                ("dbxtool", "/usr/bin/dbxtool", "--dbx", "equals"),
            ):
                with self.subTest(edition=edition, name=name):
                    profile, options = menu(name, path, edition)
                    self.assertEqual(options[flag]["argument_count"], 1)
                    self.assertEqual(options[flag]["argument_style"], style)
                    for line in (name + " -- ", name + " 'a positional operand' "):
                        with self.assertRaises(HelpError):
                            find_context(line, len(line), [profile])

    def test_netfilter_dispatch_and_stdin_boundary(self):
        """Compare the exact bridge save, bridge restore, ARP restore and legacy save entry points."""
        nft = "/usr/sbin/xtables-nft-multi"
        _, save = menu("ebtables-save", nft, "resolute")
        _, restore = menu("ebtables-restore", nft, "resolute")
        self.assertEqual(set(save), {"-c", "--counters", "-M", "--modprobe", "-t", "--table", "-V", "--version"})
        self.assertEqual(set(restore), {"-n", "--noflush", "-v", "--verbose"})
        for entry in ("arptables-restore", "arptables-nft-restore"):
            record = lookup_record(entry, "resolute", "/usr/sbin", nft)
            self.assertEqual(record["package"], "iptables")
            with self.assertRaisesRegex(HelpError, "standard input"):
                reference_profile(record, build_profile, validate_profile)
        for edition in ("noble", "resolute"):
            for name in ("iptables-legacy-save", "ip6tables-legacy-save"):
                with self.subTest(edition=edition, name=name):
                    _, options = menu(name, "/usr/sbin/xtables-legacy-multi", edition)
                    self.assertEqual(options["--file"]["argument_style"], "equals")
                    self.assertIn("--dump", options)
                    self.assertNotIn("--binary", options)
                    self.assertNotIn("--noflush", options)

    def test_packaged_providers_keep_each_switch_in_its_own_grammar(self):
        """Replay a source-specific root choice and a foreign or downstream spelling per invocation."""
        fixture = ROOT / "tests/fixtures/ubuntu-coverage/provider-help/root-boundaries.tsv"
        with fixture.open(encoding="utf-8", newline="") as source:
            for case in csv.DictReader(source, delimiter="\t"):
                name = case["Invocation"]
                with self.subTest(name=name):
                    _, options = menu(name, case["Resolved executable"], "resolute")
                    row = options[case["Selectable spelling"]]
                    if row.get("kind") == "keyword":
                        shape = "keyword"
                    else:
                        shape = row.get("argument_style", "none")
                    self.assertEqual(shape, case["Value style"])
                    self.assertNotIn(case["Excluded root spelling"], options)

    def test_fixed_discovery_uses_passive_reference(self):
        """A stripped image must resolve this alias without forwarding user words to a child."""
        with patch("ubuntu_reference.ubuntu_edition", return_value="resolute"), \
                patch("discovery.shutil.which", side_effect=lambda n: "/usr/bin/dbxtool" if n == "dbxtool" else None), \
                patch("discovery.installed_reference", side_effect=lambda record: record), patch("discovery.executable_identity", return_value={}), \
                patch("discovery.run_probe", side_effect=AssertionError("unexpected probe")):
            line = "dbxtool --db 'unrelated argument'"
            ctx = find_context(line, len("dbxtool --db"), [], lambda cmd: discover(cmd, Settings()))
            options = {row["flag"]: row for category in ctx.profile["categories"] for row in category["options"]}
            self.assertEqual(insert_option(ctx, options["--dbx"]), ("dbxtool --dbx= 'unrelated argument'", 14))


@unittest.skipUnless(TMUX_AVAILABLE, "Rendered-screen tests require Linux and tmux")
class ProviderInsertionScreenTests(TerminalTestCase):
    def test_cracklib_output_remains_a_separate_word(self):
        """Inspect the compiled profile in a small shell, cancel and insert before a quoted filename."""
        shell = self.start()
        profiles = shell.folder / "profiles"
        profiles.mkdir()
        command = "create-cracklib-dict"
        profile, _ = menu(command, "/usr/sbin/" + command, "resolute")
        (profiles / "cracklib.json").write_text(json.dumps(profile))
        shell.text("export CLI_HELP_PROFILES=" + shlex.quote(str(profiles)) +
                   "; " + command + "() { printf executed > " + shlex.quote(str(shell.executed)) + "; }")
        shell.keys("Enter")
        shell.wait_for(lambda state: state.cells[state.y] == PROMPT.rstrip())
        shell.resize(60, 16)
        prefix, suffix = command + " --out", " 'word list'"
        shell.text(prefix + suffix)
        shell.keys(*(["Left"] * len(suffix)))
        for action in ("Escape", "Enter"):
            shell.open_menu()
            shell.find_detail("Write the dictionary under this path prefix.")
            shell.cancel(action)
            if action == "Escape":
                self.assertEqual(shell.read_buffer(), (prefix + suffix, len(prefix)))
        final = command + " --output"
        self.assertEqual(shell.read_buffer(), (final + suffix, len(final) + 1))
        self.assertFalse(shell.executed.exists())
