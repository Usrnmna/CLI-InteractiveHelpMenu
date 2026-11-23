"""Compare OpenSSH menu declarations with release synopses and inspect real terminal cells."""

import json
import re
import sys
import unittest

from test_terminal_screen import ROOT, TMUX_AVAILABLE, TerminalTestCase

sys.path.insert(0, str(ROOT / "cli_help"))
from arguments import value_forms
from core import HelpError, find_context, insert_option
from presentation import option_label, option_text
from ui import ellipsize_cells


# Transcribed from the three upstream synopses, including ssh's separate -Q invocation.
# Ubuntu adds scp -s, omits ssh -Z, and accepts the synopsis-free sftp -h action.
UPSTREAM = {
    "ssh": ("46AaCfGgKkMNnqsTtVvXxYyZ", "BbcDEeFIiJLlmOoPpRSWwQ"),
    "scp": ("346ABCOpqRrTv", "cDFiJloPSX"),
    "sftp": ("46AaCfNpqrv", "BbcDFiJloPRSsX"),
}
ORIGINAL = {
    "ssh": "-4 -6 -C -F:CONFIGFILE -i:IDENTITY_FILE -J:DESTINATION -o:OPTION -q -v "
           "-p:PORT -l:USER -L:ADDRESS -R:ADDRESS -D:ADDRESS -N -T -t -n -E:LOG_FILE",
    "scp": "-4 -6 -C -F:CONFIGFILE -i:IDENTITY_FILE -J:DESTINATION -o:OPTION -q -v "
           "-P:PORT -p -r -l:LIMIT -O -S:PROGRAM",
    "sftp": "-4 -6 -C -F:CONFIGFILE -i:IDENTITY_FILE -J:DESTINATION -o:OPTION -q -v "
            "-P:PORT -b:BATCHFILE -B:BUFFER_SIZE -R:NUM_REQUESTS -l:LIMIT -r -p -s:SUBSYSTEM",
}
# The quoted word at the cursor and the operands beyond it must survive insertion.
SUFFIXES = {
    "ssh": " 'value here' destination printf '%s' -x",
    "scp": " 'value here' 'local file' destination:path",
    "sftp": " 'value here' 'destination:remote path'",
}


def profile_for(client):
    return json.loads((ROOT / "profiles" / (client + ".json")).read_text(encoding="utf-8"))


def manual_arity(client):
    """Map the union of documented client spellings and the two additional Ubuntu actions."""
    switches, valued = UPSTREAM[client]
    if client == "scp":
        switches += "s"
    if client == "sftp":
        switches += "h"
    return {"-" + flag: required for letters, required in ((switches, False), (valued, True))
            for flag in letters}


def usage_arity(usage):
    """Read leading switch bundles and single-value declarations, including nested metavariables."""
    switches = re.findall(r"\[-([a-zA-Z0-9]+)\]", usage)
    valued = re.findall(r"\[-([a-zA-Z])\s", usage)
    return {"-" + flag: required for groups, required in ((switches, False), (valued, True))
            for group in groups for flag in group}


class OpenSSHInventoryTests(unittest.TestCase):
    def test_packaged_and_captured_manual_synopses_match_ubuntu_surface(self):
        """Check usage and the original discovery captures independently of the profile declarations."""
        fixtures = ROOT / "tests/fixtures"
        for client in UPSTREAM:
            expected = manual_arity(client)
            if client == "ssh":
                del expected["-Z"]  # Current upstream only.
            elif client == "sftp":
                del expected["-h"]  # Parser action absent from usage and the manual.
            original = (fixtures / "help" / (client + ".txt")).read_text(encoding="utf-8")
            synopsis = original.split("SYNOPSIS", 1)[1].split("DESCRIPTION", 1)[0]
            with self.subTest(client=client, source="Noble manual"):
                self.assertEqual(usage_arity(synopsis), expected)
            for release in ("noble", "resolute"):
                with self.subTest(client=client, release=release):
                    source = fixtures / "openssh" / f"{release}-{client}-usage.txt"
                    self.assertEqual(usage_arity(source.read_text(encoding="utf-8")), expected)

    def test_inventories_pin_every_operand_and_disposition(self):
        """Match each manual table to the actual label and distinguish pilot rows from additions."""
        for client in UPSTREAM:
            if client == "ssh":
                doc, section = "openssh-ssh-inventory.md", "Manual inventory"
            else:
                doc, section = "openssh-transfer-inventories.md", client + " inventory"
            audit = (ROOT / "docs" / doc).read_text(encoding="utf-8")
            table = audit.split("## " + section + "\n", 1)[1].split("\n## ", 1)[0]
            profile = profile_for(client)
            expected = {row["flag"]: row.get("argument", "") for cat in profile["categories"]
                        for row in cat["options"]}
            original = {label.split(":")[0] for label in ORIGINAL[client].split()}
            seen = []
            for line in table.splitlines():
                if line.startswith("| `-"):
                    columns = line.strip("| ").split(" | ")
                    flag, operand = (value.strip("`") for value in columns[:2])
                    seen.append(flag)
                    with self.subTest(client=client, flag=flag):
                        self.assertEqual(expected[flag], "" if operand == "—" else operand)
                        self.assertEqual(columns[-2].lower(), "original" if flag in original else "added")
            self.assertCountEqual(seen, list(expected))

    def test_release_specific_qualifications_are_visible(self):
        """Keep the Ubuntu/upstream differences and resume requirements in the visible Details."""
        expected = {
            ("ssh", "-Z"): ("Upstream", "Ubuntu 24.04 and 26.04", "reject -Z"),
            ("ssh", "-X"): ("Upstream defaults to untrusted", "default to trusted", "ForwardX11Trusted=no"),
            ("scp", "-s"): ("reverses -O", "10.6p2", "ignores -s"),
            ("sftp", "-a"): ("prefix", "shorter", "upload"),
            ("sftp", "-h"): ("standard error", "status 1"),
        }
        for (client, flag), qualifications in expected.items():
            profile = profile_for(client)
            category, row = next((cat, opt) for cat in profile["categories"] for opt in cat["options"]
                                 if opt["flag"] == flag)
            visible = " ".join(option_text(profile, category, row).details)
            with self.subTest(client=client, flag=flag):
                for qualification in qualifications:
                    self.assertIn(qualification, visible)

    def test_completed_option_values_remain_opaque(self):
        """A filename may begin with '=' in an attached operand or '-' in a separate operand."""
        for client in UPSTREAM:
            profile = profile_for(client)
            for value in ("-F=private.conf", "-F '-private.conf'"):
                line = f"{client} {value} -v"
                with self.subTest(client=client, value=value):
                    self.assertEqual(find_context(line, len(line), [profile]).query, "-v")

    def test_original_labels_order_and_complete_insertions(self):
        """Pin all pilot labels independently of the expanded menu, then check every literal edit."""
        for client in UPSTREAM:
            profile = profile_for(client)
            options = [row for cat in profile["categories"] for row in cat["options"]]
            originals = ORIGINAL[client].split()
            original_flags = {label.split(":")[0] for label in originals}
            with self.subTest(client=client):
                self.assertEqual([row["flag"] + (":" + row["argument"] if row.get("argument") else "")
                                  for row in options if row["flag"] in original_flags], originals)
                expected = manual_arity(client)
                self.assertCountEqual([row["flag"] for row in options], list(expected))
            prefix, suffix = client + " ", SUFFIXES[client]
            context = find_context(prefix + suffix, len(prefix), [profile])
            for row in options:
                flag = row["flag"]
                with self.subTest(client=client, flag=flag):
                    self.assertEqual(bool(row.get("argument")), expected[flag])
                    self.assertFalse(row.get("argument_optional"))
                    self.assertEqual(row.get("argument_count", 1), 1)
                    self.assertEqual(insert_option(context, row),
                                     (prefix + flag + suffix, len(prefix + flag) + 1))
                    if expected[flag]:
                        self.assertTrue({"separate", "attached"} <= value_forms(row))
                        pending = prefix + flag + " "
                        with self.assertRaises(HelpError) as caught:
                            find_context(pending, len(pending), [profile])
                        self.assertEqual(caught.exception.code, "option_value_required")
                        for separator in ("", " "):
                            pending = prefix + flag + separator + "'a b' "
                            self.assertEqual(find_context(pending, len(pending), [profile]).query, "")


@unittest.skipUnless(TMUX_AVAILABLE, "Rendered-screen tests require Linux and tmux")
class OpenSSHMenuTests(TerminalTestCase):
    def pending(self, client, columns, rows):
        """Open an isolated shell and position Readline before the quoted value."""
        shell = self.start()
        shell.resize(columns, rows)
        prefix, suffix = client + " ", SUFFIXES[client]
        shell.text(prefix + suffix)
        shell.keys(*(["Left"] * len(suffix)))
        return shell, prefix, suffix

    def test_each_client_row_and_its_complete_details(self):
        """Inspect the highlight, declaration, prose and formatted values for every selectable row."""
        for client in UPSTREAM:
            profile = profile_for(client)
            shell, prefix, suffix = self.pending(client, 220, 150)
            shell.open_menu()
            for category_index, category in enumerate(profile["categories"]):
                if category_index:
                    shell.keys("Right")
                for index, option in enumerate(category["options"]):
                    if index:
                        shell.keys("Down")
                    label = option_label(option)
                    with self.subTest(client=client, label=label):
                        state = shell.wait_for(lambda screen: "Option: " + label in screen.cells)
                        divider = next(i for i, line in enumerate(state.cells) if line.startswith("Category "))
                        self.assertTrue(any("> " + ellipsize_cells(label, 40) in line
                                            and option["summary"] in line for line in state.cells[4:divider]))
                        first, last, total = map(int, re.split(r"[-/]", state.cells[-3].split()[1]))
                        self.assertEqual((first, last), (1, total))
                        panel = " ".join(" ".join(state.cells[divider + 1:-3]).split())
                        for line in option_text(profile, category, option).details:
                            self.assertIn(" ".join(line.split()), panel)
                        self.assertIn(" ".join(option.get("detail", "").split()), panel)
            shell.cancel()
            self.assertEqual(shell.read_buffer(), (prefix + suffix, len(prefix)))
            self.assertFalse(shell.executed.exists())

    def test_added_value_options_at_minimum_size(self):
        """Search from the unfiltered menu, scroll to a qualification, cancel and insert."""
        cases = (("ssh", "multiplexing master", "-O", "conninfo and channels"),
                 ("scp", "server executable", "-D", "path containing spaces"),
                 ("sftp", "local server command", "-D", "when it includes arguments"))
        for client, query, flag, qualification in cases:
            shell, prefix, suffix = self.pending(client, 60, 16)
            for action in ("Escape", "Enter"):
                with self.subTest(client=client, action=action):
                    self.assertEqual(shell.open_menu().cells[2].rstrip(), "Filter:")
                    shell.keys("/")
                    shell.text(query)
                    shell.keys("Enter")
                    state = shell.wait_for(lambda screen: screen.cells[2] == "Filter: " + query)
                    self.assertIn("> " + flag + " ", state.cells[4])
                    shell.keys(*(["]"] * 100))
                    state = shell.wait_for(lambda screen: qualification in " ".join(" ".join(screen.cells[8:-3]).split()))
                    self.assertGreater(int(state.cells[-3].split()[1].split("-")[0]), 1)
                    shell.cancel(action)
                    token = flag if action == "Enter" else ""
                    point = len(prefix + token) + bool(token)
                    self.assertEqual(shell.read_buffer(), (prefix + token + suffix, point))
            self.assertFalse(shell.executed.exists())

    def test_positional_boundaries_in_readline(self):
        """At the remote command or transfer path, refuse client options and retain the buffer."""
        lines = ("ssh destination printf '%s' -x ", "scp 'local file' host:'remote file' ",
                 "sftp 'host:remote path' ")
        for line in lines:
            with self.subTest(line=line):
                shell = self.start()
                shell.text(line)
                shell.keys("Escape", "h")
                shell.wait_for(lambda screen: screen.alternate == 0 and
                               "child_argument_boundary" in " ".join(screen.cells))
                self.assertEqual(shell.read_buffer(), (line, len(line)))
                self.assertFalse(shell.executed.exists())
