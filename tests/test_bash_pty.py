"""Exercise real Bash Readline and curses in a Linux pseudoterminal."""

import fcntl
import json
import os
from pathlib import Path
import pty
import select
import shlex
import signal
import struct
import tempfile
import termios
import time
import unittest


ROOT = Path(__file__).resolve().parents[1]


class BashSession:
    """Own an isolated interactive shell and capture its pending buffer on demand."""

    def __init__(self, folder, custom=False, locale_name="C.UTF-8", extra_environment=None):
        self.folder = Path(folder)
        self.snapshot = self.folder / "snapshot"
        self.executed = self.folder / "executed"
        self.buffer = b""
        config = self.folder / "keys.json"
        config.write_text(json.dumps({"keys": {"accept": ["a"], "next_category": ["n"]}}))
        rcfile = self.folder / "bashrc"
        rcfile.write_text(
            "PS1='__HELP_TEST_PROMPT__ '\n"
            "PS2='__CONTINUATION__ '\n"
            "set +o history\n"
            + ("CLI_HELP_KEY='\\C-x\\C-h'\nexport CLI_HELP_CONFIG=" + shlex.quote(str(config)) + "\n" if custom else "")
            + "source " + shlex.quote(str(ROOT / "bash/interactive-help.bash")) + "\n"
            + "_snapshot() { printf '%s\\0%s\\0' \"$READLINE_POINT\" \"$READLINE_LINE\" > " + shlex.quote(str(self.snapshot)) + "; }\n"
            + "bind -x '\"\\C-x\\C-g\":_snapshot'\n"
            + "rsync() { printf executed > " + shlex.quote(str(self.executed)) + "; }\n"
        )
        self.pid, self.fd = pty.fork()
        if self.pid == 0:
            environment = {**os.environ, "TERM": "xterm-256color", "LC_ALL": locale_name}
            for key in list(environment):
                if key.startswith("CLI_HELP_") or key == "PROMPT_COMMAND":
                    environment.pop(key, None)
            environment["CLI_HELP_CACHE_DIR"] = str(self.folder / "cache")
            environment.update(extra_environment or {})
            os.execve("/bin/bash", ["bash", "--noprofile", "--rcfile", str(rcfile), "-i"], environment)
        fcntl.ioctl(self.fd, termios.TIOCSWINSZ, struct.pack("HHHH", 24, 100, 0, 0))
        self.expect(b"__HELP_TEST_PROMPT__")
        self.trigger = b"\x18\x08" if custom else b"\x1bh"

    def send(self, text):
        os.write(self.fd, text.encode() if isinstance(text, str) else text)

    def expect(self, text, timeout=5):
        deadline = time.monotonic() + timeout
        while text not in self.buffer:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise AssertionError(f"Missing terminal output {text!r}; recent output: {self.buffer[-2000:]!r}")
            if select.select([self.fd], [], [], remaining)[0]:
                self.buffer += os.read(self.fd, 65536)
        end = self.buffer.index(text) + len(text)
        result, self.buffer = self.buffer[:end], self.buffer[end:]
        return result

    def open(self, line):
        self.send(line)
        self.send(self.trigger)
        self.expect(b"Interactive help")

    def finish(self, key):
        self.send(key)
        self.expect(b"\x1b[?1049l")

    def read_buffer(self):
        self.snapshot.unlink(missing_ok=True)
        self.send(b"\x18\x07")
        deadline = time.monotonic() + 3
        while time.monotonic() < deadline:
            if self.snapshot.exists():
                fields = self.snapshot.read_bytes().split(b"\0")
                if len(fields) == 3:
                    return fields[1].decode(), int(fields[0])
            time.sleep(0.01)
        raise AssertionError("Readline snapshot was not written.")

    def close(self):
        try:
            self.send(b"\x03\x15exit\n")
            deadline = time.monotonic() + 2
            while time.monotonic() < deadline:
                if os.waitpid(self.pid, os.WNOHANG)[0]:
                    return
                time.sleep(0.02)
            os.kill(self.pid, signal.SIGKILL)
            os.waitpid(self.pid, 0)
        finally:
            os.close(self.fd)


class BashIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.session = None

    def tearDown(self):
        if self.session:
            self.session.close()
        self.temp.cleanup()

    def start(self, custom=False, locale_name="C.UTF-8", extra_environment=None):
        self.session = BashSession(self.temp.name, custom, locale_name, extra_environment)
        return self.session

    def test_select_inserts_without_executing_then_normal_enter_executes(self):
        session = self.start()
        session.open("rsync --ar")
        session.finish("\n")
        self.assertEqual(session.read_buffer(), ("rsync --archive ", 16))
        self.assertFalse(session.executed.exists())
        session.send("\n")
        session.expect(b"__HELP_TEST_PROMPT__")
        deadline = time.monotonic() + 2
        while not session.executed.exists() and time.monotonic() < deadline:
            time.sleep(0.01)
        self.assertTrue(session.executed.exists())

    def test_escape_preserves_exact_line_and_midline_cursor(self):
        session = self.start()
        line = 'rsync --ar "target folder"  '
        session.send(line)
        session.send(b"\x01" + b"\x06" * len("rsync --ar"))
        session.send(session.trigger)
        session.expect(b"Interactive help")
        session.finish(b"\x1b")
        self.assertEqual(session.read_buffer(), (line, len("rsync --ar")))
        self.assertFalse(session.executed.exists())

    def test_custom_trigger_category_and_accept_bindings(self):
        session = self.start(custom=True)
        session.open("rsync ")
        session.send("n")
        session.finish("a")
        self.assertEqual(session.read_buffer(), ("rsync --dry-run ", 16))
        self.assertFalse(session.executed.exists())

    def test_unicode_prefix_preserves_bash_character_offset(self):
        session = self.start()
        session.open('rsync "café/日本" --ar')
        session.finish("\n")
        expected = 'rsync "café/日本" --archive '
        self.assertEqual(session.read_buffer(), (expected, len(expected)))

    def test_scroll_categories_and_options(self):
        session = self.start()
        session.open("rsync ")
        session.send(b"\t\x1bOF")
        session.expect(b"Recovery")
        session.send(b"\t\x1bOF")
        session.finish("\n")
        self.assertEqual(session.read_buffer()[0], "rsync --backup-dir=")

    def test_search_applies_before_insertion(self):
        session = self.start()
        session.open("rsync ")
        session.send("/checksum\n")
        session.expect(b"--checksum")
        session.finish("\n")
        self.assertEqual(session.read_buffer()[0], "rsync --checksum ")

    def test_control_c_cancels_and_shell_remains_usable(self):
        session = self.start()
        session.open("rsync ")
        session.finish(b"\x03")
        self.assertEqual(session.read_buffer(), ("rsync ", 6))
        session.send(session.trigger)
        session.expect(b"Interactive help")
        session.finish("\n")
        self.assertEqual(session.read_buffer()[0], "rsync --archive ")

    def test_shell_substitution_is_not_evaluated(self):
        session = self.start()
        marker = Path(self.temp.name, "substitution-executed")
        line = f"rsync $(touch {shlex.quote(str(marker))}) --"
        session.send(line)
        session.send(session.trigger)
        session.expect(b"Shell expansions are not supported")
        self.assertEqual(session.read_buffer()[0], line)
        self.assertFalse(marker.exists())
        self.assertFalse(session.executed.exists())

    def test_invalid_configuration_preserves_buffer(self):
        session = self.start(custom=True)
        Path(self.temp.name, "keys.json").write_text('{"keys":{"accept":["j"]}}')
        session.send("rsync --ar")
        session.send(session.trigger)
        session.expect(b"A key is assigned to more than one action")
        self.assertEqual(session.read_buffer(), ("rsync --ar", 10))
        self.assertFalse(session.executed.exists())

    def test_non_utf8_locale_is_rejected_without_edit(self):
        session = self.start(locale_name="C")
        session.send("rsync --ar")
        session.send(session.trigger)
        session.expect(b"A UTF-8 shell locale is required")
        self.assertEqual(session.read_buffer(), ("rsync --ar", 10))

    def test_small_terminal_can_cancel_and_recover_after_resize(self):
        session = self.start()
        session.open("rsync ")
        fcntl.ioctl(session.fd, termios.TIOCSWINSZ, struct.pack("HHHH", 10, 40, 0, 0))
        session.expect(b"Resize to at least")
        session.finish(b"\x1b")
        self.assertEqual(session.read_buffer(), ("rsync ", 6))
        fcntl.ioctl(session.fd, termios.TIOCSWINSZ, struct.pack("HHHH", 24, 100, 0, 0))
        session.send(session.trigger)
        session.expect(b"Interactive help")
        session.finish("\n")
        self.assertEqual(session.read_buffer()[0], "rsync --archive ")

    def test_midline_insertion_preserves_suffix_and_cursor(self):
        session = self.start()
        session.send('rsync --arch "target folder"')
        session.send(b"\x01" + b"\x06" * len("rsync --ar"))
        session.send(session.trigger)
        session.expect(b"Interactive help")
        session.finish("\n")
        self.assertEqual(session.read_buffer(), ('rsync --archive "target folder"', 16))
        self.assertFalse(session.executed.exists())

    def test_automatic_discovery_inserts_without_executing_pending_arguments(self):
        from test_discovery import make_commands
        command, invocation_log, executed = make_commands(Path(self.temp.name))
        session = self.start(extra_environment={"PATH": str(command.parent) + ":" + os.environ["PATH"]})
        line = 'discover-tool "pending file" --al'
        session.open(line)
        session.finish("\n")
        self.assertEqual(session.read_buffer()[0], 'discover-tool "pending file" --alpha ')
        self.assertEqual(json.loads(invocation_log.read_text()), ["--help"])
        self.assertFalse(executed.exists())

    def test_automatic_discovery_cancellation_preserves_line(self):
        from test_discovery import make_commands
        command, _, executed = make_commands(Path(self.temp.name))
        session = self.start(extra_environment={"PATH": str(command.parent) + ":" + os.environ["PATH"]})
        line = "discover-tool --al"
        session.open(line)
        session.finish(b"\x1b")
        self.assertEqual(session.read_buffer(), (line, len(line)))
        self.assertFalse(executed.exists())

    def test_man_only_browser_never_invokes_target(self):
        from test_discovery import make_commands
        command, invocation_log, executed = make_commands(Path(self.temp.name))
        session = self.start(extra_environment={"PATH": str(command.parent) + ":" + os.environ["PATH"], "CLI_HELP_DISCOVERY": "man"})
        session.open("discover-tool --manual")
        session.finish("\n")
        self.assertEqual(session.read_buffer()[0], "discover-tool --manual-only=")
        self.assertFalse(invocation_log.exists())
        self.assertFalse(executed.exists())

    def test_discovery_failure_preserves_pending_buffer(self):
        from test_discovery import make_commands, write_executable
        command, _, executed = make_commands(Path(self.temp.name))
        write_executable(command, "print('No help available')\n")
        write_executable(command.parent / "man", "print('No manual entry')\n")
        session = self.start(extra_environment={"PATH": str(command.parent) + ":" + os.environ["PATH"]})
        line = "discover-tool private-file --"
        session.send(line)
        session.send(session.trigger)
        session.expect(b"No recognizable option declarations")
        self.assertEqual(session.read_buffer(), (line, len(line)))
        self.assertFalse(executed.exists())

    def test_docker_subcommand_insertion_preserves_pending_action_and_suffix(self):
        from test_subcommands import make_subcommands
        binaries, executed = make_subcommands(Path(self.temp.name))
        session = self.start(extra_environment={"PATH": str(binaries) + ":" + os.environ["PATH"]})
        prefix = "docker -Hprivate-host run --name 'private name' --det"
        line = prefix + " private-image sh -c 'touch marker'"
        session.send(line)
        session.send(b"\x01" + b"\x06" * len(prefix))
        session.send(session.trigger)
        session.expect(b"Interactive help")
        session.finish("\n")
        expected = line.replace("--det ", "--detach ")
        self.assertEqual(session.read_buffer(), (expected, len(prefix) + 4))
        self.assertEqual(json.loads(Path(self.temp.name, "docker-calls").read_text()), ["help", "run"])
        self.assertFalse(executed.exists())

    def test_nested_docker_cancellation_preserves_pending_command(self):
        from test_subcommands import make_subcommands
        binaries, executed = make_subcommands(Path(self.temp.name))
        session = self.start(extra_environment={"PATH": str(binaries) + ":" + os.environ["PATH"]})
        line = "docker --context private container run --det"
        session.open(line)
        session.finish(b"\x1b")
        self.assertEqual(session.read_buffer(), (line, len(line)))
        self.assertEqual(json.loads(Path(self.temp.name, "docker-calls").read_text()), ["help", "container", "run"])
        self.assertFalse(executed.exists())

    def test_git_discovered_subcommand_uses_manual_without_invoking_git(self):
        from test_subcommands import make_subcommands
        binaries, executed = make_subcommands(Path(self.temp.name))
        session = self.start(extra_environment={"PATH": str(binaries) + ":" + os.environ["PATH"]})
        line = "git -C 'private repo' branch --al"
        session.open(line)
        session.finish("\n")
        expected = "git -C 'private repo' branch --all "
        self.assertEqual(session.read_buffer(), (expected, len(expected)))
        self.assertFalse(Path(self.temp.name, "git-calls").exists())
        self.assertEqual(json.loads(Path(self.temp.name, "man-calls").read_text())[-1], "git-branch")
        self.assertFalse(executed.exists())

    def test_loaded_driver_inserts_without_executing_pending_action(self):
        from test_drivers import install_driver_fixture
        drivers, binaries, log, marker = install_driver_fixture(Path(self.temp.name))
        session = self.start(extra_environment={"PATH": str(binaries) + ":" + os.environ["PATH"],
                                               "CLI_HELP_DRIVERS": str(drivers)})
        line = "newtool --config 'private config' image convert --fa"
        session.open(line)
        session.finish("\n")
        expected = line[:-4] + "--fast "
        self.assertEqual(session.read_buffer(), (expected, len(expected)))
        self.assertEqual(json.loads(log.read_text()), ["help", "image", "convert"])
        self.assertFalse(marker.exists())

    def test_invalid_driver_preserves_pending_buffer_without_probes(self):
        from test_drivers import install_driver_fixture
        drivers, binaries, log, marker = install_driver_fixture(Path(self.temp.name))
        (drivers / "newtool.json").write_text('{"command":"newtool","paths":[]}')
        session = self.start(extra_environment={"PATH": str(binaries) + ":" + os.environ["PATH"],
                                               "CLI_HELP_DRIVERS": str(drivers)})
        line = "newtool image convert --fa"
        session.send(line)
        session.send(session.trigger)
        session.expect(b"Invalid driver")
        self.assertEqual(session.read_buffer(), (line, len(line)))
        self.assertFalse(log.exists())
        self.assertFalse(marker.exists())

    def test_suffix_help_driver_preserves_cloud_arguments_and_cancel(self):
        from test_discovery import write_executable
        folder = Path(self.temp.name)
        binaries = folder / "bin"
        binaries.mkdir()
        log, marker = folder / "aws-calls", folder / "action-dispatched"
        write_executable(binaries / "aws", "import json, pathlib, sys\n"
                         f"pathlib.Path({str(log)!r}).write_text(json.dumps(sys.argv[1:]))\n"
                         "if sys.argv[1:] != ['s3', 'cp', 'help']:\n"
                         f"    pathlib.Path({str(marker)!r}).touch()\n"
                         "print('Options:\\n  --recursive  Copy recursively.\\n  --exclude (string)  Exclude a pattern.')\n")
        session = self.start(extra_environment={"PATH": str(binaries) + ":" + os.environ["PATH"],
                                               "CLI_HELP_DRIVERS": str(ROOT / "config/drivers.example")})
        line = "aws --profile private s3 cp 'private file' s3://private --rec"
        session.open(line)
        session.finish(b"\x1b")
        self.assertEqual(session.read_buffer(), (line, len(line)))
        session.send(session.trigger)
        session.expect(b"Interactive help")
        session.finish("\n")
        expected = line[:-5] + "--recursive "
        self.assertEqual(session.read_buffer(), (expected, len(expected)))
        self.assertEqual(json.loads(log.read_text()), ["s3", "cp", "help"])
        self.assertFalse(marker.exists())

    def test_imported_manual_profile_loads_and_inserts_without_target_execution(self):
        from test_discovery import MAN_TEXT, write_executable
        from manual_import import import_manual
        folder = Path(self.temp.name)
        source = folder / "manual.txt"
        source.write_text(MAN_TEXT)
        result = import_manual(["newtool", "convert"], folder / "collection", text_file=source)
        binaries = folder / "bin"
        binaries.mkdir()
        marker = folder / "target-executed"
        write_executable(binaries / "newtool", f"import pathlib\npathlib.Path({str(marker)!r}).touch()\n")
        session = self.start(extra_environment={"PATH": str(binaries) + ":" + os.environ["PATH"],
                                               "CLI_HELP_DRIVERS": result["driver_directory"],
                                               "CLI_HELP_PROFILES": result["profile_directory"]})
        session.open("newtool convert --al")
        session.finish("\n")
        expected = "newtool convert --alpha "
        self.assertEqual(session.read_buffer(), (expected, len(expected)))
        self.assertFalse(marker.exists())

    def test_empty_quoted_argument_is_preserved(self):
        session = self.start()
        line = "rsync ''"
        session.send(line)
        session.send(session.trigger)
        session.expect(b"Move the cursor to an empty argument or an option name")
        self.assertEqual(session.read_buffer(), (line, len(line)))
        self.assertFalse(session.executed.exists())

    def test_unsupported_subcommand_preserves_line_without_probes(self):
        from test_subcommands import make_subcommands
        binaries, executed = make_subcommands(Path(self.temp.name))
        session = self.start(extra_environment={"PATH": str(binaries) + ":" + os.environ["PATH"]})
        line = "docker compose up --det"
        session.send(line)
        session.send(session.trigger)
        session.expect(b"Unsupported subcommand")
        self.assertEqual(session.read_buffer(), (line, len(line)))
        self.assertFalse(Path(self.temp.name, "docker-calls").exists())
        self.assertFalse(Path(self.temp.name, "man-calls").exists())
        self.assertFalse(executed.exists())


if __name__ == "__main__":
    unittest.main()
