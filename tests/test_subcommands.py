"""Verify context selection and exact help-only subprocess argument contracts."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from test_discovery import ROOT, write_executable
from core import HelpError, find_context, insert_option, load_profiles
from discovery import Settings, build_profile, discover


DOCKER_HELP = """Usage: docker run [OPTIONS] IMAGE [COMMAND] [ARG...]
Container options:
  -d, --detach          Run in background
  -i, --interactive     Keep stdin open
      --name string     Assign a name
      --env list        Set an environment variable
      --rm              Remove after exit
"""
GIT_MAN = """OPTIONS
       -a, --all
              Include tracked changes.
       -m, --message MESSAGE
              Supply a commit message.
"""


def make_subcommands(folder: Path):
    """Record every invocation; any action route creates an execution marker."""
    binaries = folder / "bin"
    binaries.mkdir()
    executed = folder / "action-executed"
    for name in ("docker", "git"):
        write_executable(binaries / name,
                         "import json, pathlib, sys\n"
                         f"with open({str(folder / (name + '-calls'))!r}, 'a') as stream: stream.write(json.dumps(sys.argv[1:]) + '\\n')\n"
                         "if " + repr(name) + " == 'docker' and sys.argv[1:] in "
                         "(['--help'], ['help', 'run'], ['help', 'exec'], ['help', 'container', 'run']):\n"
                         f"    print({DOCKER_HELP!r})\n"
                         "else:\n"
                         f"    pathlib.Path({str(executed)!r}).write_text(json.dumps(sys.argv[1:]))\n")
    write_executable(binaries / "man",
                     "import json, sys\n"
                     f"with open({str(folder / 'man-calls')!r}, 'a') as stream: stream.write(json.dumps(sys.argv[1:]) + '\\n')\n"
                     f"print({GIT_MAN!r} if sys.argv[-1].startswith('git-') else {DOCKER_HELP!r})\n")
    return binaries, executed


class SubcommandTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.folder = Path(self.temp.name)
        self.binaries, self.executed = make_subcommands(self.folder)
        self.environment = patch.dict(os.environ, {"PATH": str(self.binaries)})
        self.environment.start()
        self.settings = Settings(cache_dir=self.folder / "cache")

    def tearDown(self):
        self.environment.stop()
        self.temp.cleanup()

    def calls(self, name):
        path = self.folder / (name + "-calls")
        return [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []

    def context(self, line, point=None, profiles=None):
        return find_context(line, len(line) if point is None else point, profiles or [],
                            discover=lambda command, subcommands=(): discover(command, self.settings, subcommands=subcommands))

    def test_git_manual_does_not_invoke_git_or_forward_global_values(self):
        line = "git -C 'private repo' -c alias.commit='!touch marker' --no-pager commit --message 'private message' --a"
        context = self.context(line)
        self.assertEqual(context.profile["command"], ["git", "commit"])
        self.assertEqual(context.profile["discovery"]["sources"], ["man git-commit"])
        self.assertEqual(self.calls("git"), [])
        self.assertEqual(self.calls("man")[0][-2:], ["--", "git-commit"])
        self.assertNotIn("private", json.dumps(self.calls("man")))
        self.assertFalse(self.executed.exists())

    def test_docker_help_never_receives_globals_values_or_suffix(self):
        prefix = "docker --host 'tcp://private-host:2375' --config private-config run --name 'private name' --det"
        line = prefix + " private-image sh -c 'touch marker'"
        context = self.context(line, len(prefix))
        option = next(option for category in context.profile["categories"] for option in category["options"]
                      if option["flag"] == "--detach")
        edited, point = insert_option(context, option)
        self.assertEqual(edited, line.replace("--det ", "--detach "))
        self.assertEqual(point, len(prefix) + 4)
        self.assertEqual(self.calls("docker"), [["help", "run"]])
        self.assertEqual(self.calls("man")[0][-2:], ["--", "docker-run"])
        self.assertFalse(self.executed.exists())

    def test_nested_docker_context_and_attached_globals(self):
        context = self.context("docker -Hprivate-host --context=private --debug=false container run --det")
        self.assertEqual(context.profile["command"], ["docker", "container", "run"])
        self.assertEqual(self.calls("docker"), [["help", "container", "run"]])
        self.assertEqual(self.calls("man")[0][-1], "docker-container-run")

    def test_global_value_named_like_subcommand_is_not_a_path(self):
        context = self.context("docker --context run exec --i")
        self.assertEqual(context.profile["command"], ["docker", "exec"])
        self.assertEqual(self.calls("docker"), [["help", "exec"]])

    def test_git_attached_globals_and_bundled_precedence(self):
        context = self.context("git -Cprivate -cuser.name=private --git-dir=private commit --m",
                               profiles=load_profiles(ROOT / "profiles"))
        self.assertEqual(context.profile["command"], ["git", "commit"])
        self.assertEqual(self.calls("git") + self.calls("man"), [])

    def test_specific_context_wins_over_static_root_profile(self):
        root = build_profile("docker", [("fixture", "  --root-only   Root flag")])
        context = self.context("docker run --det", profiles=[root])
        self.assertEqual(context.profile["command"], ["docker", "run"])
        self.assertEqual(self.calls("docker"), [["help", "run"]])

    def test_custom_subcommand_profile_needs_no_probe(self):
        profile = build_profile(["docker", "compose", "up"], [("fixture", DOCKER_HELP)])
        context = self.context("docker --context private compose up --det", profiles=[profile])
        self.assertEqual(context.profile, profile)
        self.assertEqual(self.calls("docker") + self.calls("man"), [])

    def test_cursor_before_subcommand_selects_root_help(self):
        line = "docker --deb run --name private"
        context = self.context(line, len("docker --deb"))
        self.assertEqual(context.profile["command"], ["docker"])
        self.assertEqual(self.calls("docker"), [["--help"]])

    def test_ambiguous_paths_and_global_values_fail_before_any_probe(self):
        lines = ["docker --unknown run --", "docker --context --", "git -C --",
                 "docker compose up --", "git custom-alias --", "docker container unknown --",
                 "docker -- run --", "git -C $(touch marker) commit --", "git commit -- > file"]
        for line in lines:
            with self.subTest(line=line), self.assertRaises(HelpError):
                self.context(line)
        self.assertEqual(self.calls("git") + self.calls("docker") + self.calls("man"), [])
        self.assertFalse(self.executed.exists())

    def test_arguments_cannot_be_supplied_as_discovery_paths(self):
        for name, path in [("docker", ("run", "private-image")), ("git", ("commit", "--message")),
                           ("docker", ("compose", "up")), ("other", ("run",))]:
            with self.subTest(name=name, path=path), self.assertRaises(HelpError):
                discover(name, self.settings, subcommands=path)
        self.assertEqual(self.calls("git") + self.calls("docker") + self.calls("man"), [])

    def test_no_docker_insertion_after_image_or_container_command(self):
        for line in ["docker run private-image --", "docker exec private-container sh --",
                     "docker container run --name private private-image --", "docker run --unknown value --",
                     "docker run -it --", "docker run --name --", "docker run -- --"]:
            with self.subTest(line=line), self.assertRaises(HelpError):
                self.context(line)
        self.assertEqual(self.calls("docker"), [["help", "run"], ["help", "exec"], ["help", "container", "run"]])
        self.assertFalse(self.executed.exists())

    def test_docker_option_values_do_not_end_option_context(self):
        for line in ["docker run --name private --det", "docker run --name=private --det",
                     "docker run --env 'KEY=private value' --det", "docker run --name -- --det"]:
            with self.subTest(line=line):
                self.assertEqual(self.context(line).profile["command"], ["docker", "run"])

    def test_cache_separates_root_subcommands_and_nested_paths(self):
        for path in [(), ("run",), ("exec",), ("container", "run")]:
            for _ in range(2):
                profile = discover("docker", self.settings, subcommands=path)
                self.assertEqual(profile["command"], ["docker", *path])
        self.assertEqual(self.calls("docker"), [["--help"], ["help", "run"], ["help", "exec"], ["help", "container", "run"]])
        self.assertEqual(len(list(self.settings.cache_dir.glob("*.json"))), 4)

    def test_man_only_and_off_modes_never_invoke_target(self):
        profile = discover("docker", Settings(mode="man"), subcommands=("run",))
        self.assertEqual(profile["discovery"]["sources"], ["man docker-run"])
        with self.assertRaises(HelpError):
            discover("docker", Settings(mode="off"), subcommands=("run",))
        self.assertEqual(self.calls("docker"), [])

    def test_git_without_manual_fails_without_action_fallback(self):
        (self.binaries / "man").unlink()
        with self.assertRaisesRegex(HelpError, "man executable is unavailable"):
            discover("git", self.settings, subcommands=("commit",))
        self.assertEqual(self.calls("git"), [])
        self.assertFalse(self.executed.exists())

    def test_failed_docker_help_uses_manual_without_action_fallback(self):
        write_executable(self.binaries / "docker", "print('Unsupported help topic')\n")
        profile = discover("docker", self.settings, subcommands=("run",))
        self.assertEqual(profile["discovery"]["sources"], ["man docker-run"])
        self.assertTrue(profile["discovery"]["warnings"])

    def test_cli_inspection_supports_paths_and_rejects_extra_arguments(self):
        result = subprocess.run([sys.executable, str(ROOT / "cli_help/main.py"), "--discover", "docker", "run", "--refresh"],
                                capture_output=True, text=True, env={**os.environ, "CLI_HELP_CACHE_TTL": "0"})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["command"], ["docker", "run"])
        result = subprocess.run([sys.executable, str(ROOT / "cli_help/main.py"), "--discover", "docker", "run", "private-image"],
                                capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertEqual(self.calls("docker"), [["help", "run"]])


if __name__ == "__main__":
    unittest.main()
