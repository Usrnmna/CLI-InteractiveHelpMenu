"""Module-version cache invalidation with independent fixed-argument contracts."""

import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cli_help"))
from core import HelpError
from diagnostics import explain
from discovery import ProbeError, Settings, discover


class ModuleFreshnessTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.interpreter = self.folder / "python3"
        self.interpreter.write_text("interpreter")
        self.manual = self.folder / "man"
        self.manual.write_text("renderer")
        self.version = "pip 24.0 from /isolated/module (python 3.12)"
        self.flag = "--old"
        self.calls = []
        self.settings = Settings(cache_dir=self.folder / "cache")
        self.which = patch("discovery.shutil.which", side_effect=lambda name: str(self.manual if name == "man" else self.interpreter))
        self.which.start()
        self.addCleanup(self.which.stop)

    def response(self, argv, timeout, **kwargs):
        self.calls.append((argv, timeout, kwargs))
        return self.version if "--version" in argv else f"  {self.flag}  Documented option\n"

    def flags(self, profile):
        return {option["flag"] for category in profile["categories"] for option in category["options"]}

    def test_changed_module_under_same_interpreter_invalidates_cache(self):
        with patch("discovery.run_probe", side_effect=self.response):
            self.assertEqual(self.flags(discover("python3", self.settings, module="pip")), {"--old"})
            self.flag = "--new"
            self.assertEqual(self.flags(discover("python3", self.settings, module="pip")), {"--old"})
            self.version = "pip 25.0 from /isolated/module (python 3.12)"
            self.assertEqual(self.flags(discover("python3", self.settings, module="pip")), {"--new"})
        self.assertEqual([call[0][-1] for call in self.calls], ["--version", "--help", "--version", "--version", "--help"])
        for path in self.settings.cache_dir.glob("*.json"):
            self.assertNotIn("/isolated/module", path.read_text())

    def test_expiration_and_refresh_requery_help_but_warm_hits_only_check_version(self):
        with patch("discovery.run_probe", side_effect=self.response):
            discover("python3", self.settings, module="pip")
            self.flag = "--new"
            self.assertEqual(self.flags(discover("python3", self.settings, refresh=True, module="pip")), {"--new"})
            self.flag = "--later"
            path = next(self.settings.cache_dir.glob("*.json"))
            document = json.loads(path.read_text())
            document["created"] -= self.settings.cache_ttl + 1
            path.write_text(json.dumps(document))
            self.assertEqual(self.flags(discover("python3", self.settings, module="pip")), {"--later"})
            discover("python3", self.settings, module="pip")
        self.assertEqual(sum("--version" in call[0] for call in self.calls), 4)
        self.assertEqual(sum("--help" in call[0] for call in self.calls), 3)

    def test_interpreter_flags_home_and_file_identity_separate_cache(self):
        with patch("discovery.run_probe", side_effect=self.response):
            discover("python3", self.settings, module="pip")
            discover("python3", self.settings, module="pip", interpreter_options=("-I", "-B"))
            with patch.dict(os.environ, {"HOME": str(self.folder / "different-home")}):
                discover("python3", self.settings, module="pip")
            self.interpreter.write_text("changed interpreter bytes")
            discover("python3", self.settings, module="pip")
        self.assertEqual(sum("--help" in call[0] for call in self.calls), 4)
        self.assertIn([str(self.interpreter), "-I", "-B", "-m", "pip", "--version"], [call[0] for call in self.calls])

    def test_changed_virtual_environment_configuration_invalidates_cache(self):
        binary = self.folder / "venv" / "bin" / "python3"
        binary.parent.mkdir(parents=True)
        binary.write_text("same interpreter")
        self.interpreter = binary
        configuration = binary.parent.parent / "pyvenv.cfg"
        configuration.write_text("include-system-site-packages = false\n")
        with patch("discovery.run_probe", side_effect=self.response):
            discover("python3", self.settings, module="pip")
            self.flag = "--venv-new"
            configuration.write_text("include-system-site-packages = true\n")
            changed = discover("python3", self.settings, module="pip")
        self.assertEqual(self.flags(changed), {"--venv-new"})
        self.assertEqual(sum("--help" in call[0] for call in self.calls), 2)

    def test_pytest_version_and_help_disable_plugins_and_conftest(self):
        self.version = "pytest 8.3.0"
        with patch("discovery.run_probe", side_effect=self.response):
            discover("python3", self.settings, module="pytest", interpreter_options=("-I",))
        self.assertEqual(self.calls, [
            ([str(self.interpreter), "-I", "-m", "pytest", "--version", "--noconftest"], 2.0,
             {"check": True, "environment_overrides": {"PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"}}),
            ([str(self.interpreter), "-I", "-m", "pytest", "--help", "--noconftest"], 2.0,
             {"environment_overrides": {"PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"}})])

    def test_unverified_or_failed_version_never_reuses_or_writes_cache(self):
        with patch("discovery.run_probe", side_effect=self.response):
            discover("python3", self.settings, module="pip")
        self.flag = "--new"
        for failure in ("unrecognized PRIVATE_SENTINEL", ProbeError("PRIVATE_SENTINEL", "probe_timeout")):
            def response(argv, timeout, **kwargs):
                if "--version" in argv:
                    if isinstance(failure, Exception):
                        raise failure
                    return failure
                return "  --new  New help\n"
            with self.subTest(failure=failure), patch("discovery.run_probe", side_effect=response), \
                    patch("discovery.read_cache", side_effect=AssertionError("Stale cache read")), \
                    patch("discovery.write_cache", side_effect=AssertionError("Unverified cache written")):
                profile = discover("python3", self.settings, module="pip")
                self.assertEqual(self.flags(profile), {"--new"})
                self.assertNotIn("PRIVATE_SENTINEL", json.dumps(profile))

    def test_man_and_off_modes_never_probe_module_identity(self):
        with patch("discovery.run_probe", side_effect=self.response), \
                patch("discovery.module_fingerprint", side_effect=AssertionError("Module version invoked")):
            discover("python3", Settings(mode="man", cache_ttl=0), module="pip")
            with self.assertRaises(HelpError):
                discover("python3", Settings(mode="off"), module="pip")
        self.assertEqual(len(self.calls), 1)
        self.assertEqual(self.calls[0][0][0], str(self.manual))

    def test_cancelled_identity_request_does_not_read_cache_or_continue_to_help(self):
        with patch("discovery.run_probe", side_effect=KeyboardInterrupt) as probe, \
                patch("discovery.read_cache", side_effect=AssertionError("Cache read after cancel")), \
                patch("discovery.write_cache", side_effect=AssertionError("Cache written after cancel")):
            with self.assertRaises(KeyboardInterrupt):
                discover("python3", self.settings, module="pip")
        self.assertEqual(probe.call_count, 1)

    @unittest.skipUnless(os.name == "posix", "Fixed process probes require Linux")
    def test_real_module_change_has_fixed_operands_and_excludes_pending_environment(self):
        version = self.folder / "version"
        version.write_text("24.0")
        calls = self.folder / "calls"
        marker = self.folder / "workload"
        self.interpreter.write_text(
            f"#!{sys.executable}\nimport json,os,pathlib,sys\n"
            f"version=pathlib.Path({str(version)!r}).read_text()\n"
            f"with open({str(calls)!r},'a') as output: output.write(json.dumps(sys.argv[1:])+'\\n')\n"
            "if 'CLI_HELP_LINE' in os.environ or 'PYTHONPATH' in os.environ:\n"
            f"    pathlib.Path({str(marker)!r}).touch()\n"
            "if sys.argv[1:]==['-B','-m','pip','--version']:\n"
            "    print('pip '+version+' from /isolated/module (python 3.12)')\n"
            "elif sys.argv[1:]==['-B','-m','pip','help','install']:\n"
            "    print('  --version-'+version.replace('.','-')+'  Module option')\n"
            "else:\n"
            f"    pathlib.Path({str(marker)!r}).touch()\n")
        self.interpreter.chmod(0o700)
        with patch.dict(os.environ, {"CLI_HELP_LINE": "python3 -m pip install PRIVATE_PACKAGE --", "PYTHONPATH": "PRIVATE_MODULE"}):
            first = discover("python3", self.settings, module="pip", subcommands=("install",), interpreter_options=("-B",))
            discover("python3", self.settings, module="pip", subcommands=("install",), interpreter_options=("-B",))
            version.write_text("25.0")
            changed = discover("python3", self.settings, module="pip", subcommands=("install",), interpreter_options=("-B",))
        self.assertEqual(self.flags(first), {"--version-24-0"})
        self.assertEqual(self.flags(changed), {"--version-25-0"})
        self.assertEqual([json.loads(line) for line in calls.read_text().splitlines()], [
            ["-B", "-m", "pip", "--version"], ["-B", "-m", "pip", "help", "install"],
            ["-B", "-m", "pip", "--version"], ["-B", "-m", "pip", "--version"],
            ["-B", "-m", "pip", "help", "install"]])
        self.assertFalse(marker.exists())

    def test_passive_module_cache_is_explicitly_unverified_and_prose_is_not_echoed(self):
        with patch("discovery.run_probe", side_effect=self.response):
            discover("python3", self.settings, module="pip")
        path = next(self.settings.cache_dir.glob("*.json"))
        document = json.loads(path.read_text())
        document["profile"]["discovery"]["warnings"] = ["Source timed out PRIVATE_SENTINEL",
                                                         "No option declarations PRIVATE_SENTINEL"]
        path.write_text(json.dumps(document))
        with patch.dict(os.environ, {"CLI_HELP_CACHE_DIR": str(self.settings.cache_dir), "CLI_HELP_DISCOVERY": "auto",
                                     "CLI_HELP_DRIVERS": "", "CLI_HELP_PROFILES": ""}), \
                patch("discovery.run_probe", side_effect=AssertionError("Passive probe")):
            line = "python3 -m pip --old"
            report = explain(ROOT, line, len(line))
        self.assertEqual(report["cache"]["status"], "candidate_requires_verification")
        self.assertEqual(report["status"], "metadata_unverified")
        self.assertIn("age_seconds", report["cache"])
        self.assertEqual(report["cache"]["source_warnings"], ["source_timeout", "source_unparsed"])
        self.assertNotIn("/isolated/module", json.dumps(report))
        self.assertNotIn("PRIVATE_SENTINEL", json.dumps(report))


if __name__ == "__main__":
    unittest.main()
