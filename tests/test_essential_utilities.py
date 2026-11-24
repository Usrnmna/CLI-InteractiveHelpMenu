"""Independent spelling, arity and source-ownership checks for utility discovery."""

import json
import lzma
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cli_help"))

from discovery import build_profile
from presentation import option_text

FIXTURES = ROOT / "tests/fixtures"
ESSENTIAL = FIXTURES / "essential"
HISTORICAL = json.loads((ESSENTIAL / "utilities.json").read_text())
CURRENT = json.loads((ESSENTIAL / "utilities-full.json").read_text())
EXCERPTS = json.loads((FIXTURES / "help/captured.json").read_text())


def options_for(command, text):
    """Return one generated profile and its literal rows from a fixed response."""
    profile = build_profile(command, [(command + " help", text)])
    options = {option["flag"]: option for group in profile["categories"] for option in group["options"]}
    return profile, options


def historical_text(command):
    """Use the installed excerpt or complete workflow capture recorded for this route."""
    if command in EXCERPTS:
        return EXCERPTS[command]["text"]
    return (FIXTURES / "help" / f"workflow-{command}.txt").read_text()


def current_text(command, index=0):
    """Read unmodified package output including the capture reused by two releases."""
    path = ESSENTIAL / CURRENT[command]["sources"][index]["file"]
    return lzma.decompress(path.read_bytes()).decode() if path.suffix == ".xz" else path.read_text()


class EssentialUtilityTests(unittest.TestCase):
    def assert_inventory(self, command, text, expected):
        """Compare complete inventories including zero, one and paired operands."""
        _, options = options_for(command, text)
        counts = {flag: option.get("argument_count", 1) if option["argument"] else 0
                  for flag, option in options.items()}
        self.assertEqual(counts, expected)

    def test_installed_excerpts_and_workflow_responses(self):
        for command, expected in HISTORICAL.items():
            with self.subTest(command=command):
                self.assert_inventory(command, historical_text(command), expected)

    def test_complete_current_fixed_responses(self):
        for command, case in CURRENT.items():
            with self.subTest(command=command):
                expected = {flag: count for flag, count in case["options"].items()
                            if flag not in case.get("manual_only", [])}
                self.assert_inventory(command, current_text(command), expected)

    def test_complete_fixed_help_and_matching_installed_manual(self):
        for command, case in CURRENT.items():
            with self.subTest(command=command):
                sources = [(" ".join(record["argv"]), current_text(command, i))
                           for i, record in enumerate(case["sources"])]
                result = build_profile(command, sources)
                counts = {option["flag"]: option.get("argument_count", 1) if option["argument"] else 0
                          for group in result["categories"] for option in group["options"]}
                self.assertEqual(counts, case["options"])

    def test_manual_section_and_build_ownership(self):
        _, options = options_for("jq", current_text("jq", 1))
        self.assertNotIn("--disable-decnum", options)
        self.assertTrue(options["--run-tests"]["argument_optional"])
        self.assertIn("last option", options["--run-tests"]["detail"])
        _, options = options_for("rsync", current_text("rsync", 1))
        self.assertNotIn("-M--debug=", options)
        self.assertNotIn("--no-OPTION", options)
        self.assertIn("With --daemon", options["--config="]["detail"])
        self.assertEqual(options["-@"]["argument"], "NUM")
        _, options = options_for("wget", current_text("wget", 1))
        self.assertIn("c-ares support", options["--dns-servers="]["detail"])
        self.assertIn("Metalink support", options["--preferred-location"]["detail"])
        _, options = options_for("xz", current_text("xz", 1))
        self.assertIn("--filters9=", options)
        self.assertNotIn("-0", options)

    def test_older_rsync_fixed_response(self):
        case = CURRENT["rsync"]
        self.assert_inventory("rsync", (FIXTURES / "rsync/noble-client.txt").read_text(),
                              {flag: count for flag, count in case["options"].items() if flag not in case["manual_only"]})

    def test_fixed_modes_do_not_consume_a_filename_after_short_aliases(self):
        _, options = options_for("sort", historical_text("sort"))
        self.assertEqual(options["-c"]["argument"], "")
        self.assertEqual(options["-C"]["argument"], "")
        self.assertTrue(options["--check"]["argument_optional"])
        for mode in ("diagnose-first", "quiet", "silent"):
            self.assertIn("--check=" + mode, options["--check"]["detail"])
        _, options = options_for("du", historical_text("du"))
        self.assertTrue(options["--time"]["argument_optional"])
        self.assertIn("ctime or status", options["--time"]["detail"])
        _, options = options_for("tail", historical_text("tail"))
        self.assertFalse(options["-f"]["argument"])
        self.assertTrue(options["--follow"]["argument_optional"])
        _, options = options_for("fzf", "Options:\n  -m, --multi[=MAX]  Select multiple entries")
        self.assertEqual(options["-m"]["argument"], "[=MAX]")
        self.assertTrue(options["-m"]["argument_optional"])

    def test_wrapped_references_and_detached_rules_keep_correct_owners(self):
        _, options = options_for("du", historical_text("du"))
        self.assertIn("--max-depth=0 is the same as\n--summarize", options["--max-depth="]["detail"])
        self.assertNotIn("--max-depth=0", options["--summarize"]["detail"])
        _, options = options_for("cp", historical_text("cp"))
        self.assertIn("equivalent to --update=none.", options["--no-clobber"]["detail"])
        _, options = options_for("mv", historical_text("mv"))
        for spelling in ("-i", "--interactive", "-f", "--force", "-n", "--no-clobber"):
            self.assertIn("only the final one", options[spelling]["detail"])
        profile, options = options_for("xz", historical_text("xz"))
        self.assertNotIn("compression preset", options["--stdout"]["detail"])
        self.assertTrue(any("compression preset" in item["text"] and not item["options"]
                            for item in profile["documentation"]["shared"]))

    def test_source_qualified_inverses_and_literal_arguments_are_visible(self):
        profile, options = options_for("rg", current_text("rg"))
        owner = next(group for group in profile["categories"] if options["--no-mmap"] in group["options"])
        view = option_text(profile, owner, options["--no-mmap"])
        self.assertIn("Disable --mmap.", view.details)
        self.assertIn("--mmap", view.searchable)
        _, options = options_for("rsync", current_text("rsync"))
        self.assertIn("no creation-time support", options["-N"]["detail"])
        self.assertIn("help only on its own", options["-h"]["detail"])
        _, options = options_for("curl", current_text("curl"))
        self.assertTrue(options["--help"]["argument_optional"])
        self.assertNotIn("--http1.1", options["--hsts"]["detail"])

    def test_command_specific_facts_require_matching_evidence(self):
        for command in ("jq", "wget", "curl"):
            with self.subTest(command=command):
                _, options = options_for(command, "Options:\n  --from-file  List source files\n"
                                                  "  --hsts-file  Show database location\n"
                                                  "  --help TOPIC  Explain a required topic")
                self.assertFalse(options["--from-file"]["argument"])
                self.assertFalse(options["--hsts-file"]["argument"])
                self.assertFalse(options["--help"]["argument_optional"])
