"""Check literal declarations and source ownership on the system-tool discovery routes."""

import json
import lzma
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cli_help"))
from discovery import build_profile
from errors import HelpError


FIXTURES = ROOT / "tests" / "fixtures" / "discovery-tiers"
SYSTEM_TOOLS = set("systemctl journalctl ssh scp sftp ip ss openssl podman psql fd fdfind fzf yq".split())


def profile_for(command, record):
    """Merge the fixture's exact help and manual responses, excluding the identity reply."""
    replies = []
    for source in record["sources"]:
        if source.get("identity"):
            continue
        if "file" in source:
            path = FIXTURES / source["file"]
            text = lzma.decompress(path.read_bytes()).decode() if path.suffix == ".xz" else path.read_text()
        else:
            text = source["text"]
        replies.append((" ".join(source["argv"]), text))
    return build_profile(command.split(), replies)


def options(profile):
    """Index selectable rows by their literal insertion spelling."""
    return {o["flag"]: o for c in profile["categories"] for o in c["options"]}


class SystemDiscoveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Read family inventories once without modifying captures or user state."""
        cls.inventory = json.loads((FIXTURES / "extended-tools.json").read_text())

    def discovered(self, command):
        return options(profile_for(command, self.inventory[command]))

    def test_systemctl_verb_ownership(self):
        for verb in ("status", "list-units", "show"):
            with self.subTest(verb=verb):
                view = self.discovered("systemctl " + verb)
                self.assertNotIn("--now", view)
                self.assertNotIn("--boot-loader-entry=", view)
                self.assertEqual("--property=" in view, verb == "show")
                self.assertEqual("--recursive" in view, verb == "list-units")

    def test_ssh_compound_values_and_session_escape(self):
        ssh = self.discovered("ssh")
        self.assertEqual(ssh["-W"]["argument"], "host:port")
        self.assertTrue(ssh["-L"]["argument"])
        self.assertIn("remote_socket", ssh["-L"]["detail"])
        self.assertNotIn("-KL", ssh)
        historical = (ROOT / "tests/fixtures/help/expansion-system-captures/ssh.txt").read_text()
        self.assertIn("-KL[bind_address:]", historical)
        self.assertNotIn("-KL", options(build_profile(["ssh"], [("man ssh", historical)])))
        alternate = "SSH(1)\n\nOPTIONS\n  -p PORT  Choose a port.\n"
        self.assertEqual(options(build_profile(["ssh"], [("man ssh", alternate)]))["-p"]["argument"], "PORT")
        self.assertEqual(self.discovered("sftp")["-s"]["argument"], "subsystem | sftp_server")

    def test_podman_volume_section_and_pull_policy(self):
        run = self.discovered("podman run")
        self.assertIn("idmap", run["--volume"]["detail"])
        self.assertNotIn("--volume,", run["--variant"]["detail"])
        self.assertNotIn("--link-local-ip", run)
        build = self.discovered("podman build")
        self.assertNotIn("--runtime", build)
        self.assertNotIn("--storage", build)
        self.assertTrue(build["--pull"]["argument_optional"])
        self.assertEqual(build["--pull"]["argument_style"], "equals")
        self.assertIn("Ubuntu 26.04", build["--pull"]["detail"])

    def test_client_formats_and_disabled_algorithms(self):
        s_client = self.discovered("openssl s_client")
        self.assertEqual(s_client["-port"]["argument"], "+int")
        self.assertFalse(s_client["-port"]["summary"].startswith("+int"))
        self.assertEqual(s_client["-certform"]["argument"], "PEM|DER")
        self.assertNotIn("-sctp", s_client)
        dgst = self.discovered("openssl dgst")
        self.assertFalse(dgst["-engine_impl"]["argument"])
        self.assertNotIn("-digest", dgst)

    def test_alias_ownership_and_optional_values(self):
        fdfind = self.discovered("fdfind")
        self.assertEqual(fdfind["--newer"]["argument"], fdfind["--changed-within"]["argument"])
        self.assertIn("Reverse", fdfind["--no-follow"]["summary"])
        self.assertTrue(fdfind["--exec"]["argument"])
        fzf = self.discovered("fzf")
        self.assertIn("+i", fzf["-i"]["detail"])
        self.assertIn("--no-sort", fzf)
        self.assertNotIn("-2", fzf)
        self.assertTrue(fzf["--listen-unsafe"]["argument_optional"])
        self.assertTrue(self.discovered("psql")["--help="]["argument_optional"])

    def test_ip_negative_filter_paragraph_boundary(self):
        address = self.discovered("ip address")
        self.assertIn("IPv6", address["-permanent"]["detail"])
        self.assertNotIn("flush protocol addresses", address["-primary"]["detail"])


def inventory_test(command):
    """Build a distinct test for each path so a failure identifies the source pair."""
    def test(self):
        record = self.inventory[command]
        if not record["options"]:
            diagnostic = "No applicable root option" if command == "ip route" else "No recognizable option"
            with self.assertRaisesRegex(HelpError, diagnostic):
                profile_for(command, record)
            return
        actual = self.discovered(command)
        self.assertEqual({name: (o.get("argument_count", 1) if o["argument"] else 0)
                          for name, o in actual.items()}, record["options"])
    return test


for case in json.loads((ROOT / "tests/fixtures/help/matrix.json").read_text()):
    name = case["command"]
    if case["tier"] == "extended" and name.split()[0] in SYSTEM_TOOLS:
        setattr(SystemDiscoveryTests, "test_inventory_" + name.replace(" ", "_"), inventory_test(name))
