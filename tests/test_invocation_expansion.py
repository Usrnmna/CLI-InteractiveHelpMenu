"""Independent prefix, module-offset and structured-argument edit contracts."""

import copy
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cli_help"))
from command_paths import load_driver_registry
from core import HelpError, find_context, insert_option, load_profiles, validate_profile
from discovery import Settings, discover
from invocation import resolve_invocation


def profile(command, options, **metadata):
    """Create small independent contract profiles, unrelated to parser output."""
    return {"command": command.split(), "description": "Contract fixture", "categories": [
        {"name": "Options", "options": options}], **metadata}


FLAGS = [{"flag": "--verbose", "summary": "Verbose output"},
         {"flag": "--output", "summary": "Output path", "argument": "FILE"},
         {"flag": "-I", "summary": "Include", "argument": "DIR", "attached": True}]


class PrefixAndModuleEditingTests(unittest.TestCase):
    def test_every_required_route_is_in_the_maintained_matrix(self):
        required = """systemctl status|systemctl list-units|systemctl show|journalctl|
ssh|scp|sftp|pytest|ruff check|ruff format|uv sync|uv add|uv lock|uv venv|uv tool install|
uv pip install|uv run|go build|go test|go run|go mod tidy|dotnet build|dotnet test|
dotnet run|dotnet publish|dotnet restore|ip address|ip link|ip route|ss|openssl s_client|
openssl x509|openssl dgst|yarn install|yarn add|yarn run|bun run|podman run|podman build|
podman exec|podman logs|psql|yq eval|fd|fdfind|fzf|ansible-playbook|az account show|
az vm list|az storage blob list|gcloud config list|gcloud compute instances list|
gcloud storage ls|git stash|git stash push|git stash pop|git stash apply|git stash list|
git stash show|git worktree|git worktree add|git worktree list|git worktree remove|
git worktree prune|pio run|pio device monitor|platformio run|platformio device monitor|
esptool write-flash|esptool.py write-flash|esptool.py write_flash|arduino-cli compile"""
        fixtures = ROOT / "tests/fixtures/help"
        matrix = json.loads((fixtures / "matrix.json").read_text())
        commands = [case["command"] for case in matrix]
        self.assertTrue({route.strip() for route in required.split("|")} <= set(commands))
        self.assertEqual(len(commands), len(set(commands)))
        for family in ("systems", "development"):
            cases = json.loads((fixtures / f"expansion-{family}.json").read_text())
            self.assertEqual({case["command"] for case in cases},
                             {case["command"] for case in matrix if case.get("expansion") == family})

    def test_prefix_chains_preserve_whitespace_quoting_unicode_and_midline_cursor(self):
        prefixes = ["sudo ", "sudo -n -u 'operator' -- ", "env A='café 日本' ",
                    "env -u LANG -- A=literal ", "command -- ",
                    "command sudo -gstaff env LABEL='two words' ",
                    "env A=1 sudo --user=operator ", "sudo env A=1 env B=2 "]
        target = profile("target", FLAGS)
        for prefix in prefixes:
            with self.subTest(prefix=prefix):
                before = prefix + "target\t --ver\t 'tail 日本'"
                point = len(prefix + "target\t --ve")
                context = find_context(before, point, [target])
                after, cursor = insert_option(context, FLAGS[0])
                expected = prefix + "target\t --verbose\t 'tail 日本'"
                self.assertEqual(after, expected)
                self.assertEqual(cursor, len(prefix + "target\t --verbose\t"))

    def test_unsupported_prefixes_fail_before_discovery(self):
        probe = Mock()
        lines = ["env PATH=/private target --", "env -u PATH target --", "env -i target --",
                 "env -C /private target --", "env -S 'target --' ", "sudo -i target --",
                 "sudo -s target --", "sudo --chdir=/tmp target --", "sudo -h host target --",
                 "command -p target --", "command -v target --", "command -V target --",
                 "env command target --", "sudo command target --", "A=1 target --",
                 "sudo -u --", "env A=1 --", "env PYTHONPATH=/private python -m pip --",
                 "sudo env LD_PRELOAD=private target --", "sudo --unknown target --"]
        for line in lines:
            with self.subTest(line=line), self.assertRaises(HelpError):
                find_context(line, len(line), [], discover=probe)
        probe.assert_not_called()

    def test_cursor_in_prefix_or_interpreter_does_not_probe(self):
        probe = Mock()
        for line, point in [("sudo -u operator target --", 9),
                            ("env A=literal target --", 8),
                            ("python -I -m pip install --", 9),
                            ("python3 -m pytest --", 14)]:
            with self.subTest(line=line), self.assertRaises(HelpError):
                find_context(line, point, [], discover=probe)
        probe.assert_not_called()

    def test_module_context_keeps_interpreter_and_offsets_separate(self):
        registry = load_driver_registry(ROOT / "config/drivers.example")
        for interpreter in ("python", "python3", "/isolated/venv/bin/python"):
            for module, route in (("pip", "install"), ("pip", "download"), ("pytest", "")):
                with self.subTest(interpreter=interpreter, module=module, route=route):
                    logical = profile((module + " " + route).strip(), FLAGS)
                    probe = Mock(return_value=logical)
                    prefix = f"command env LABEL='café' {interpreter} -I -B -m {module} " + (route + " " if route else "")
                    line = prefix + "--ver 'unexecuted 日本'"
                    context = find_context(line, len(prefix + "--ve"), [], discover=probe, driver_registry=registry)
                    probe.assert_called_once_with(interpreter, subcommands=tuple(route.split()), module=module,
                                                  interpreter_options=("-I", "-B"))
                    self.assertEqual(insert_option(context, FLAGS[0]),
                                     (prefix + "--verbose 'unexecuted 日本'", len(prefix + "--verbose ")))

    def test_ordinary_profile_never_substitutes_module_documentation(self):
        generic = profile("pytest", FLAGS)
        line = "python3 -m pytest --ver"
        with self.assertRaises(HelpError):
            find_context(line, len(line), [generic])
        explicit = profile("python3 -m pytest", FLAGS)
        self.assertEqual(find_context(line, len(line), [explicit]).profile, explicit)

    def test_module_routes_require_no_driver_and_ignore_executable_overlays(self):
        for registry in ({}, load_driver_registry(ROOT / "config/drivers.example")):
            for command in ("install", "uninstall", "download", "list"):
                logical = profile("pip " + command, FLAGS)
                probe = Mock(return_value=logical)
                line = "python3 -m pip " + command + " --ver"
                find_context(line, len(line), [], discover=probe, driver_registry=registry)
                probe.assert_called_once_with("python3", subcommands=(command,), module="pip", interpreter_options=())
            probe = Mock()
            line = "python3 -m pip --python /other/python install --"
            with self.assertRaises(HelpError):
                find_context(line, len(line), [], discover=probe, driver_registry=registry)
            probe.assert_not_called()
        explicit = profile("python3 -m pip install", FLAGS)
        line = "python3 -m pip install --python=/other/python --"
        with self.assertRaises(HelpError):
            find_context(line, len(line), [explicit], driver_registry={})

    def test_unsupported_module_forms_are_explicit(self):
        for line in ("python script.py --", "python -c 'print(1)' --", "python -m os --",
                     "python -X importtime -m pip --", "python -W ignore -m pytest --",
                     "python -mpip --", "python3 -- -m pip --", "python3 -m pip unknown --"):
            probe = Mock()
            with self.subTest(line=line), self.assertRaises(HelpError):
                find_context(line, len(line), [], discover=probe,
                             driver_registry=load_driver_registry(ROOT / "config/drivers.example"))
            probe.assert_not_called()


class StructuredEditingTests(unittest.TestCase):
    def setUp(self):
        self.keyword = profile("ip address", [
            {"kind": "keyword", "flag": "show", "summary": "Show addresses"},
            {"kind": "keyword", "flag": "dev", "argument": "IFNAME", "summary": "Select interface"},
            {"kind": "keyword", "flag": "scope", "argument": "SCOPE", "summary": "Select scope"}])
        self.group = profile("flash write-flash", FLAGS, positional_group={
            "argument": "ADDRESS FILE", "argument_count": 2, "repeatable": True})

    def context(self, line, active_profile, point=None):
        return find_context(line, len(line) if point is None else point, [active_profile])

    def test_keyword_replacement_and_actual_values_are_distinct(self):
        option = self.keyword["categories"][0]["options"][1]
        context = self.context("sudo ip address show de\t scope global", self.keyword, len("sudo ip address show de"))
        self.assertEqual(insert_option(context, option),
                         ("sudo ip address show dev\t scope global", len("sudo ip address show dev\t")))
        for line in ("ip address dev ", "ip address dev sc", "ip address arbitrary", "ip address ''"):
            with self.subTest(line=line), self.assertRaises(HelpError):
                self.context(line, self.keyword)
        self.context("ip address show dev '日本 eth' scope global ", self.keyword)

    def test_joined_flags_are_complete_literals_and_never_placeholders(self):
        target = next(p for p in load_profiles(ROOT / "profiles") if p["command"] == ["ffmpeg"])
        option = next(o for c in target["categories"] for o in c["options"] if o["flag"] == "-c:v")
        line = "ffmpeg -i '日本 movie.mp4' -c: tail.mp4"
        context = self.context(line, target, len("ffmpeg -i '日本 movie.mp4' -c:"))
        expected = "ffmpeg -i '日本 movie.mp4' -c:v tail.mp4"
        self.assertEqual(insert_option(context, option), (expected, len("ffmpeg -i '日本 movie.mp4' -c:v ")))
        with self.assertRaises(HelpError):
            self.context("ffmpeg -c:v ", target)
        self.context("ffmpeg -c:v copy -ss -1 ", target)
        for flag in ("-c:", "-c:<stream>", "-c[:stream_specifier]", "-c:v;bad"):
            bad = profile("test", [{"flag": flag, "summary": "Invalid"}])
            with self.subTest(flag=flag), self.assertRaises(HelpError):
                validate_profile(bad, Path("fixture"))

    def test_repeated_groups_block_incomplete_input_but_keep_values_opaque(self):
        for line in ("flash write-flash 0x1000 --ver", "flash write-flash 0x1000 a.bin 0x2000 --ver"):
            with self.subTest(line=line), self.assertRaises(HelpError):
                self.context(line, self.group)
        for line in ("flash write-flash 0x1000 'café 日本.bin' 0x2000 './-flag.bin' --ver",
                     "flash write-flash --output=-1 0x1000 file.bin --ver"):
            context = self.context(line, self.group)
            self.assertEqual(insert_option(context, FLAGS[0])[0], line[:-5] + "--verbose ")
        for line in ("flash write-flash -- 0x1000 a.bin --ver", "flash write-flash 0x1000 -- --ver",
                     "flash write-flash 0x1000 --verbose --ver"):
            with self.subTest(line=line), self.assertRaises(HelpError):
                self.context(line, self.group)

    def test_attached_values_and_child_boundary(self):
        target = profile("runner", FLAGS, stop_at_positional=True)
        self.context("runner -I'café 日本' --ver", target)
        for line in ("runner -Ifoo", "runner script --verbose ", "runner -- script --ver",
                     "runner --output '--verbose' child --ver", "runner -unknown child --ver"):
            with self.subTest(line=line), self.assertRaises(HelpError):
                self.context(line, target)

    def test_schema_rejects_invalid_structured_metadata(self):
        for metadata in ({"stop_at_positional": "yes"}, {"identity": "execute-whatever"},
                         {"positional_group": {"argument": "PAIR", "argument_count": 1, "repeatable": True}}):
            with self.subTest(metadata=metadata), self.assertRaises(HelpError):
                validate_profile(profile("test", FLAGS, **metadata), Path("fixture"))


@unittest.skipUnless(sys.platform.startswith("linux"), "Probe contract requires Linux")
class PrefixProbeTests(unittest.TestCase):
    def test_only_fixed_target_help_executes_in_all_modes(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            marker, calls = root / "executed", root / "calls"
            target = root / "target"
            target.write_text("#!/usr/bin/python3\nimport sys,json\nfrom pathlib import Path\n"
                              f"with Path({str(calls)!r}).open('a') as f: f.write(json.dumps(sys.argv[1:])+'\\n')\n"
                              "if sys.argv[1:] == ['--help']: print('  --verbose  Verbose output')\n"
                              f"else: Path({str(marker)!r}).touch()\n")
            target.chmod(0o755)
            for name in ("sudo", "env", "command"):
                path = root / name
                path.write_text(f"#!/bin/sh\ntouch {marker}\n")
                path.chmod(0o755)
            line = f"command sudo -n env PRIVATE='café' {target} --ver action"
            point = len(line) - len(" action")
            with patch.dict(os.environ, {"PATH": str(root), "HOME": str(root)}):
                for mode in ("auto", "man", "off"):
                    callback = lambda executable, **kwargs: discover(executable, Settings(mode=mode, cache_ttl=0), **kwargs)
                    if mode == "auto":
                        context = find_context(line, point, [], discover=callback)
                        insert_option(context, context.profile["categories"][0]["options"][0])
                    else:
                        with self.assertRaises(HelpError):
                            find_context(line, point, [], discover=callback)
                    context = find_context(line, point, [profile("target", FLAGS)], discover=callback)
                    insert_option(context, FLAGS[0])
            self.assertFalse(marker.exists())
            self.assertEqual([json.loads(row) for row in calls.read_text().splitlines()], [["--help"]])


if __name__ == "__main__":
    unittest.main()
