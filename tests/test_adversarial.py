"""Deterministic mutation tests for parser, buffer, cache, and process boundaries."""

import copy
import json
import os
from pathlib import Path
import random
import signal
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

from test_discovery import ROOT, write_executable
from core import HelpError, find_context, insert_option, validate_profile
from discovery import (ProbeError, Settings, build_profile, clean_output, parse_help,
                       read_cache, run_probe, write_cache)
from ui import Browser


def sample_profile():
    return build_profile("tool", [("fixture", "Options:\n  --alpha   Enable alpha\n  --output FILE   Select output\n")])


class ParserEdgeTests(unittest.TestCase):
    def test_alias_separators_and_shared_arguments(self):
        for separator in [", ", ",", " | ", " or "]:
            with self.subTest(separator=separator):
                entries = parse_help("  -o" + separator + "--output FILE   Output path", "fixture")
                self.assertEqual([entry["flag"] for entry in entries], ["-o", "--output"])
                self.assertTrue(all(entry["argument"] == "FILE" for entry in entries))

    def test_unsupported_joined_flags_are_not_truncated(self):
        for declaration in ["-Wl,<options>", "-Wa,<options>", "-c:v", "--name;bad", "--name/other", "--name$(bad)"]:
            with self.subTest(declaration=declaration):
                self.assertEqual(parse_help(declaration + "   Description", "fixture"), [])

    def test_examples_do_not_become_options_or_pollute_descriptions(self):
        text = "Options:\n  --safe   Valid flag\nExamples:\n  --example-only   Not an option declaration\nOther options:\n  --other   Another flag\n"
        entries = parse_help(text, "fixture")
        self.assertEqual([entry["flag"] for entry in entries], ["--safe", "--other"])
        self.assertNotIn("example-only", entries[0]["detail"])

    def test_crlf_and_cr_only_sources_preserve_declaration_boundaries(self):
        for newline in ["\n", "\r\n", "\r"]:
            with self.subTest(newline=repr(newline)):
                text = newline.join(["OPTIONS", "  --one   First", "  --two   Second"])
                self.assertEqual([entry["flag"] for entry in parse_help(text, "fixture")], ["--one", "--two"])

    def test_terminal_styling_and_overstrikes_preserve_literal_flags(self):
        for text in ["\x1b[31m--color\x1b[0m   Color", "_\b-\b--color   Color", "--color   Color\x1b]0;title\x07"]:
            entries = parse_help(text, "fixture")
            self.assertEqual(entries[0]["flag"], "--color")
            self.assertNotIn("\x1b", entries[0]["detail"])

    def test_boolean_aliases_do_not_inherit_unrelated_argument(self):
        entries = parse_help("--enable, --disable   Toggle feature\n--output FILE   Set path", "fixture")
        self.assertEqual([entry["argument"] for entry in entries], ["", "", "FILE"])

    def test_long_backspace_runs_do_not_destroy_line_boundaries(self):
        text = "Header\n" + "x" + "\b" * 100000 + "--flag   Description"
        self.assertEqual(clean_output(text), "Header\n--flag   Description")
        self.assertEqual(parse_help(text, "fixture")[0]["flag"], "--flag")

    def test_optional_and_required_equals_forms(self):
        entries = parse_help("--color[=WHEN]   Color\n--output=<file>   Path", "fixture")
        self.assertEqual(entries[0]["flag"], "--color")
        self.assertTrue(entries[0]["argument_optional"])
        self.assertEqual(entries[1]["flag"], "--output=")
        self.assertFalse(entries[1]["argument_optional"])

    def test_duplicate_sources_do_not_duplicate_insertable_flags(self):
        profile = build_profile("tool", [("help", "--output   Output"), ("man", "--output=FILE   Detailed output")])
        options = profile["categories"][0]["options"]
        self.assertEqual(len(options), 1)
        self.assertEqual(options[0]["flag"], "--output=")
        self.assertIn("Source: help", options[0]["detail"])
        self.assertIn("Source: man", options[0]["detail"])

    def test_large_manual_is_browsable_at_last_category_and_option(self):
        text = "\n".join(f"Category {category}:\n" + "\n".join(
            f"  --item-{category}-{option} VALUE   Description {option}" for option in range(50)) for category in range(30))
        profile = build_profile("tool", [("large", text)])
        browser = Browser(profile)
        browser.move_category(10000)
        browser.move_option(10000)
        self.assertEqual(browser.options()[browser.selected]["flag"], "--item-29-49")
        browser.set_query("--item-0-0")
        self.assertEqual(browser.category, 0)
        browser.set_query("absent option")
        browser.move_option(10000)
        self.assertEqual(browser.selected, 0)

    def test_seeded_parser_mutations_only_produce_schema_valid_literal_flags(self):
        rng = random.Random(20261017)
        characters = "abcXYZ012-_=,;[]<>:$()`\\\"' /\t\n\r\x00\x1b\b日本"
        for index in range(1200):
            text = "--" + "".join(rng.choice(characters) for _ in range(rng.randrange(0, 140)))
            with self.subTest(seed=20261017, case=index, text=text):
                try:
                    profile = build_profile("tool", [("mutation", text)])
                except HelpError:
                    continue
                validate_profile(profile, Path("mutation"))
                context = find_context("tool --", 7, [profile])
                for category in profile["categories"]:
                    for option in category["options"]:
                        edited, point = insert_option(context, option)
                        self.assertRegex(edited, r"^tool --?[A-Za-z0-9][A-Za-z0-9_-]*=? ?$")
                        self.assertEqual(point, len(edited))


class BufferEdgeTests(unittest.TestCase):
    def test_empty_quoted_positional_argument_is_not_an_insertion_slot(self):
        for raw in ["''", '""']:
            line = "tool " + raw
            with self.subTest(raw=raw), self.assertRaises(HelpError):
                find_context(line, len(line), [sample_profile()])

    def test_unsafe_shell_forms_fail_before_discovery(self):
        payloads = ["$(touch marker)", "`touch marker`", "$HOME", "${HOME}", "$((1+1))", "<(cat file)",
                    ">file", "2>file", "| cat", "&& echo", "; echo", "# comment", "'unfinished", "\\", "\nnext"]
        calls = []
        for payload in payloads:
            line = "tool " + payload + " --"
            # A final escaped space is valid shell syntax; an isolated trailing escape is tested separately.
            if payload == "\\":
                line = "tool \\"
            with self.subTest(payload=payload), self.assertRaises(HelpError):
                find_context(line, len(line), [], discover=lambda command: calls.append(command))
        self.assertEqual(calls, [])

    def test_seeded_unicode_midline_edits_preserve_prefix_suffix_and_cursor(self):
        rng = random.Random(41071)
        profile = sample_profile()
        option = profile["categories"][0]["options"][0]
        for index in range(500):
            value = "".join(rng.choice("ab café日本😀;|$()") for _ in range(rng.randrange(1, 50)))
            prefix = "tool '" + value + "'" + rng.choice([" ", "  ", "\t"])
            partial = rng.choice(["--a", "'--a'", '"--a"'])
            suffix = rng.choice(["", "  'next file'", "\tend", " 日本"])
            line = prefix + partial + suffix
            with self.subTest(seed=41071, case=index):
                context = find_context(line, len(prefix) + rng.randrange(1, len(partial) + 1), [profile])
                edited, point = insert_option(context, option)
                expected = prefix + "--alpha" + (suffix or " ")
                self.assertEqual(edited, expected)
                self.assertEqual(point, len(prefix + "--alpha "))

    def test_invalid_offsets_and_surrogates_fail_without_probes(self):
        for line, point in [("tool --", -1), ("tool --", 100), ("tool --", 2), ("tool '\ud800' --", 12)]:
            with self.subTest(line=line, point=point), self.assertRaises(HelpError):
                find_context(line, point, [], discover=lambda command: self.fail("Probe invoked"))


class CacheEdgeTests(unittest.TestCase):
    def test_corrupt_schema_cache_is_a_miss(self):
        identity = {"command": ["tool"]}
        document = {"identity": identity, "created": time.time(), "profile": sample_profile()}
        mutations = [None, [], {}, "text", 12]
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "cache.json"
            for value in mutations:
                for field in ["created", "profile", "identity"]:
                    candidate = {**document, field: value}
                    path.write_text(json.dumps(candidate))
                    with self.subTest(field=field, value=value):
                        self.assertIsNone(read_cache(path, identity, 60))
            path.write_text('[' * 1500 + '0' + ']' * 1500)
            self.assertIsNone(read_cache(path, identity, 60))

    def test_wrong_command_future_and_oversized_cache_are_misses(self):
        identity = {"command": ["tool"]}
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "cache.json"
            write_cache(path, identity, sample_profile())
            document = json.loads(path.read_text())
            for change in ["command", "future", "oversized"]:
                candidate = copy.deepcopy(document)
                if change == "command":
                    candidate["profile"]["command"] = ["other"]
                elif change == "future":
                    candidate["created"] = time.time() + 3600
                else:
                    candidate["padding"] = "x" * (2 * 1024 * 1024)
                path.write_text(json.dumps(candidate))
                self.assertIsNone(read_cache(path, identity, 60), change)

    def test_concurrent_atomic_cache_writes_leave_valid_json(self):
        from concurrent.futures import ThreadPoolExecutor
        identity = {"command": ["tool"]}
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "cache.json"
            with ThreadPoolExecutor(max_workers=4) as executor:
                list(executor.map(lambda _: write_cache(path, identity, sample_profile()), range(20)))
            self.assertIsNotNone(read_cache(path, identity, 60))
            self.assertEqual(list(Path(folder).iterdir()), [path])

    def test_settings_reject_nonfinite_and_out_of_range_numbers(self):
        for key, values in {"CLI_HELP_DISCOVERY_TIMEOUT": ["nan", "inf", "-1", "0", "31", "oops"],
                            "CLI_HELP_CACHE_TTL": ["-1", "604801", "1.5"], "CLI_HELP_DISCOVERY": ["unknown"]}.items():
            for value in values:
                with self.subTest(key=key, value=value), patch.dict(os.environ, {key: value}), self.assertRaises(HelpError):
                    Settings.from_environment()


class ProbeEdgeTests(unittest.TestCase):
    def probe(self, body, timeout=1, max_bytes=4096):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "probe"
            write_executable(path, body)
            return run_probe([str(path), "--help"], timeout, max_bytes)

    def test_stderr_and_nonzero_exit_are_available_to_parser(self):
        text = self.probe("import sys\nprint('  --stderr   Error stream help', file=sys.stderr)\nsys.exit(64)\n")
        self.assertEqual(parse_help(text, "probe")[0]["flag"], "--stderr")

    def test_invalid_utf8_is_replaced_without_losing_valid_options(self):
        text = self.probe("import os\nos.write(1, b'  --flag   Invalid byte \\xff\\n')\n")
        self.assertEqual(parse_help(text, "probe")[0]["flag"], "--flag")

    def test_exact_output_limit_and_overflow(self):
        self.assertEqual(len(self.probe("import os\nos.write(1, b'x' * 4096)\n")), 4096)
        with self.assertRaises(ProbeError):
            self.probe("import os\nos.write(1, b'x' * 4097)\n")

    def test_closed_stdout_does_not_bypass_process_timeout(self):
        with self.assertRaises(ProbeError):
            self.probe("import os, time\nos.close(1)\nos.close(2)\ntime.sleep(5)\n", timeout=0.1)

    def test_child_holding_pipe_is_killed_after_parent_exits(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "probe"
            marker = Path(folder) / "escaped"
            write_executable(path, "import os, time, pathlib\n"
                             "if os.fork() == 0:\n    time.sleep(0.4)\n"
                             f"    pathlib.Path({str(marker)!r}).write_text('alive')\n")
            with self.assertRaises(ProbeError):
                run_probe([str(path), "--help"], 0.1)
            time.sleep(0.5)
            self.assertFalse(marker.exists())

    def test_signal_exit_and_missing_executable_are_handled(self):
        self.assertEqual(self.probe("import os, signal\nos.kill(os.getpid(), signal.SIGTERM)\n"), "")
        with self.assertRaises(ProbeError):
            run_probe(["/nonexistent/cli-help-test-command", "--help"], 1)


if __name__ == "__main__":
    unittest.main()
