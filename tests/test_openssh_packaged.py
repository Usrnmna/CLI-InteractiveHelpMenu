"""Exercise Ubuntu OpenSSH clients with configuration dumps, inert transports and local pipes."""

import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


CAPTURES = Path(__file__).resolve().parent / "fixtures" / "openssh"


class PackagedOpenSSHTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Use a release-matched client directory, optionally supplied by the sandbox."""
        cls.bindir = Path(os.environ.get("OPENSSH_TEST_BINDIR", "/usr/bin"))
        cls.env = {"PATH": "/usr/bin:/bin", "LC_ALL": "C"}
        if "OPENSSH_TEST_LIBDIR" in os.environ:
            cls.env["LD_LIBRARY_PATH"] = os.environ["OPENSSH_TEST_LIBDIR"]
        ssh = cls.bindir / "ssh"
        if not ssh.is_file():
            raise unittest.SkipTest("Ubuntu OpenSSH client fixture unavailable")
        probe = subprocess.run([ssh, "-V"], env=cls.env, capture_output=True, timeout=5, check=True)
        captures = json.loads((CAPTURES / "captures.json").read_text())
        for data in captures.values():
            # Package rebuild and OpenSSL suffixes may vary within the same Ubuntu release.
            if probe.stderr.startswith(data["version"]["stderr"].split(" Ubuntu-")[0].encode() + b" Ubuntu-"):
                cls.capture = data
                break
        else:
            raise unittest.SkipTest("Packaged regressions cover Ubuntu OpenSSH 9.6p1 and 10.2p1")

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="cli-help-openssh-")
        self.addCleanup(temporary.cleanup)
        self.tree = Path(temporary.name)
        self.env = {**self.env, "HOME": str(self.tree)}
        self.stub = self.tree / "transport"
        self.stub.write_text('#!/bin/sh\nprintf "%s\\n" "$@" > transport.args\nexit 73\n')
        self.stub.chmod(0o700)

    def invoke(self, client, *args, input_text=""):
        """Capture both streams and status with an empty stdin unless a batch is supplied."""
        return subprocess.run([self.bindir / client, *args], cwd=self.tree, env=self.env,
                              input=input_text.encode(), capture_output=True, timeout=10)

    def transport(self, client, *options, operands=None):
        """Return the exact transport arguments; a parser rejection leaves no record."""
        record = self.tree / "transport.args"
        record.unlink(missing_ok=True)
        if operands is None:
            operands = ("origin.invalid:input", "output") if client == "scp" else ("origin.invalid",)
        result = self.invoke(client, "-S", self.stub, *options, *operands)
        self.assertEqual(result.stdout, b"")
        return result, record.read_text().splitlines() if record.exists() else []

    def config(self, *args):
        """Dump evaluated options without reading configuration files or opening a connection."""
        result = self.invoke("ssh", "-G", "-T", "-F", "none", *args)
        self.assertEqual((result.returncode, result.stderr), (0, b""), args)
        return result.stdout.decode().splitlines()

    def server(self):
        """Use the packaged SFTP server as a subprocess without starting an SSH daemon."""
        path = Path(os.environ.get("OPENSSH_TEST_SERVER", "/usr/lib/openssh/sftp-server"))
        if not path.is_file():
            self.skipTest("Local openssh-sftp-server fixture unavailable")
        return path

    def test_fixed_usage_and_unsupported_protocol(self):
        for client, record in self.capture["usage"].items():
            with self.subTest(client=client):
                result = self.invoke(client)
                usage = (CAPTURES / record["stderr_file"]).read_bytes()
                self.assertEqual((result.returncode, result.stdout, result.stderr),
                                 (record["status"], b"", usage))
                rejected = self.invoke(client, "-1")
                self.assertEqual((rejected.returncode, rejected.stdout), (255, b""))
                self.assertIn(b"SSH protocol v.1 is no longer supported", rejected.stderr)
        version = self.invoke("ssh", "-V")
        ignored = self.invoke("ssh", "-2", "-V")
        self.assertEqual((ignored.returncode, ignored.stdout, ignored.stderr), (0, b"", version.stderr))
        help_option = self.invoke("sftp", "-h")
        self.assertEqual((help_option.returncode, help_option.stdout, help_option.stderr),
                         (1, b"", self.invoke("sftp").stderr))

    def test_ssh_local_queries_and_release_specific_rejections(self):
        query = self.invoke("ssh", "-Q", "cipher")
        self.assertEqual((query.returncode, query.stderr), (0, b""))
        self.assertIn(b"aes128-ctr", query.stdout.splitlines())
        unsupported = self.invoke("ssh", "-Z", "-G", "-F", "none", "fixture.invalid")
        self.assertEqual((unsupported.returncode, unsupported.stdout), (255, b""))
        self.assertIn(b"unknown option -- Z", unsupported.stderr)
        for command in ("conninfo", "channels"):
            rejected = self.invoke("ssh", "-G", "-F", "none", "-O", command, "fixture.invalid")
            self.assertEqual((rejected.returncode, rejected.stdout, rejected.stderr),
                             (255, b"", b"Invalid multiplex command.\r\n"))
        self.assertIn("controlmaster ask", self.config("-MM", "-S", "none", "fixture.invalid"))
        for command in ("forward", "proxy"):
            self.assertIn("controlmaster false", self.config("-O", command, "fixture.invalid"))

    def test_ssh_configuration_and_remote_command_boundary(self):
        lines = self.config("-X", "-L", "/tmp/listen:/tmp/connect", "-R", "0",
                            "-D", "localhost:5555", "fixture.invalid", "-p", "2022", "echo", "-p", "2023")
        for expected in ("port 2022", "forwardx11 yes", "forwardx11trusted yes",
                         "localforward /tmp/listen /tmp/connect", "remoteforward 0 [socks]:0",
                         "dynamicforward [localhost]:5555"):
            self.assertIn(expected, lines)
        self.assertIn("port 22", self.config("fixture.invalid", "echo", "-p", "2023"))
        self.assertIn("forwardx11trusted no", self.config("-X", "-oForwardX11Trusted=no", "fixture.invalid"))

    def test_attached_filename_preserves_leading_equals_and_dash(self):
        """Getopt hands the complete filename to SSH, including punctuation in the first byte."""
        for name, arguments in (("=private.conf", ["-F=private.conf"]),
                                ("-private.conf", ["-F", "-private.conf"])):
            (self.tree / name).write_text("Host fixture.invalid\n    Port 54321\n")
            result = self.invoke("ssh", "-G", "-T", *arguments, "fixture.invalid")
            with self.subTest(client="ssh", name=name):
                self.assertEqual((result.returncode, result.stderr), (0, b""))
                self.assertIn(b"port 54321", result.stdout.splitlines())
            for client in ("scp", "sftp"):
                with self.subTest(client=client, name=name):
                    _, transport = self.transport(client, *arguments)
                    self.assertEqual(transport[transport.index("-F") + 1], name)

    def test_transfer_protocol_subsystem_and_remote_copy_routing(self):
        for client in ("scp", "sftp"):
            result, default = self.transport(client)
            self.assertEqual(result.returncode, 255)
            self.assertIn(b"Connection closed", result.stderr)
            self.assertEqual(default[-4:], ["-s", "--", "origin.invalid", "sftp"])
            self.assertEqual(self.transport(client, "-2")[1], default)
        self.assertEqual(self.transport("scp", "-O", "-s")[1][-4:], ["-s", "--", "origin.invalid", "sftp"])
        legacy, args = self.transport("scp", "-s", "-O")
        self.assertEqual((legacy.returncode, legacy.stderr), (1, b""))
        self.assertEqual(args[-3:], ["--", "origin.invalid", "scp -f input"])
        for option in ((), ("-3",)):
            _, args = self.transport("scp", *option, operands=("origin.invalid:from", "dest.invalid:to"))
            self.assertEqual(args[-4:], ["-s", "--", "dest.invalid", "sftp"])
        direct, args = self.transport("scp", "-R", operands=("origin.invalid:from", "dest.invalid:to"))
        self.assertEqual((direct.returncode, direct.stderr), (1, b""))
        self.assertEqual(args[-5:], ["--", "origin.invalid", "scp", "from", "dest.invalid:to"])
        _, args = self.transport("sftp", "-s", "custom")
        self.assertEqual(args[-4:], ["-s", "--", "origin.invalid", "custom"])
        _, args = self.transport("sftp", "-s", "/remote/server")
        self.assertNotIn("-s", args)
        self.assertEqual(args[-3:], ["--", "origin.invalid", "/remote/server"])

    def test_transfer_option_ranges_before_transport(self):
        for client in ("scp", "sftp"):
            for option in (("-l1",), ("-l", "104857600"), ("-Xbuffer=256K",), ("-X", "nrequests=262144")):
                with self.subTest(client=client, option=option):
                    self.assertTrue(self.transport(client, *option)[1])
            for value in ("0", "104857601", "1K"):
                result, args = self.transport(client, "-l", value)
                self.assertEqual((result.returncode, args), (1, []))
                self.assertTrue(result.stderr.startswith(b"usage:"))
            for value in ("buffer=0", "buffer=262145", "nrequests=0", "nrequests=262145", "requests=2"):
                result, args = self.transport(client, "-X", value)
                self.assertEqual((result.returncode, args), (255, []))
                self.assertIn(b"Invalid", result.stderr)
        for flag in ("-B", "-R"):
            for value in ("-1", "262145"):
                # An inert transport never allocates the parsed value or starts a transfer.
                self.assertTrue(self.transport("sftp", flag, value)[1])
            for value in ("0", "1K"):
                result, args = self.transport("sftp", flag, value)
                self.assertEqual((result.returncode, args), (255, []))
                self.assertIn(b"Invalid", result.stderr)

    def test_recursive_symlinks_with_local_sftp_server(self):
        server = self.server()
        (self.tree / "source").mkdir()
        (self.tree / "source/plain").write_bytes(b"plain")
        (self.tree / "outside").write_bytes(b"linked")
        (self.tree / "source/alias").symlink_to("../outside")
        copy = self.invoke("scp", "-O", "-s", "-D", server, "-r", "fixture:source", "scp-tree")
        self.assertEqual((copy.returncode, copy.stdout, copy.stderr), (0, b"", b""))
        batch = self.invoke("sftp", "-D", server, "-r", "-b", "-", input_text="get source sftp-tree\n")
        self.assertEqual(batch.returncode, 0, batch.stderr)
        for directory in ("scp-tree", "sftp-tree"):
            self.assertEqual((self.tree / directory / "plain").read_bytes(), b"plain")
        self.assertEqual((self.tree / "scp-tree/alias").read_bytes(), b"linked")
        self.assertFalse((self.tree / "scp-tree/alias").is_symlink())
        self.assertFalse(os.path.lexists(self.tree / "sftp-tree/alias"))

    def test_sftp_resume_flush_and_batch_termination(self):
        """Observe fsync requests in the local server log and inspect the transferred bytes."""
        server = self.server()
        (self.tree / "origin").write_bytes(b"0123456789")
        (self.tree / "resumed").write_bytes(b"xx")
        result = self.invoke("sftp", "-af", "-D", f"{server} -e -l VERBOSE", "-b", "-",
                             input_text="get origin resumed\nget origin new\nput origin absent\nmkdir unreached\n")
        self.assertEqual(result.returncode, 1)
        self.assertIn(b"stat remote: No such file or directory", result.stderr)
        self.assertEqual((self.tree / "resumed").read_bytes(), b"xx23456789")
        self.assertEqual((self.tree / "new").read_bytes(), b"0123456789")
        self.assertFalse((self.tree / "absent").exists())
        self.assertFalse((self.tree / "unreached").exists())
        (self.tree / "partial").write_bytes(b"xx")
        result = self.invoke("sftp", "-af", "-D", f"{server} -e -l VERBOSE", "-b", "-",
                             input_text="-get missing ignore\nput origin partial\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(b'fsync "', result.stderr)
        self.assertEqual((self.tree / "partial").read_bytes(), b"xx23456789")
