"""Check Resolute provider ownership for the 57 initially option-bearing usage records."""

import hashlib
import json
from pathlib import Path
import shlex
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cli_help"))
from command_paths import help_route
from core import HelpError, find_context, insert_option, validate_profile
from discovery import Settings, build_profile, discover
from ubuntu_reference import lookup_record, reference_profile
from test_terminal_screen import TMUX_AVAILABLE, TmuxShell


XZ_GREP = "xzgrep xzegrep xzfgrep lzgrep lzegrep lzfgrep".split()
GHOSTSCRIPT = "dvipdf eps2eps gsnd pdf2ps ps2pdf ps2pdf12 ps2pdf13 ps2pdf14 ps2pdfwr ps2ps".split()
SBIN = set("coldreboot ebtables-translate ipp-usb iscsi-iname iscsid iscsistart mount.fuse mount.fuse3 pppd service xtables-nft-multi".split())
ALIASES = {
    **dict.fromkeys(XZ_GREP, "xzgrep"), **dict.fromkeys(("xzcmp", "lzcmp", "lzdiff"), "xzdiff"),
    "bzcmp": "bzdiff",
    "ebtables-translate": "xtables-nft-multi", "git-upload-archive": "git",
    "mount.fuse": "mount.fuse3", "captoinfo": "tic", "infotocap": "tic", "vimdiff": "vim.basic",
}
FIXTURES = ROOT / "tests/fixtures/ubuntu-coverage"


def record_for(name, edition="resolute"):
    """Look up the observed image executable, resolving only the listed provider aliases."""
    directory = "/usr/sbin" if name in SBIN else "/usr/bin"
    return lookup_record(name, edition, directory, directory + "/" + ALIASES.get(name, name))


def profile_for(name, edition="resolute"):
    """Build the packaged menu through the runtime declaration parser and schema validator."""
    return reference_profile(record_for(name, edition), build_profile, validate_profile)


def options(profile):
    return {row["flag"]: row for category in profile["categories"] for row in category["options"]}


class PriorityProviderTests(unittest.TestCase):
    def test_comparator_aliases_follow_the_wrapper_option_parser(self):
        for edition, names in (
                ("resolute", "xzcmp lzcmp zcmp bzcmp xzdiff lzdiff zdiff bzdiff"),
                ("noble", "xzcmp zcmp xzdiff zdiff")):
            for name in names.split():
                with self.subTest(command=name, edition=edition):
                    rows = options(profile_for(name, edition))
                    if name.endswith("cmp"):
                        self.assertIn("-l", rows)
                        self.assertEqual("--verbose" in rows, name == "bzcmp")
                        self.assertEqual(rows["-i"]["argument_style"], "attached_only")
                        self.assertEqual(rows["-n"]["argument_style"], "attached_only")
                        self.assertEqual(rows["--bytes"]["argument_style"], "equals")
                        self.assertNotIn("--unified", rows)
                    else:
                        self.assertNotIn("argument", rows["-u"])
                        self.assertNotIn("argument", rows["-c"])
                        self.assertTrue(rows["--unified"]["argument_optional"])
                        self.assertEqual(rows["--unified"]["argument_style"], "equals")
                        short_style = "attached" if name == "zdiff" else "attached_only"
                        self.assertEqual(rows["-U"]["argument_style"], short_style)
                        self.assertIn("--new-group-format", rows)
                        self.assertEqual("--horizon-lines" in rows, name == "bzdiff")
                        self.assertNotIn("--recursive", rows)
                        self.assertNotIn("--bytes", rows)
        for first, second in (("lzcmp", "xzcmp"), ("lzdiff", "xzdiff"), ("ps2ps2", "ps2ps")):
            with self.subTest(first=first, second=second):
                self.assertEqual(record_for(first)["options"], record_for(second)["options"])

    def test_comparison_and_postscript_wrapper_argument_insertion(self):
        comparable = profile_for("zdiff")
        line = "zdiff -U 3 --br 'café file'"
        point = line.index(" '")
        ctx = find_context(line, point, [comparable])
        self.assertEqual(insert_option(ctx, options(ctx.profile)["--brief"]),
                         (line.replace("--br ", "--brief "), len("zdiff -U 3 --brief ")))
        for name in ("xzdiff", "bzdiff"):
            profile = profile_for(name)
            line = name + " -U3 --un 'input path'"
            point = line.index(" '")
            ctx = find_context(line, point, [profile])
            self.assertEqual(insert_option(ctx, options(ctx.profile)["--unified"]),
                             (line.replace("--un ", "--unified= "), len(name + " -U3 --unified=")))
        profile = profile_for("ps2ps2")
        line = "ps2ps2 -r 'source file.ps' 'result file.ps'"
        ctx = find_context(line, len("ps2ps2 -r"), [profile])
        self.assertEqual(insert_option(ctx, options(ctx.profile)["-r"]), (line, len("ps2ps2 -r")))
        self.assertNotIn("-sOutputFile", options(profile))

    def test_shared_mentions_do_not_leak_sibling_or_unsupported_arguments(self):
        for name in XZ_GREP:
            with self.subTest(command=name):
                rows = options(profile_for(name))
                for switch in ("-r", "-R", "-z", "-Z", "--recursive", "--directories", "--exclude"):
                    self.assertNotIn(switch, rows)
                self.assertEqual(rows["-e"]["argument_count"], 1)
                self.assertEqual(rows["--regexp"]["argument_style"], "equals")
                self.assertNotIn("argument", rows["--with-filename"])

        table = options(profile_for("ebtables-translate"))
        self.assertEqual(table["-A"]["argument"], "CHAIN")
        self.assertNotIn("--dport", table)
        dispatcher = options(profile_for("xtables-nft-multi"))
        self.assertEqual(dispatcher["ebtables-translate"]["kind"], "keyword")
        self.assertNotIn("--wait", dispatcher)
        self.assertNotIn("-A", dispatcher)
        self.assertEqual(set(options(profile_for("fprintd-delete"))), {"-h", "--help"})
        xdg = options(profile_for("xdg-terminal-exec"))
        self.assertNotIn("-e", xdg)
        self.assertEqual(xdg["--print-cmd"]["argument_style"], "equals")
        self.assertIs(xdg["--print-cmd"]["argument_optional"], True)

    def test_forwarded_and_shared_options_keep_provider_boundaries(self):
        for name in GHOSTSCRIPT:
            with self.subTest(command=name):
                rows = options(profile_for(name))
                self.assertEqual(rows["-sPAPERSIZE"]["argument_style"], "equals")
                self.assertEqual(rows["-r"]["argument_style"], "attached_only")
                self.assertEqual("-sOutputFile" in rows, name == "gsnd")
        for name in ("dh_perl_openssl", "dh_bash-completion"):
            with self.subTest(command=name):
                rows = options(profile_for(name))
                self.assertEqual(rows["-p"]["argument_count"], 1)
                self.assertNotIn("--with", rows)
        for name in ("captoinfo", "infotocap"):
            with self.subTest(command=name):
                row = options(profile_for(name))["-w"]
                self.assertEqual((row["argument_optional"], row["argument_style"]), (True, "attached_only"))

    def test_synopsis_forms_and_command_boundaries(self):
        # Each case names a declaration from a provider's synopsis, code, or fixed help.
        # The last token belongs to another command, a later operand or an interactive mode.
        cases = [
            ("coldreboot", "--wtmp-only", "", "--kexec"),
            ("ibus", "engine", "keyword", "--type"),
            ("ipp-usb", "check", "keyword", "-bg"),
            ("iscsi-iname", "--prefix", "equals", "--initiatorname"),
            ("iscsid", "-i", "attached", "--targetname"),
            ("iscsistart", "--username_in", "equals", "-username_in"),
            ("m17n-db", "--locate", "", "--database"),
            ("nautilus-sendto", "--version", "", "--send"),
            ("nslookup", "-query", "equals", "server"),
            ("perl", "-e", "separate", "--programfile"),
            ("pon", "--quick", "", "-r"),
            ("pppd", "dryrun", "keyword", "--quick"),
            ("ptar", "-C", "", "--directory"),
            ("remmina-file-wrapper", "--connect", "equals", "--url-handler"),
            ("routel", "-f", "separate", "table"),
            ("service", "--status-all", "", "--full-restart"),
            ("systemd-cryptsetup", "attach", "keyword", "--key-file"),
            ("vimdiff", "-o", "attached_only", "--diff-mode"),
            ("vmware-xferlogs", "dec", "keyword", "--vmx"),
            ("Xwayland", "-glamor", "separate", "--rootless"),
            ("xzcmp", "--version", "", "--recursive"),
            ("zipdetails", "--encoding", "separate", "--extract"),
            ("zipgrep", "-e", "separate", "--exclude-from"),
            ("zstdgrep", "-B", "separate", "--decompress"),
            ("zstdless", "-N", "", "--decompress"),
        ]
        for name, spelling, shape, excluded in cases:
            with self.subTest(command=name):
                rows = options(profile_for(name))
                row = rows[spelling]
                if shape == "keyword":
                    self.assertEqual(row["kind"], "keyword")
                else:
                    self.assertEqual(row.get("argument_style", ""), shape)
                    self.assertEqual(row.get("argument_count", 0), int(bool(shape)))
                self.assertNotIn(excluded, rows)
        self.assertEqual(options(profile_for("xzcmp"))["-i"]["argument_style"], "attached_only")
        self.assertNotIn("--verbose", options(profile_for("xzcmp")))
        self.assertEqual(options(profile_for("nautilus-sendto"))["--xid"]["argument_count"], 1)
        self.assertNotIn("-f", options(profile_for("zstdgrep")))
        self.assertEqual(options(profile_for("zstdless"))["--buffers"]["argument_style"], "equals")
        self.assertNotIn("-F", options(profile_for("xzegrep")))
        self.assertNotIn("-E", options(profile_for("xzfgrep")))
        self.assertEqual(options(profile_for("ptar"))["-T"]["argument_count"], 1)
        self.assertFalse(options(profile_for("Xwayland"))["-glamor"]["argument_optional"])
        self.assertTrue(options(profile_for("Xwayland"))["-verbose"]["argument_optional"])

    def test_positional_and_provider_selected_guidance(self):
        for name, topic in (("fprintd-list", "username"), ("git-upload-archive", "repository"),
                            ("funzip", "password"), ("mount.fuse", "destination"),
                            ("mount.fuse3", "destination"), ("sensible-editor", "editor"),
                            ("sensible-pager", "pager"), ("usb_printerid", "device path")):
            with self.subTest(command=name), self.assertRaises(HelpError) as raised:
                profile_for(name)
            self.assertEqual(raised.exception.code, "usage_guidance")
            self.assertIn(topic, str(raised.exception).lower())

    def test_fixed_replies_and_provider_identities(self):
        replies = json.loads((FIXTURES / "resolute-priority-help.json").read_text())
        for name in ("fprintd-delete", "nautilus-sendto"):
            with self.subTest(command=name):
                self.assertEqual(record_for(name)["sha256"], hashlib.sha256(replies[name].encode()).hexdigest())
                self.assertIn("--help", replies[name])
        self.assertEqual(record_for("m17n-db")["package"], "m17n-db")
        self.assertEqual(record_for("usb_printerid")["package"], "printer-driver-foo2zjs")
        self.assertIsNone(lookup_record("vimdiff", "resolute", "/usr/bin", "/usr/bin/vim.tiny"))
        self.assertIsNone(lookup_record("xzgrep", "resolute", "/usr/bin", "/usr/local/bin/xzgrep"))

    def test_fixed_discovery_and_literal_midline_values(self):
        name = "xdg-terminal-exec"
        line = name + " --ti 'quoted café'"
        point = line.index(" '")
        with patch("discovery.shutil.which", side_effect=lambda cmd: "/usr/bin/" + name if cmd == name else None), \
                patch("ubuntu_reference.ubuntu_edition", return_value="resolute"), \
                patch("discovery.installed_reference", side_effect=lambda record: record), patch("discovery.executable_identity", return_value={}), \
                patch("discovery.run_probe", side_effect=AssertionError("Unexpected executable probe")):
            context = find_context(line, point, [], lambda executable: discover(executable, Settings()))
        self.assertEqual(insert_option(context, options(context.profile)["--title"]),
                         (line.replace("--ti ", "--title= "), len(name + " --title=")))
        self.assertEqual(help_route("coldreboot", ()).arguments, ())
        for name, tail in (("iscsistart", " -P "), ("service", " example "),
                           ("fprintd-delete", " person "), ("xzgrep", " -- ")):
            with self.subTest(command=name), self.assertRaises(HelpError):
                find_context(name + tail, len(name + tail), [profile_for(name)])

    @unittest.skipUnless(TMUX_AVAILABLE, "Requires Linux and tmux")
    def test_rendered_menu_cancel_and_midline_insert(self):
        """Replay the verified wrapper menu in Bash without invoking a terminal launcher."""
        temporary = tempfile.TemporaryDirectory(prefix="cli-help-priority-")
        self.addCleanup(temporary.cleanup)
        folder = Path(temporary.name)
        profiles = folder / "profiles"
        profiles.mkdir()
        profile = profile_for("xdg-terminal-exec")
        (profiles / "xdg-terminal-exec.json").write_text(json.dumps(profile))
        shell = TmuxShell(folder, profile_directory=profiles)
        self.addCleanup(shell.close)
        shell.text("xdg-terminal-exec() { touch " + shlex.quote(str(shell.executed)) + "; }")
        shell.keys("Enter")
        shell.resize(60, 16)
        prefix = "xdg-terminal-exec --ti"
        line = prefix + " 'café file'"
        shell.text(line)
        shell.keys("C-a", *(["Right"] * len(prefix)))
        shell.open_menu()
        shell.wait_for(lambda state: "--title" in state.selected_row)
        shell.keys("D")
        shell.wait_for(lambda state: "Detailed" in state.cells[0])
        shell.keys("D")
        shell.wait_for(lambda state: "Expanded" in state.cells[0])
        shell.find_detail("title")
        shell.cancel("Escape")
        self.assertEqual(shell.read_buffer(), (line, len(prefix)))
        shell.open_menu()
        shell.keys("Enter")
        shell.wait_for(lambda state: state.alternate == 0 and "--title=" in "".join(state.cells))
        self.assertEqual(shell.read_buffer(), ("xdg-terminal-exec --title= 'café file'", len("xdg-terminal-exec --title=")))
        self.assertFalse(shell.executed.exists())
