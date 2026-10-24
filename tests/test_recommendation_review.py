"""Regression contracts for the scoped resolver, diagnostic, and cache review."""

import json
import locale
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cli_help"))

from command_paths import load_driver_registry, resolve_path
from core import HelpError, find_context, insert_option
from diagnostics import doctor, explain
from discovery import MAX_CACHE_BYTES, read_cache, write_cache
from drivers import parse_driver


SECRET = "PRIVATE_REVIEW_SENTINEL"
PARENT = {"command": ["docker", "compose"], "description": "Parent fixture",
          "categories": [{"name": "Options", "options": [
              {"flag": "-f", "argument": "FILE", "summary": "File"},
              {"flag": "-p", "argument": "NAME", "summary": "Project"},
              {"flag": "--dry-run", "summary": "Preview"}]}]}
PROFILE = {"command": ["fixture"], "description": "Fixture",
           "categories": [{"name": "Options", "options": [{"flag": "--flag", "summary": "Flag"}]}]}


class ResolverReviewTests(unittest.TestCase):
    def setUp(self):
        self.registry = load_driver_registry(ROOT / "config/drivers.example")

    def test_malformed_executable_is_rejected_before_observation_or_discovery(self):
        for executable in ("--token=" + SECRET, "./--token=" + SECRET, "-p" + SECRET):
            line = executable + " --"
            observer, probe = Mock(), Mock()
            with self.subTest(executable=executable), self.assertRaises(HelpError) as raised:
                find_context(line, len(line), [], discover=probe, observe=observer)
            self.assertEqual(raised.exception.code, "invalid_executable")
            self.assertNotIn(SECRET, str(raised.exception))
            observer.assert_not_called()
            probe.assert_not_called()
            report = explain(ROOT, line, len(line))
            self.assertEqual(report["status"], "rejected")
            self.assertNotIn("resolved_command", report)
            self.assertNotIn(SECRET, json.dumps(report))

    def test_parent_short_attached_payload_is_not_an_editable_flag(self):
        for flag in ("-f", "-p"):
            line = "docker compose " + flag + SECRET
            for point in (len("docker compose " + flag), len(line) - 2, len(line)):
                probe = Mock()
                with self.subTest(flag=flag, point=point), self.assertRaises(HelpError) as raised:
                    find_context(line, point, [PARENT], discover=probe, driver_registry=self.registry)
                self.assertEqual(raised.exception.code, "cursor_in_value")
                self.assertNotIn(SECRET, str(raised.exception))
                probe.assert_not_called()

    def test_declared_short_option_remains_editable_before_its_value(self):
        line = "docker compose -f"
        context = find_context(line, len(line), [PARENT], driver_registry=self.registry)
        self.assertEqual(insert_option(context, PARENT["categories"][0]["options"][0]),
                         ("docker compose -f ", len("docker compose -f ")))

    def test_attached_parent_values_still_allow_leaf_edits(self):
        leaf = {**PROFILE, "command": ["docker", "compose", "up"]}
        line = "docker compose -f" + SECRET + " --profile debug up --fl"
        context = find_context(line, len(line), [leaf], driver_registry=self.registry)
        result, point = insert_option(context, leaf["categories"][0]["options"][0])
        self.assertEqual(result, line[:-4] + "--flag ")
        self.assertEqual(point, len(result))

    def test_exact_parent_option_names_take_precedence_over_short_prefixes(self):
        name, driver = parse_driver({"command": "fixture", "paths": [
            {"command": ["group"], "help": ["help", "group"],
             "option_values": ["-f", "-file"], "option_flags": ["-fast"]},
            {"command": ["group", "leaf"], "help": ["help", "group", "leaf"]}]})
        profile = {**PROFILE, "command": ["fixture", "group"], "categories": [{"name": "Options", "options": [
            {"flag": "-f", "argument": "FILE", "attached": True, "summary": "File"},
            {"flag": "-file", "argument": "FILE", "summary": "File"}, {"flag": "-fast", "summary": "Fast"}]}]}
        for flag in ("-file", "-fast"):
            line = "fixture group " + flag
            context = find_context(line, len(line), [profile], driver_registry={name: driver})
            option = next(item for item in profile["categories"][0]["options"] if item["flag"] == flag)
            self.assertEqual(insert_option(context, option), (line + " ", len(line) + 1))
        for value in ("true", "false"):
            self.assertEqual(resolve_path(["fixture", "group", "-fast=" + value, "leaf"], [], {name: driver}).words,
                             ("fixture", "group", "leaf"))
        with self.assertRaises(HelpError) as raised:
            resolve_path(["fixture", "group", "-fast=" + SECRET, "leaf"], [], {name: driver})
        self.assertEqual(raised.exception.code, "unsupported_option")
        self.assertNotIn(SECRET, str(raised.exception))

    def test_root_global_values_preserve_existing_empty_and_dash_spellings(self):
        for arguments in (["-C", ""], ["-C", "-repository"], ["--git-dir="], ["-C="]):
            words = ["git", *arguments, "commit"]
            with self.subTest(arguments=arguments):
                result = resolve_path(words, [], self.registry)
                self.assertEqual(result.words, ("git", "commit"))
                self.assertEqual(result.argument_start, len(words))


class DiagnosticReviewTests(unittest.TestCase):
    @unittest.skipUnless(sys.platform.startswith("linux"), "Bash runtime locale checks require Linux")
    def test_python_utf8_mode_does_not_mask_an_ascii_shell_locale(self):
        environment = dict(os.environ, LC_ALL="C", LANG="C", PYTHONUTF8="1", PYTHONCOERCECLOCALE="0",
                           CLI_HELP_PROFILES="", CLI_HELP_DRIVERS="", CLI_HELP_CONFIG="")
        result = subprocess.run([sys.executable, "-B", str(ROOT / "cli_help/main.py"), "--doctor"],
                                env=environment, capture_output=True, text=True, timeout=5)
        report = json.loads(result.stdout)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(next(item for item in report["checks"] if item["name"] == "utf8")["status"], "unavailable")
        previous = locale.setlocale(locale.LC_CTYPE)
        with patch.dict(os.environ, {"LC_ALL": "C", "LANG": "C"}):
            doctor(ROOT)
        self.assertEqual(locale.setlocale(locale.LC_CTYPE), previous)

    def test_failed_home_expansion_stays_a_redacted_diagnostic(self):
        with patch.dict(os.environ, {"CLI_HELP_PROFILES": "~unresolvable/profiles"}), \
                patch.object(Path, "expanduser", side_effect=RuntimeError(SECRET)):
            health = doctor(ROOT)
            context = explain(ROOT, "rsync --ar", len("rsync --ar"))
        self.assertEqual(health["status"], "attention_required")
        self.assertEqual(health["configuration"]["code"], "configuration_invalid")
        self.assertEqual(context["status"], "rejected")
        self.assertEqual(context["code"], "configuration_invalid")
        self.assertNotIn(SECRET, json.dumps([health, context]))

    @unittest.skipUnless(sys.platform.startswith("linux"), "Unresolvable account paths use POSIX expansion")
    def test_invalid_home_path_cli_returns_json_instead_of_traceback(self):
        environment = dict(os.environ, CLI_HELP_PROFILES="~__cli_help_review_missing_account__/profiles",
                           CLI_HELP_LINE="rsync --ar", CLI_HELP_POINT=str(len("rsync --ar")))
        for mode in ("--doctor", "--explain"):
            result = subprocess.run([sys.executable, "-B", str(ROOT / "cli_help/main.py"), mode],
                                    env=environment, capture_output=True, text=True, timeout=5)
            self.assertEqual(result.returncode, 1)
            self.assertEqual(json.loads(result.stdout)["mode"], mode[2:])
            self.assertNotIn("Traceback", result.stderr)


class CacheReviewTests(unittest.TestCase):
    def test_regular_cache_hit_remains_available(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "cache.json"
            identity = {"command": ["fixture"]}
            write_cache(path, identity, PROFILE)
            self.assertEqual(read_cache(path, identity, 60), PROFILE)

    @unittest.skipUnless(os.name == "posix", "FIFO and symlink cache checks require POSIX")
    def test_symlink_cache_entry_is_not_followed(self):
        with tempfile.TemporaryDirectory() as directory:
            original = Path(directory) / "original.json"
            link = Path(directory) / "cache.json"
            identity = {"command": ["fixture"]}
            write_cache(original, identity, PROFILE)
            link.symlink_to(original)
            self.assertIsNone(read_cache(link, identity, 60))

    def test_actual_read_limit_holds_when_size_metadata_is_stale(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "cache.json"
            identity = {"command": ["fixture"]}
            write_cache(path, identity, PROFILE)
            # A growing source can disagree with its initial stat size. The
            # reader must stop by bytes consumed rather than waiting for EOF.
            with patch("os.fstat", return_value=SimpleNamespace(st_mode=stat.S_IFREG, st_size=0)), \
                    patch("os.read", side_effect=lambda fd, count: b"x" * count) as read:
                self.assertIsNone(read_cache(path, identity, 60))
            self.assertLessEqual(read.call_count, MAX_CACHE_BYTES // 65536 + 2)

    @unittest.skipUnless(os.name == "posix", "FIFO cache checks require POSIX")
    def test_fifo_cache_entries_do_not_block_runtime_or_passive_inspection(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "candidate.json"
            os.mkfifo(path)
            code = ("import sys; from pathlib import Path; sys.path.insert(0,sys.argv[1]); "
                    "from discovery import read_cache; "
                    "assert read_cache(Path(sys.argv[2]),{'command':['fixture']},60) is None")
            result = subprocess.run([sys.executable, "-B", "-c", code, str(ROOT / "cli_help"), str(path)],
                                    capture_output=True, text=True, timeout=3)
            self.assertEqual(result.returncode, 0, result.stderr)
            line = "python3 -m pip --"
            environment = dict(os.environ, CLI_HELP_CACHE_DIR=directory, CLI_HELP_DISCOVERY="auto",
                               CLI_HELP_PROFILES="", CLI_HELP_DRIVERS="", CLI_HELP_LINE=line,
                               CLI_HELP_POINT=str(len(line)))
            result = subprocess.run([sys.executable, "-B", str(ROOT / "cli_help/main.py"), "--explain"],
                                    env=environment, capture_output=True, text=True, timeout=3)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)["status"], "needs_discovery")


if __name__ == "__main__":
    unittest.main()
