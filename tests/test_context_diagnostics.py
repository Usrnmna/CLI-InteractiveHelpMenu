"""Parent-option resolution and passive, operand-free diagnostic contracts."""

import copy
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cli_help"))

from command_paths import help_route, load_driver_registry, resolve_path
from core import HelpError, find_context, insert_option, load_profiles
from diagnostics import doctor, explain
from discovery import ProbeExitError, Settings, discover
from drivers import parse_driver


SECRET = "PRIVATE_DIAGNOSTIC_SENTINEL"
LEAF = {"command": ["docker", "compose", "up"], "description": "Leaf contract",
        "categories": [{"name": "Options", "options": [
            {"flag": "--detach", "summary": "Detach"},
            {"flag": "--timeout", "summary": "Wait", "argument": "SECONDS"}]}]}


class ParentOptionTests(unittest.TestCase):
    def setUp(self):
        self.registry = load_driver_registry(ROOT / "config/drivers.example")

    def test_parent_options_resolve_exact_leaf_and_argument_offset(self):
        cases = [
            ["-f", "private.yml", "-f", "second.yml", "--profile", "debug"],
            ["--file=private.yml", "--profile=debug", "--project-name=private"],
            ["-fprivate.yml", "-pprivate", "--dry-run"],
            ["--parallel", "-1", "--compatibility=true"],
        ]
        for options in cases:
            words = ["docker", "--context", "private", "compose", *options, "up", "--detach"]
            with self.subTest(options=options):
                path = resolve_path(words, [], self.registry)
                self.assertEqual(path.words, ("docker", "compose", "up"))
                self.assertEqual(path.argument_start, len(words) - 1)
                self.assertEqual(help_route("docker", path.words[1:], self.registry).arguments,
                                 ("compose", "up", "--help"))

    def test_missing_values_unknown_flags_and_bundles_are_rejected_without_echo(self):
        for options in (["-f"], ["--file="], ["-f", "--profile"], ["--unknown=" + SECRET],
                        ["-Z" + SECRET], ["--profile", "debug", "--"], ["--dry-run=maybe"]):
            words = ["docker", "compose", *options]
            if options not in (["-f"], ["--file="], ["-f", "--profile"]):
                words.append("up")
            with self.subTest(options=options), self.assertRaises(HelpError) as raised:
                resolve_path(words, [], self.registry)
            self.assertNotIn(SECRET, str(raised.exception))
            self.assertIn(raised.exception.code, {"option_value_required", "unsupported_option"})

    def test_literal_midline_edit_keeps_prefix_quotes_suffix_and_cursor(self):
        prefix = "command sudo -n env LABEL='café' docker --context private compose -f '日本 file.yml' --profile=debug up\t "
        line = prefix + "--det\t  'tail 日本'"
        context = find_context(line, len(prefix + "--de"), [LEAF], driver_registry=self.registry)
        self.assertEqual(insert_option(context, LEAF["categories"][0]["options"][0]),
                         (prefix + "--detach\t  'tail 日本'", len(prefix + "--detach\t")))
        for value in ("", "-1", "'quoted value'"):
            line = prefix + "--timeout " + value + " --det"
            if value:
                self.assertEqual(find_context(line, len(line), [LEAF], driver_registry=self.registry).profile, LEAF)
            else:
                with self.assertRaises(HelpError):
                    find_context(line, len(line), [LEAF], driver_registry=self.registry)

    def test_cursor_before_within_and_after_leaf_uses_completed_words_only(self):
        parent = copy.deepcopy(LEAF)
        parent["command"] = ["docker", "compose"]
        parent["categories"][0]["options"] = [{"flag": "--profile", "argument": "NAME", "summary": "Profile"}]
        line = "docker compose -f private.yml  up --det"
        before = line.index("  up") + 1
        context = find_context(line, before, [parent, LEAF], driver_registry=self.registry)
        self.assertEqual(context.profile["command"], ["docker", "compose"])
        probe = Mock()
        with self.assertRaises(HelpError):
            find_context(line, line.index("up") + 1, [], discover=probe, driver_registry=self.registry)
        probe.assert_not_called()
        self.assertEqual(find_context(line, len(line), [LEAF], driver_registry=self.registry).profile, LEAF)

    def test_nested_parent_metadata_and_legacy_routes_remain_compatible(self):
        document = {"command": "tool", "paths": [
            {"command": ["group"], "help": ["help", "group"], "option_values": ["--config"]},
            {"command": ["group", "child"], "help": ["help", "group", "child"], "option_flags": ["--quiet"]},
            {"command": ["group", "child", "leaf"], "help": ["help", "group", "child", "leaf"]}]}
        name, driver = parse_driver(document)
        words = "tool group --config private child --quiet leaf".split()
        self.assertEqual(resolve_path(words, [], {name: driver}).words, ("tool", "group", "child", "leaf"))
        for field in ("option_values", "option_flags"):
            for bad in (None, "--x", ["--x", "--x"], ["--x=private"], [None]):
                changed = copy.deepcopy(document)
                changed["paths"][0][field] = bad
                with self.subTest(field=field, bad=bad), self.assertRaises(ValueError):
                    parse_driver(changed)
        document["paths"][0]["option_flags"] = ["--config"]
        with self.assertRaisesRegex(ValueError, "arity"):
            parse_driver(document)
        with self.assertRaisesRegex(ValueError, "root"):
            parse_driver({"command": "tool", "paths": [{"command": [], "help": ["--help"], "option_flags": ["--quiet"]}]})

    def test_fixed_probe_never_receives_parent_values_or_pending_operands(self):
        line = "docker compose -f '" + SECRET + ".yml' --profile debug up --det"
        with patch("discovery.shutil.which", side_effect=lambda name: sys.executable if name == "docker" else None), \
                patch("discovery.run_probe", return_value="  --detach  Detach\n") as probe:
            resolver = lambda command, **kwargs: discover(command, Settings(cache_ttl=0),
                                                           driver_registry=self.registry, **kwargs)
            find_context(line, len(line), [], discover=resolver, driver_registry=self.registry)
        probe.assert_called_once_with([os.path.abspath(sys.executable), "compose", "up", "--help"], 2.0)

    def test_manual_import_retains_parent_option_metadata(self):
        from manual_import import ManualCollection

        parent = copy.deepcopy(LEAF)
        parent["command"] = ["docker", "compose"]
        with tempfile.TemporaryDirectory() as directory:
            with ManualCollection(Path(directory)) as collection:
                result = collection.save(parent, "docker-compose", driver_defaults=self.registry["docker"])
            route = json.loads(Path(result["driver"]).read_text())["paths"][0]
        self.assertIn("--file", route["option_values"])
        self.assertIn("--dry-run", route["option_flags"])

    def test_existing_child_and_end_of_options_boundaries_remain_closed(self):
        leaf = copy.deepcopy(LEAF)
        leaf["command"] = ["docker", "compose", "exec"]
        for suffix in (" service echo --det", " -- service --det"):
            line = "docker compose -f private.yml exec" + suffix
            with self.subTest(suffix=suffix), self.assertRaises(HelpError):
                find_context(line, len(line), [leaf], driver_registry=self.registry)


class PassiveDiagnosticTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.environment = patch.dict(os.environ, {"CLI_HELP_DRIVERS": str(ROOT / "config/drivers.example"),
            "CLI_HELP_DISCOVERY": "auto", "CLI_HELP_CACHE_DIR": str(self.folder / "absent-cache"),
            "CLI_HELP_PROFILES": "", "CLI_HELP_CONFIG": ""})
        self.environment.start()
        self.addCleanup(self.environment.stop)

    def test_passive_modes_never_launch_probes_or_write_files(self):
        original_open = io.open

        def read_only(file, mode="r", *args, **kwargs):
            self.assertFalse(any(character in mode for character in "wax+"), mode)
            return original_open(file, mode, *args, **kwargs)

        with patch("subprocess.Popen", side_effect=AssertionError("Process started")), \
                patch("discovery.run_probe", side_effect=AssertionError("Probe started")), \
                patch("discovery.write_cache", side_effect=AssertionError("Cache written")), \
                patch("os.mkdir", side_effect=AssertionError("Directory created")), \
                patch("os.replace", side_effect=AssertionError("File replaced")), patch("io.open", side_effect=read_only):
            health = doctor(ROOT)
            ready = explain(ROOT, "rsync --ar", len("rsync --ar"))
            pending = explain(ROOT, "docker compose -f private.yml up --det", len("docker compose -f private.yml up --det"))
        self.assertEqual(health["mode"], "doctor")
        self.assertEqual(ready["status"], "ready")
        self.assertEqual(ready["profile"]["kind"], "bundled")
        self.assertEqual(pending["resolved_command"], ["docker", "compose", "up"])
        self.assertEqual(pending["code"], "discovery_required")
        self.assertFalse((self.folder / "absent-cache").exists())

    def test_pending_values_unknown_prefixes_and_operands_are_not_reported(self):
        lines = ["kubectl --token=" + SECRET + " get --", "sudo --bad=" + SECRET + " rsync --",
                 "env --bad=" + SECRET + " rsync --", "git " + SECRET + " --",
                 "env PYTHON" + SECRET + "=private rsync --", "rsync --exclude='" + SECRET + "' --ar",
                 "docker compose -f " + SECRET + ".yml --profile debug up --det"]
        for line in lines:
            with self.subTest(line=line):
                report = explain(ROOT, line, len(line))
                self.assertNotIn(SECRET, json.dumps(report))
                self.assertNotIn(line, json.dumps(report))
        registry = load_driver_registry(ROOT / "config/drivers.example")
        with self.assertRaises(HelpError) as raised:
            find_context(lines[0], len(lines[0]), [], driver_registry=registry)
        self.assertEqual(raised.exception.code, "unsupported_option")
        self.assertNotIn(SECRET, str(raised.exception))
        self.assertNotIn(SECRET, str(ProbeExitError(9, SECRET)))

    def test_custom_profile_provenance_and_configuration_failures_are_safe(self):
        profiles = self.folder / "profiles"
        profiles.mkdir()
        profile = copy.deepcopy(LEAF)
        (profiles / "custom.json").write_text(json.dumps(profile))
        with patch.dict(os.environ, {"CLI_HELP_PROFILES": str(profiles)}):
            line = "docker compose -f private.yml up --det"
            report = explain(ROOT, line, len(line))
            self.assertEqual(report["profile"], {"kind": "custom", "file": str(profiles / "custom.json")})
            (profiles / "custom.json").write_text('{"command":"' + SECRET + '"}')
            self.assertNotIn(SECRET, json.dumps(doctor(ROOT)))
            self.assertNotIn(SECRET, json.dumps(explain(ROOT, line, len(line))))

    def test_cli_diagnostics_do_not_create_bytecode_or_echo_rejected_cursor(self):
        runtime = self.folder / "runtime"
        import shutil
        shutil.copytree(ROOT / "cli_help", runtime / "cli_help", ignore=shutil.ignore_patterns("__pycache__"))
        shutil.copytree(ROOT / "profiles", runtime / "profiles")
        environment = dict(os.environ)
        environment.pop("PYTHONDONTWRITEBYTECODE", None)
        for mode in ("--doctor", "--explain"):
            environment.update(CLI_HELP_LINE="rsync --ar", CLI_HELP_POINT=SECRET if mode == "--explain" else "10")
            result = subprocess.run([sys.executable, str(runtime / "cli_help/main.py"), mode],
                                    env=environment, capture_output=True, text=True, timeout=15)
            self.assertNotIn(SECRET, result.stdout + result.stderr)
            self.assertEqual(json.loads(result.stdout)["mode"], mode[2:])
        self.assertFalse(list(runtime.rglob("*.pyc")))
        result = subprocess.run([sys.executable, str(ROOT / "cli_help/main.py"), "--doctor", "--bad=" + SECRET],
                                capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 2)
        self.assertNotIn(SECRET, result.stdout + result.stderr)

    def test_normal_cli_errors_omit_pending_values_and_invalid_cursor(self):
        for line, point in [("kubectl --token=" + SECRET + " get --", None),
                            ("sudo --bad=" + SECRET + " rsync --", None),
                            ("git " + SECRET + " --", None), ("rsync --ar", SECRET)]:
            environment = dict(os.environ, CLI_HELP_LINE=line, CLI_HELP_POINT=point or str(len(line)))
            result = subprocess.run([sys.executable, "-B", str(ROOT / "cli_help/main.py"), "--bash"],
                                    env=environment, capture_output=True, text=True, timeout=15)
            self.assertEqual(result.returncode, 1)
            self.assertEqual(result.stdout, "")
            self.assertNotIn(SECRET, result.stderr)


if __name__ == "__main__":
    unittest.main()
