"""Reconcile named manual options, build help and provider digest families offline."""

import re
import unittest

from test_expansion_systems import ROOT, options_for, profile_for


CAPTURES = ROOT / "tests/fixtures/openssl"
NOBLE_HELP = ROOT / "tests/fixtures/help/expansion-system-captures"
RELEASES = ("noble", "resolute", "upstream")
COMMANDS = ("s_client", "x509", "dgst")
HELP_OPTION = re.compile(r"^ (-[\w*-]+)(?: (\S+))? {2,}", re.M)
TABLE_ROW = re.compile(r"^\| `(-[\w-]+)` \| ([^|]+?) \| (\S+) \| (\S+) \| (\S+) \|$", re.M)


def manual_rows(command):
    """Read spelling, operand and release evidence from the audited manual table."""
    audit = (ROOT / "docs/openssl-manual-coverage.md").read_text(encoding="utf-8")
    table = audit.split(f"## openssl {command} inventory\n", 1)[1].partition("\n## ")[0]
    return {flag: (operand.strip("`"), evidence) for flag, operand, *evidence in TABLE_ROW.findall(table)}


class OpenSSLManualCoverageTests(unittest.TestCase):
    def test_every_manual_spelling_has_the_documented_operand(self):
        for command in COMMANDS:
            with self.subTest(command=command):
                rows = options_for(profile_for("openssl " + command))
                audit = manual_rows(command)
                self.assertEqual({f: r.get("argument") or "—" for f, r in rows.items()},
                                 {f: operand for f, (operand, _) in audit.items()})
                self.assertTrue(all("M" in "".join(e) or "D" in "".join(e) for _, e in audit.values()))

    def test_binary_help_matches_release_columns_and_operand_arity(self):
        for command in COMMANDS:
            audit = manual_rows(command)
            for index, release in enumerate(RELEASES):
                with self.subTest(command=command, release=release):
                    path = (NOBLE_HELP / f"openssl-{command}.txt" if release == "noble"
                            else CAPTURES / f"{release}-{command}-help.txt")
                    found = dict(HELP_OPTION.findall(path.read_text(encoding="utf-8")))
                    if command != "s_client":
                        self.assertEqual(found.pop("-*"), "")
                    expected = {f: operand != "—" for f, (operand, evidence) in audit.items()
                                if "H" in evidence[index]}
                    self.assertEqual({f: bool(arg) for f, arg in found.items()}, expected)

    def test_dynamic_digest_selectors_match_each_fixed_list(self):
        for index, release in enumerate(RELEASES):
            path = CAPTURES / f"{release}-dgst-list.txt"
            names = set(re.findall(r"-[\w-]+", path.read_text(encoding="utf-8")))
            for command in ("dgst", "x509"):
                with self.subTest(command=command, release=release):
                    expected = {f for f, (_, evidence) in manual_rows(command).items()
                                if "D" in evidence[index]}
                    self.assertEqual(names, expected)
                    self.assertNotIn("-digest", manual_rows(command))
