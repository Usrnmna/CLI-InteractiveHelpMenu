"""Verify source parsing, bounded probes, caching, and pending-command isolation."""

import json
import os
from pathlib import Path
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cli_help"))

from core import HelpError, find_context, insert_option, load_profiles
from discovery import (ProbeError, Settings, build_profile, clean_output, discover,
                       parse_help, probe_environment, run_probe)


HELP_TEXT = """Usage: discover-tool [OPTIONS] FILE

Output options:
  -a, --alpha                 Enable alpha output
                             More detail about alpha.
  -o, --output=FILE           Write output to a file
      --color[=WHEN]         Control color output
      --message MESSAGE      Set the message

Selection options:
  --beta                     Select beta
  --unsafe;touch marker      This is not a valid option declaration
"""

MAN_TEXT = """DISCOVER-TOOL(1)                     User Commands

NAME
       discover-tool - demonstrate automatic discovery

OPTIONS
       --alpha
              Detailed manual explanation of alpha.

       --manual-only=VALUE
              An option documented only in the manual.

SEE ALSO
       Other documentation.
"""


def write_executable(path: Path, body: str):
    """Create an isolated Python command fixture with an absolute interpreter."""
    path.write_text(f"#!{sys.executable}\n" + body, encoding="utf-8")
    path.chmod(0o700)


def make_commands(folder: Path):
    """Record help and normal invocations separately to detect accidental execution."""
    binary_dir = folder / "bin"
    binary_dir.mkdir()
    command = binary_dir / "discover-tool"
    invocation_log = folder / "help-invocations"
    executed = folder / "pending-executed"
    write_executable(command,
                     "import json, pathlib, sys\n"
                     "if sys.argv[1:] == ['--help']:\n"
                     f"    with open({str(invocation_log)!r}, 'a') as stream: stream.write(json.dumps(sys.argv[1:]) + '\\n')\n"
                     f"    print({HELP_TEXT!r})\n"
                     "else:\n"
                     f"    pathlib.Path({str(executed)!r}).write_text(json.dumps(sys.argv[1:]))\n")
    manual = binary_dir / "man"
    write_executable(manual,
                     "import json, sys\n"
                     f"with open({str(folder / 'man-invocations')!r}, 'a') as stream: stream.write(json.dumps(sys.argv[1:]) + '\\n')\n"
                     f"print({MAN_TEXT!r})\n")
    return command, invocation_log, executed


class ParsingTests(unittest.TestCase):
    def options(self, profile):
        return {option["flag"]: option for category in profile["categories"] for option in category["options"]}

    def test_aliases_arguments_categories_and_multiline_descriptions(self):
        profile = build_profile("discover-tool", [("--help", HELP_TEXT)])
        options = self.options(profile)
        self.assertEqual([category["name"] for category in profile["categories"]], ["Output Options", "Selection Options"])
        self.assertIn("More detail about alpha.", options["--alpha"]["detail"])
        self.assertEqual(options["-o"]["argument"], "FILE")
        self.assertEqual(options["--output="]["argument"], "FILE")
        self.assertEqual(options["--message"]["argument"], "MESSAGE")
        self.assertNotIn("--unsafe", options)

    def test_man_only_options_and_description_merge(self):
        options = self.options(build_profile("discover-tool", [("--help", HELP_TEXT), ("man", MAN_TEXT)]))
        self.assertIn("--manual-only=", options)
        self.assertIn("Detailed manual explanation", options["--alpha"]["detail"])
        self.assertIn("Source: man", options["--alpha"]["detail"])

    def test_optional_argument_does_not_require_a_following_value(self):
        profile = build_profile("discover-tool", [("--help", HELP_TEXT)])
        option = self.options(profile)["--color"]
        self.assertTrue(option["argument_optional"])
        context = find_context("discover-tool --color --a", 24, [profile])
        self.assertEqual(insert_option(context, self.options(profile)["--alpha"])[0], "discover-tool --color --alpha ")

    def test_no_flag_is_extracted_from_usage_or_example_commands(self):
        self.assertEqual(parse_help("Usage: foo --delete FILE\nExample: foo --execute FILE", "test"), [])

    def test_terminal_controls_and_man_overstrikes_are_removed(self):
        raw = "\x1b[31m--flag\x1b[0m\n_\b-\b--manual\n\x1b]0;window title\x07\x07"
        clean = clean_output(raw)
        self.assertNotIn("\x1b", clean)
        self.assertNotIn("\b", clean)
        self.assertNotIn("window title", clean)
        self.assertIn("--flag", clean)

    def test_lowercase_typed_arguments_and_choice_sets(self):
        profile = build_profile("tool", [("help", "  --output string   Output file\n  --mode {fast,slow}   Choose a mode\n")])
        options = self.options(profile)
        self.assertEqual(options["--output"]["argument"], "string")
        self.assertEqual(options["--mode"]["argument"], "{fast,slow}")

    def test_indented_uppercase_description_is_not_a_heading(self):
        profile = build_profile("tool", [("man", "OPTIONS\n       --context\n              Apply context\n              CTX\n")])
        self.assertIn("CTX", self.options(profile)["--context"]["detail"])

    def test_description_content_cannot_become_inserted_shell_text(self):
        profile = build_profile("tool", [("help", "  --literal   $(touch marker); shell text\n")])
        context = find_context("tool --lit", 10, [profile])
        option = self.options(profile)["--literal"]
        self.assertEqual(insert_option(context, option)[0], "tool --literal ")


class DiscoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.folder = Path(self.temp.name)
        self.command, self.invocations, self.executed = make_commands(self.folder)
        self.settings = Settings(cache_dir=self.folder / "cache")
        self.environment = patch.dict(os.environ, {"PATH": str(self.command.parent), "CLI_HELP_LINE": "secret pending command"})
        self.environment.start()

    def tearDown(self):
        self.environment.stop()
        self.temp.cleanup()

    def test_probe_uses_only_help_argument_and_manual_lookup(self):
        profile = discover("discover-tool", self.settings)
        self.assertEqual(json.loads(self.invocations.read_text()), ["--help"])
        manual_args = json.loads((self.folder / "man-invocations").read_text())
        self.assertEqual(manual_args[-2:], ["--", "discover-tool"])
        self.assertEqual(profile["discovery"]["sources"], ["discover-tool --help", "man discover-tool"])
        self.assertFalse(self.executed.exists())

    def test_context_forwards_only_executable_to_discovery(self):
        calls = []
        def resolver(command):
            calls.append(command)
            return discover(command, self.settings)
        line = 'discover-tool dangerous-subcommand "private file" --a'
        context = find_context(line, len(line), [], discover=resolver)
        option = context.profile["categories"][0]["options"][1]
        edited, _ = insert_option(context, option)
        self.assertEqual(calls, ["discover-tool"])
        self.assertEqual(edited, 'discover-tool dangerous-subcommand "private file" --alpha ')
        self.assertEqual(json.loads(self.invocations.read_text()), ["--help"])
        self.assertFalse(self.executed.exists())

    def test_unsafe_syntax_is_rejected_before_probe(self):
        for line in ['discover-tool $(touch marker) --', 'discover-tool -- > file', 'discover-tool filename', 'discover-tool']:
            with self.subTest(line=line), self.assertRaises(HelpError):
                find_context(line, len(line), [], discover=lambda command: discover(command, self.settings))
        self.assertFalse(self.invocations.exists())

    def test_static_profiles_take_precedence(self):
        def forbidden(command):
            self.fail("Static profile lookup invoked automatic discovery.")
        profiles = load_profiles(ROOT / "profiles")
        self.assertEqual(find_context("rsync --", 8, profiles, discover=forbidden).profile["command"], ["rsync"])

    def test_man_only_never_invokes_target(self):
        profile = discover("discover-tool", Settings(mode="man", cache_ttl=0))
        self.assertEqual(profile["discovery"]["sources"], ["man discover-tool"])
        self.assertFalse(self.invocations.exists())
        self.assertFalse(self.executed.exists())

    def test_off_mode_does_not_probe(self):
        with self.assertRaises(HelpError):
            discover("discover-tool", Settings(mode="off"))
        self.assertFalse(self.invocations.exists())
        self.assertFalse((self.folder / "man-invocations").exists())

    def test_cache_hit_refresh_and_executable_change(self):
        discover("discover-tool", self.settings)
        discover("discover-tool", self.settings)
        self.assertEqual(len(self.invocations.read_text().splitlines()), 1)
        discover("discover-tool", self.settings, refresh=True)
        self.assertEqual(len(self.invocations.read_text().splitlines()), 2)
        self.command.write_text(self.command.read_text() + "\n# Changed executable fingerprint.\n")
        discover("discover-tool", self.settings)
        self.assertEqual(len(self.invocations.read_text().splitlines()), 3)

    def test_corrupt_and_expired_cache_are_refreshed(self):
        discover("discover-tool", self.settings)
        path = next(self.settings.cache_dir.glob("*.json"))
        path.write_text("invalid json")
        discover("discover-tool", self.settings)
        document = json.loads(path.read_text())
        document["created"] = 0
        path.write_text(json.dumps(document))
        discover("discover-tool", self.settings)
        self.assertEqual(len(self.invocations.read_text().splitlines()), 3)

    def test_parser_version_change_invalidates_cached_metadata(self):
        with patch("discovery.CACHE_VERSION", 4):
            discover("discover-tool", self.settings)
        discover("discover-tool", self.settings)
        self.assertEqual(len(self.invocations.read_text().splitlines()), 2)
        discover("discover-tool", self.settings)
        self.assertEqual(len(self.invocations.read_text().splitlines()), 2)

    def test_unwritable_cache_does_not_block_discovery(self):
        cache = self.folder / "cache-file"
        cache.write_text("A file cannot serve as a cache directory.")
        profile = discover("discover-tool", Settings(cache_dir=cache))
        self.assertEqual(profile["command"], ["discover-tool"])

    def test_manual_fallback_when_help_has_no_options(self):
        write_executable(self.command, "print('No help available')\n")
        profile = discover("discover-tool", self.settings)
        self.assertEqual(profile["discovery"]["sources"], ["man discover-tool"])
        self.assertTrue(profile["discovery"]["warnings"])

    def test_partial_profile_is_cached_when_man_is_unavailable(self):
        (self.command.parent / "man").unlink()
        profile = discover("discover-tool", self.settings)
        discover("discover-tool", self.settings)
        self.assertEqual(profile["discovery"]["sources"], ["discover-tool --help"])
        self.assertEqual(len(self.invocations.read_text().splitlines()), 1)

    def test_probe_environment_excludes_pending_line_and_shell_hooks(self):
        with patch.dict(os.environ, {"BASH_ENV": "malicious", "ENV": "malicious", "MANOPT": "-H"}):
            environment = probe_environment()
        self.assertNotIn("CLI_HELP_LINE", environment)
        self.assertNotIn("BASH_ENV", environment)
        self.assertNotIn("ENV", environment)
        self.assertEqual(environment["MANOPT"], "")

    def test_timeout_and_output_limit(self):
        write_executable(self.command, "import time\ntime.sleep(5)\n")
        started = time.monotonic()
        with self.assertRaises(ProbeError):
            run_probe([str(self.command), "--help"], 0.1)
        self.assertLess(time.monotonic() - started, 2)
        write_executable(self.command, "print('x' * 10000)\n")
        with self.assertRaises(ProbeError):
            run_probe([str(self.command), "--help"], 1, max_bytes=1024)

    def test_nonzero_help_status_is_accepted(self):
        write_executable(self.command, "import sys\nprint('  --flag   Useful option')\nsys.exit(2)\n")
        self.assertIn("--flag", run_probe([str(self.command), "--help"], 1))

    def test_timeout_terminates_ordinary_descendants(self):
        marker = self.folder / "descendant-survived"
        write_executable(self.command,
                         "import os, pathlib, time\n"
                         "if os.fork() == 0:\n"
                         "    time.sleep(0.4)\n"
                         f"    pathlib.Path({str(marker)!r}).write_text('survived')\n"
                         "else:\n"
                         "    time.sleep(5)\n")
        with self.assertRaises(ProbeError):
            run_probe([str(self.command), "--help"], 0.1)
        time.sleep(0.5)
        self.assertFalse(marker.exists())

    def test_stdin_is_closed_and_working_directory_is_isolated(self):
        write_executable(self.command, "import os, sys\nprint(repr(sys.stdin.read()))\nprint(os.getcwd())\n")
        output = run_probe([str(self.command), "--help"], 1).splitlines()
        self.assertEqual(output[0], "''")
        self.assertNotEqual(output[1], os.getcwd())
        self.assertFalse(Path(output[1]).exists())


if __name__ == "__main__":
    unittest.main()
