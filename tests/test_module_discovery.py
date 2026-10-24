"""Verify fixed Python module help routes and executable variant identification.

Route provenance: https://pip.pypa.io/en/stable/user_guide/ and
https://docs.pytest.org/en/stable/how-to/plugins.html . Parser declarations
below are maintained minimal extracts of pip 24.0 and pytest 8.3 help; exact
route operands are independently asserted rather than read from drivers.
"""

import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cli_help"))

from core import HelpError, find_context, insert_option
from command_paths import load_driver_registry
from discovery import Settings, build_profile, discover, parse_help, probe_environment, verify_command_variant


PIP_HELP = """Install Options:
  -t, --target <dir>           Install packages into <dir>.
  --no-deps                   Don't install package dependencies.
  --timeout <sec>             Set the socket timeout.
"""
PYTEST_HELP = """general:
  -k EXPRESSION               Only run tests which match the given substring expression.
  --maxfail=num               Exit after first num failures or errors.
  --collect-only              Only collect tests, don't execute them.
"""


class ModuleCaptureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.captures = json.loads((ROOT / "tests" / "fixtures" / "help" / "python-module-captured.json").read_text(encoding="utf-8"))

    def test_each_supported_module_route_has_provenance_and_independent_arity(self):
        expected = {
            "pip": {"--isolated": "", "--timeout": "<sec>"},
            "pip install": {"-r": "<file>", "--requirement": "<file>", "--target": "<dir>", "--no-deps": ""},
            "pip uninstall": {"-r": "<file>", "--requirement": "<file>", "-y": "", "--yes": ""},
            "pip download": {"-d": "<dir>", "--dest": "<dir>", "--platform": "<platform>", "--no-deps": ""},
            "pip list": {"--outdated": "", "--format": "<list_format>"},
            "pytest": {"-k": "EXPRESSION", "--maxfail=": "num", "--collect-only": ""},
        }
        self.assertEqual(set(self.captures), set(expected))
        for route, definitions in expected.items():
            with self.subTest(route=route):
                capture = self.captures[route]
                self.assertTrue(capture["reference"].startswith("https://"))
                self.assertIn("Python", capture["interpreter_version"])
                self.assertTrue(capture["module_version"])
                options = {entry["flag"]: entry for entry in parse_help(capture["text"], route)}
                for flag, argument in definitions.items():
                    self.assertEqual(options[flag]["argument"], argument)
                    self.assertEqual(options[flag].get("argument_count", 1) if argument else 0, 1 if argument else 0)
                    self.assertFalse(options[flag]["argument_optional"])
                self.assertNotIn("EXPRESSION", options)
                self.assertNotIn("<dir>", options)

    def test_both_interpreters_every_module_route_preserve_exact_prefix_and_cursor(self):
        selected = {"pip": "--isolated", "pip install": "--no-deps", "pip uninstall": "--yes",
                    "pip download": "--no-deps", "pip list": "--outdated", "pytest": "--collect-only"}
        for interpreter in ("python", "python3"):
            for route, flag in selected.items():
                with self.subTest(interpreter=interpreter, route=route):
                    prefix = "env LABEL='日本 語'  " + interpreter + " -B -m " + route + "  "
                    partial = flag[:-2]
                    suffix = "\t  'file é name'"
                    line = prefix + partial + suffix
                    calls = []
                    def resolver(command, **arguments):
                        calls.append((command, arguments))
                        return build_profile(route.split(), [(route, self.captures[route]["text"])])
                    context = find_context(line, len(prefix + partial), [], discover=resolver)
                    option = next(option for category in context.profile["categories"] for option in category["options"] if option["flag"] == flag)
                    result, point = insert_option(context, option)
                    self.assertEqual(result, prefix + flag + suffix)
                    self.assertEqual(point, len(prefix + flag) + 1)
                    self.assertEqual(calls, [(interpreter, {"subcommands": tuple(route.split()[1:]), "module": route.split()[0], "interpreter_options": ("-B",)})])


class ModuleDiscoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.folder = Path(self.temp.name)
        self.settings = Settings(cache_dir=self.folder / "cache")
        self.interpreter = self.folder / "python3"
        self.interpreter.write_text("selected interpreter", encoding="utf-8")
        self.which = patch("discovery.shutil.which", side_effect=lambda name: None if name == "man" else str(self.interpreter))
        self.which.start()

    def tearDown(self):
        self.which.stop()
        self.temp.cleanup()

    def test_both_interpreters_all_supported_pip_paths_have_fixed_help_operands(self):
        for interpreter in ("python", "python3"):
            for route in ((), ("install",), ("uninstall",), ("download",), ("list",)):
                with self.subTest(interpreter=interpreter, route=route), patch("discovery.run_probe", return_value=PIP_HELP) as probe:
                    profile = discover(interpreter, self.settings, refresh=True, module="pip", subcommands=route)
                    expected = ["help", *route] if route else ["--help"]
                    probe.assert_called_once_with([str(self.interpreter), "-m", "pip", *expected], self.settings.timeout)
                    self.assertEqual(profile["command"], ["pip", *route])
                    self.assertEqual(profile["discovery"]["executable"], str(self.interpreter))
                    options = {option["flag"]: option for category in profile["categories"] for option in category["options"]}
                    self.assertEqual(options["--target"]["argument"], "<dir>")
                    self.assertEqual(options["--no-deps"]["argument"], "")

    def test_pytest_help_disables_plugins_and_conftest_without_pending_workload(self):
        for interpreter in ("python", "python3"):
            with self.subTest(interpreter=interpreter), patch("discovery.run_probe", return_value=PYTEST_HELP) as probe:
                profile = discover(interpreter, self.settings, refresh=True, module="pytest", interpreter_options=("-B", "-I"))
                probe.assert_called_once_with([str(self.interpreter), "-B", "-I", "-m", "pytest", "--help", "--noconftest"],
                                              self.settings.timeout, environment_overrides={"PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"})
                self.assertEqual(profile["discovery"]["interpreter_options"], ["-B", "-I"])

    def test_direct_pytest_help_also_disables_plugins_and_conftest(self):
        with patch("discovery.run_probe", return_value=PYTEST_HELP) as probe:
            discover("pytest", self.settings)
        probe.assert_called_once_with([str(self.interpreter), "--help", "--noconftest"],
                                      self.settings.timeout, environment_overrides={"PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"})

    def test_module_routes_cannot_be_replaced_by_driver_overlay(self):
        with patch("discovery.help_route", side_effect=AssertionError("Ordinary driver route consulted")), patch("discovery.run_probe", return_value=PIP_HELP) as probe:
            discover("python3", self.settings, module="pip", subcommands=("install",), driver_registry={"pip": object()})
        self.assertEqual(probe.call_args.args[0][-4:], ["-m", "pip", "help", "install"])

    def test_unsupported_forms_are_rejected_before_any_probe(self):
        cases = [dict(module="os"), dict(module="pip", subcommands=("install", "private.whl")),
                 dict(module="pytest", subcommands=("private_test.py",)),
                 dict(module="pip", interpreter_options=("-c", "code")),
                 dict(module="pip", interpreter_options=("-W", "ignore")),
                 dict(module="pip", interpreter_options=("-X", "presite=workload")),
                 dict(module="pip", interpreter_options=("-m", "workload")),
                 dict(interpreter_options=("-I",))]
        for arguments in cases:
            with self.subTest(arguments=arguments), patch("discovery.run_probe") as probe:
                with self.assertRaises(HelpError):
                    discover("python3", self.settings, **arguments)
                probe.assert_not_called()

    def test_module_cache_separates_interpreter_options_and_selected_paths(self):
        with patch("discovery.run_probe", return_value=PIP_HELP) as probe:
            discover("python3", self.settings, module="pip")
            discover("python3", self.settings, module="pip")
            self.assertEqual(probe.call_count, 1)
            discover("python3", self.settings, module="pip", interpreter_options=("-I",))
            self.assertEqual(probe.call_count, 2)
            another = self.folder / "other" / "python3"
            another.parent.mkdir()
            another.write_text("another installation")
            self.interpreter = another
            discover("python3", self.settings, module="pip")
            self.assertEqual(probe.call_count, 3)

    @unittest.skipUnless(os.name == "posix", "Executable process fixtures require Linux")
    def test_real_probe_retains_selected_path_and_never_receives_pending_operands(self):
        record = self.folder / "record.json"
        marker = self.folder / "pending-workload-ran"
        self.interpreter.write_text(
            f"#!{sys.executable}\nimport json, os, pathlib, sys\n"
            f"record = pathlib.Path({str(record)!r})\n"
            "record.write_text(json.dumps({'argv': sys.argv, 'cwd': os.getcwd(), 'env': dict(os.environ)}))\n"
            "if sys.argv[1:] == ['-B', '-m', 'pytest', '--help', '--noconftest']:\n"
            f"    print({PYTEST_HELP!r})\n"
            "else:\n"
            f"    pathlib.Path({str(marker)!r}).write_text('unsafe operands')\n",
            encoding="utf-8")
        self.interpreter.chmod(0o700)
        with patch.dict(os.environ, {"CLI_HELP_LINE": "python3 -m pytest private_test.py --capture=no", "PYTEST_PLUGINS": "pending_workload"}):
            result = discover("python3", self.settings, module="pytest", interpreter_options=("-B",))
        recorded = json.loads(record.read_text())
        self.assertEqual(recorded["argv"], [str(self.interpreter), "-B", "-m", "pytest", "--help", "--noconftest"])
        self.assertEqual(recorded["env"]["PYTEST_DISABLE_PLUGIN_AUTOLOAD"], "1")
        self.assertNotIn("PYTEST_PLUGINS", recorded["env"])
        self.assertNotIn("CLI_HELP_LINE", recorded["env"])
        self.assertFalse(Path(recorded["cwd"]).exists())
        self.assertFalse(marker.exists())
        self.assertEqual(result["command"], ["pytest"])

    @unittest.skipUnless(os.name == "posix", "Interpreter symlink fixtures require Linux")
    def test_cache_preserves_virtual_environment_symlink_identity(self):
        alternate = self.folder / "venv" / "bin" / "python3"
        alternate.parent.mkdir(parents=True)
        alternate.symlink_to(self.interpreter)
        with patch("discovery.run_probe", return_value=PIP_HELP) as probe:
            discover("python3", self.settings, module="pip")
            self.interpreter = alternate
            discover("python3", self.settings, module="pip")
            self.assertEqual(probe.call_count, 2)
            self.assertEqual(probe.call_args.args[0][0], str(alternate))

    def test_manual_only_invokes_manual_without_interpreter(self):
        manual = self.folder / "man"
        manual.write_text("manual renderer")
        with patch("discovery.shutil.which", side_effect=lambda name: str(manual if name == "man" else self.interpreter)), patch("discovery.run_probe", return_value=PIP_HELP) as probe:
            result = discover("python3", Settings(mode="man", cache_dir=None), module="pip", subcommands=("install",))
        self.assertEqual(probe.call_count, 1)
        self.assertEqual(probe.call_args.args[0][0], str(manual))
        self.assertEqual(probe.call_args.args[0][-2:], ["--", "pip-install"])
        self.assertEqual(result["discovery"]["sources"], ["man pip-install"])
        self.assertIn("selected interpreter", result["discovery"]["warnings"][0])

    def test_auto_module_help_never_merges_or_falls_back_to_unrelated_system_manual(self):
        manual = self.folder / "man"
        manual.write_text("manual renderer")
        with patch("discovery.shutil.which", side_effect=lambda name: str(manual if name == "man" else self.interpreter)), patch("discovery.run_probe", return_value="No module named pytest") as probe:
            with self.assertRaises(HelpError):
                discover("python3", self.settings, module="pytest")
        self.assertEqual(probe.call_count, 1)
        self.assertEqual(probe.call_args.args[0][0], str(self.interpreter))

    def test_disabled_discovery_performs_no_lookup_or_probe(self):
        with patch("discovery.run_probe") as probe, patch("discovery.shutil.which") as lookup:
            with self.assertRaises(HelpError):
                discover("python3", Settings(mode="off"), module="pip")
            probe.assert_not_called()
            lookup.assert_not_called()

    def test_environment_removes_python_paths_and_pytest_pending_configuration(self):
        with patch.dict(os.environ, {"PYTHONPATH": "pending", "PYTHONSTARTUP": "pending.py", "PYTEST_PLUGINS": "pending", "PYTEST_ADDOPTS": "private_test.py", "PIP_CONFIG_FILE": "private.conf"}):
            environment = probe_environment()
        for key in ("PYTHONPATH", "PYTHONSTARTUP", "PYTEST_PLUGINS", "PYTEST_ADDOPTS", "PIP_CONFIG_FILE"):
            self.assertNotIn(key, environment)

    def test_yarn_overload_help_is_selected_only_after_verified_modern_version(self):
        registry = load_driver_registry(ROOT / "config" / "drivers.example")
        for version, expected in (("1.22.22", ["run", "--help"]), ("4.9.4", ["run", "-h=1"])):
            with self.subTest(version=version), patch("discovery.run_probe", side_effect=[version, "  --require #0  Preload the specified module\n"]) as probe:
                result = discover("yarn", self.settings, refresh=True, subcommands=("run",), driver_registry=registry)
                self.assertEqual(probe.call_args_list[0].args[0], [str(self.interpreter), "--version"])
                self.assertEqual(probe.call_args_list[1].args[0], [str(self.interpreter), *expected])
                self.assertEqual(result["categories"][0]["options"][0]["argument"], "#0")


class VariantAndSelectorTests(unittest.TestCase):
    def test_openssh_manual_lowercase_metavariables_keep_arity(self):
        text = "OPTIONS\n       -p port\n               Port to connect to.\n       -i identity_file\n\n               Identity file to read.\n       -o option\n               Configuration option.\n  -h help\n  -V version\n"
        entries = {entry["flag"]: entry for entry in parse_help(text, "OpenSSH 9.6p1 manual")}
        self.assertEqual(entries["-p"]["argument"], "port")
        self.assertEqual(entries["-i"]["argument"], "identity_file")
        self.assertEqual(entries["-o"]["argument"], "option")
        self.assertEqual(entries["-h"]["argument"], "")
        self.assertEqual(entries["-V"]["argument"], "")
        self.assertEqual(entries["-p"]["summary"], "Port to connect to.")

    def test_uppercase_key_value_is_one_argument(self):
        entries = parse_help("  --env KEY=VALUE  Set an environment variable\n", "help")
        self.assertEqual(entries[0]["argument"], "KEY=VALUE")
        self.assertEqual(entries[0].get("argument_count", 1), 1)

    def test_systemd_space_separated_short_long_aliases(self):
        entries = parse_help("  -t --type=TYPE  List units of a particular type\n  -f --follow  Follow the journal\n  -u --unit=UNIT  Show logs from the specified unit\n", "systemd 255 help")
        options = {entry["flag"]: entry for entry in entries}
        self.assertEqual(set(options), {"-t", "--type=", "-f", "--follow", "-u", "--unit="})
        self.assertEqual(options["-t"]["argument"], "TYPE")
        self.assertEqual(options["-u"]["argument"], "UNIT")
        self.assertEqual(options["-f"]["argument"], "")
        self.assertEqual(options["--follow"]["argument"], "")

    def test_yq_requires_mike_farah_major_four(self):
        for version, accepted in (("yq (https://github.com/mikefarah/yq/) version v4.44.3", True), ("yq 3.4.3", False), ("yq version 4.2.0", False), ("yq (https://github.com/mikefarah/yq/) version v3.4.0", False)):
            with self.subTest(version=version), patch("discovery.run_probe", return_value=version) as probe:
                if accepted:
                    self.assertEqual(verify_command_variant("yq", "/tools/yq", Settings()), version)
                else:
                    with self.assertRaises(HelpError):
                        verify_command_variant("yq", "/tools/yq", Settings())
                probe.assert_called_once_with(["/tools/yq", "--version"], 2.0)

    def test_yarn_rejects_cmdtest_version(self):
        for version, accepted in (("1.22.22", True), ("4.5.1", True), ("0.32+git", False)):
            with self.subTest(version=version), patch("discovery.run_probe", return_value=version):
                if accepted:
                    verify_command_variant("yarn", "/tools/yarn", Settings())
                else:
                    with self.assertRaises(HelpError):
                        verify_command_variant("yarn", "/tools/yarn", Settings())

    def test_esptool_command_spelling_is_version_specific(self):
        for version, route, accepted in (("esptool v5.1.0", "write-flash", True), ("esptool.py v4.8.1", "write_flash", True), ("esptool.py v4.8.1", "write-flash", False), ("esptool v5.1.0", "write_flash", False)):
            with self.subTest(version=version, route=route), patch("discovery.run_probe", return_value=version) as probe:
                if accepted:
                    verify_command_variant("esptool", "/tools/esptool", Settings(), (route,))
                else:
                    with self.assertRaises(HelpError):
                        verify_command_variant("esptool", "/tools/esptool", Settings(), (route,))
                probe.assert_called_once_with(["/tools/esptool", "--help"], 2.0)

    def test_manual_only_variant_checks_never_execute_programs(self):
        for name in ("yq", "yarn", "esptool", "esptool.py"):
            with self.subTest(name=name), patch("discovery.run_probe") as probe:
                with self.assertRaises(HelpError):
                    verify_command_variant(name, "/tools/" + name, Settings(mode="man"))
                probe.assert_not_called()

    def test_concrete_joined_selectors_and_placeholder_exclusions(self):
        entries = parse_help("  -c:v CODEC  Video codec\n  -c:a:0 CODEC  First audio codec\n  -c[:stream_specifier] CODEC  Placeholder\n  -c:<specifier> CODEC  Placeholder\n", "FFmpeg selector declarations")
        self.assertEqual({entry["flag"] for entry in entries}, {"-c:v", "-c:a:0"})
        self.assertEqual({entry["argument"] for entry in entries}, {"CODEC"})
        bare = parse_help("  -c:v codec\n", "FFmpeg selector declarations")
        self.assertEqual(bare[0]["flag"], "-c:v")
        self.assertEqual(bare[0]["argument"], "codec")


if __name__ == "__main__":
    unittest.main()
