"""Exercise Ubuntu provider argument boundaries in the parser, menu and Bash adapter."""

import hashlib
import json
import shlex
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from test_terminal_screen import PROMPT, ROOT, TMUX_AVAILABLE, TmuxShell

sys.path.insert(0, str(ROOT / "cli_help"))
from core import HelpError, find_context, insert_option, validate_profile
from discovery import Settings, build_profile, discover
from ubuntu_reference import lookup_record, reference_profile


def menu(command, target, edition="resolute"):
    """Build the edition's menu for an exact provider path and index its selectable rows."""
    record = lookup_record(command, edition, str(Path(target).parent), target)
    profile = reference_profile(record, build_profile, validate_profile)
    options = {row["flag"]: row for category in profile["categories"] for row in category["options"]}
    return profile, options


class UbuntuProviderArgumentsTests(unittest.TestCase):
    def test_nmtui_activities_are_owned_only_by_the_root(self):
        """Compare the shortcut with its captured help and keep root activities off all shortcuts."""
        root, choices = menu("nmtui", "/usr/bin/nmtui")
        self.assertEqual(set(choices), {"edit", "connect", "hostname", "-h", "--help"})
        line = "nmtui con\t'Office Wi-Fi'"
        context = find_context(line, line.index("\t"), [root])
        self.assertEqual(insert_option(context, choices["connect"])[0], "nmtui connect\t'Office Wi-Fi'")
        capture = (ROOT / "tests/fixtures/ubuntu-coverage/provider-help/nmtui-edit").read_bytes()
        for name in ("nmtui-edit", "nmtui-connect", "nmtui-hostname"):
            with self.subTest(name=name):
                profile, choices = menu(name, "/usr/bin/nmtui")
                self.assertEqual(set(choices), {"-h", "--help"})
                if name == "nmtui-edit":
                    self.assertEqual(profile["discovery"]["reference_sha256"], hashlib.sha256(capture).hexdigest())
                    self.assertIn(b"-h, --help", capture)

    def test_required_operands_and_literal_edits(self):
        """Protect distinct tuple, attached, equals and separate argument boundaries."""
        for name, target, flag, arity, style in (
            ("spdsend", "/usr/bin/spdsend", "--open", 2, None),
            ("spdsend", "/usr/bin/spdsend", "--send", 1, "separate"),
            ("rsync-ssl", "/usr/bin/rsync-ssl", "--type", 1, "equals"),
            ("ps2ps2", "/usr/bin/ps2ps2", "-sPAPERSIZE", 1, "equals"),
            ("perl5.40.1", "/usr/bin/perl5.40.1", "-I", 1, "attached_only"),
            ("tclsh", "/usr/bin/tclsh8.6", "-encoding", 1, "separate"),
            ("spa-json-dump", "/usr/bin/spa-json-dump", "--indent", 1, "separate"),
            ("mailmail3", "/usr/bin/mailmail3", "-F", 1, "separate"),
            ("mountsnoop-bpfcc", "/usr/sbin/mountsnoop-bpfcc", "--cgroupmap", 1, "separate"),
            ("pod2html", "/usr/bin/pod2html", "--htmlroot", 1, "equals"),
            ("pdb3", "/usr/bin/pdb3.14", "--pid", 1, "separate"),
        ):
            with self.subTest(name=name, flag=flag):
                profile, choices = menu(name, target)
                opt = choices[flag]
                self.assertEqual((opt["argument_count"], opt.get("argument_style")), (arity, style))
                partial = flag[:max(1, len(flag) - 1)]
                line = name + " " + partial + "\t'keep this'"
                context = find_context(line, line.index("\t"), [profile])
                suffix = "=" if style == "equals" else ""
                self.assertEqual(insert_option(context, opt)[0], name + " " + flag + suffix + "\t'keep this'")
        profile, _ = menu("spdsend", "/usr/bin/spdsend")
        for line in ("spdsend --open ", "spdsend --open server ", "spdsend --send ", "spdsend -- "):
            with self.subTest(line=line), self.assertRaises(HelpError):
                find_context(line, len(line), [profile])

    def test_stale_manuals_and_sibling_options(self):
        """Confirm exact spellings and reject stale or differently owned flags."""
        for name, target, present, absent in (
            ("netaddr", "/usr/bin/netaddr", "info", "--ipython-dir"),
            ("setvesablank", "/usr/sbin/setvesablank", "ON", "--blanking"),
            ("pydoc3", "/usr/bin/pydoc3.14", "-b", "-g"),
            ("psfaddtable", "/usr/bin/psfxtable", "-V", "-it"),
            ("mailmail3", "/usr/bin/mailmail3", "-t", "-bp"),
            ("rsync-ssl", "/usr/bin/rsync-ssl", "--type", "--HELPER"),
            ("xtables-legacy-multi", "/usr/sbin/xtables-legacy-multi", "ip6tables-save", "-A"),
            ("zfgrep", "/usr/bin/zfgrep", "--file", "--recursive"),
            ("shadowconfig", "/usr/sbin/shadowconfig", "on", "off"),
        ):
            with self.subTest(name=name):
                _, options = menu(name, target)
                self.assertIn(present, options)
                self.assertNotIn(absent, options)

    def test_missing_manual_reaches_reference_without_workload_probe(self):
        """Route a buffer with trailing operands to the passive fallback using an exact executable."""
        target = "/usr/bin/rsync-ssl"
        with patch("ubuntu_reference.ubuntu_edition", return_value="resolute"), \
                patch("discovery.shutil.which", side_effect=lambda name: target if name == "rsync-ssl" else None), \
                patch("discovery.installed_reference", side_effect=lambda record: record), patch("discovery.executable_identity", return_value={}), \
                patch("discovery.run_probe", side_effect=AssertionError("unexpected executable probe")):
            line = "rsync-ssl --ty 'saved path'"
            context = find_context(line, len("rsync-ssl --ty"), [], lambda cmd: discover(cmd, Settings()))
            self.assertIn("reference_sha256", context.profile["discovery"])
            option = context.profile["categories"][0]["options"][0]
            self.assertEqual(insert_option(context, option)[0], "rsync-ssl --type= 'saved path'")

    def test_noble_and_resolute_use_their_own_interfaces(self):
        """Keep newer parser additions out of the older edition's usage and command rows."""
        for name, target, newer in (
            ("threadsnoop-bpfcc", "/usr/sbin/threadsnoop-bpfcc", "--help"),
            ("netaddr", "/usr/bin/netaddr", "info"),
            ("spa-json-dump", "/usr/bin/spa-json-dump", "--indent"),
        ):
            with self.subTest(name=name):
                _, choices = menu(name, target)
                self.assertIn(newer, choices)
                with self.assertRaises(HelpError) as guidance:
                    menu(name, target, "noble")
                self.assertEqual(guidance.exception.code, "usage_guidance")
        for edition, has_vars in (("resolute", True), ("noble", False)):
            with self.subTest(edition=edition):
                _, choices = menu("pw-cli", "/usr/bin/pw-cli", edition)
                self.assertIn("list-objects", choices)
                self.assertEqual("list-vars" in choices, has_vars)
                self.assertEqual("lv" in choices, has_vars)


@unittest.skipUnless(TMUX_AVAILABLE, "Rendered display requires tmux on Linux")
class UbuntuProviderArgumentsScreenTests(unittest.TestCase):
    def test_equals_argument_through_readline(self):
        """Inspect the reference row at 60×16, cancel, then insert ahead of a quoted operand."""
        with tempfile.TemporaryDirectory(prefix="cli-help-provider-") as directory:
            folder = Path(directory)
            profiles = folder / "profiles"
            profiles.mkdir()
            profile, _ = menu("rsync-ssl", "/usr/bin/rsync-ssl")
            (profiles / "rsync-ssl.json").write_text(json.dumps(profile))
            shell = TmuxShell(folder, profile_directory=profiles)
            try:
                shell.text("rsync-ssl() { touch " + shlex.quote(str(shell.executed)) + "; }")
                shell.keys("Enter")
                shell.wait_for(lambda state: state.cells[state.y] == PROMPT.rstrip())
                shell.resize(60, 16)
                prefix, suffix = "rsync-ssl --ty", " 'saved path'"
                shell.text(prefix + suffix)
                shell.keys(*(["Left"] * len(suffix)))
                shell.open_menu()
                for level in ("Detailed", "Expanded"):
                    shell.keys("D")
                    shell.wait_for(lambda state: level in state.cells[0] and "--type" in "".join(state.cells))
                shell.cancel()
                self.assertEqual(shell.read_buffer(), (prefix + suffix, len(prefix)))
                shell.open_menu()
                shell.cancel("Enter")
                self.assertEqual(shell.read_buffer(), ("rsync-ssl --type=" + suffix, len("rsync-ssl --type=")))
                self.assertFalse(shell.executed.exists())
            finally:
                shell.close()
