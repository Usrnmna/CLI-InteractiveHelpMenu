"""Run checksum-pinned Mike Farah clients on disposable files in an offline sandbox."""

import hashlib
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

from test_yq_manual_inventory import FIXTURES, HEADER


DIGESTS = {
    "4.44.3": "a2c097180dd884a8d50c956ee16a9cec070f30a7947cf4ebf87d5f36213e9ed7",
    "4.54.3": "129534601871538efe0ba4c5e62a34fb1d5f469bcb975c4fddeb467d82974973",
}


@unittest.skipUnless(os.environ.get("YQ_TEST_BINDIR"), "Pinned yq release fixtures unavailable")
class YqReleaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Require both exact release binaries whenever a fixture directory is supplied."""
        cls.clients = {}
        for version, digest in DIGESTS.items():
            binary = Path(os.environ["YQ_TEST_BINDIR"]).resolve() / ("yq-" + version)
            if hashlib.sha256(binary.read_bytes()).hexdigest() != digest:
                raise ValueError(f"Wrong SHA-256 for {binary}")
            cls.clients[version] = binary

    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)

    def invoke(self, version, *args, data=b"", code=0, stdout=None, error=b""):
        """Capture status and streams independently, using only private paths and stdin."""
        p = subprocess.run([self.clients[version], "eval", *args], cwd=self.root,
                           input=data, capture_output=True, timeout=5)
        self.assertEqual(p.returncode, code, (args, p.stdout, p.stderr))
        if stdout is not None:
            self.assertEqual(p.stdout, stdout, args)
        if error:
            self.assertIn(error, p.stderr, args)
        else:
            self.assertEqual(p.stderr, b"", args)
        return p.stdout

    def test_captured_flags_and_parser_forms(self):
        for version in self.clients:
            capture = (FIXTURES / (version + "-eval-help.txt")).read_bytes()
            self.invoke(version, "--help", stdout=capture)
            for alias, flag, operand in HEADER.findall(capture.decode()):
                for spelling in filter(None, (flag, alias)):
                    with self.subTest(version=version, spelling=spelling):
                        if operand:
                            self.invoke(version, spelling, code=1, stdout=b"", error=b"needs an argument")
                        else:
                            help_text = self.invoke(version, spelling + "=false", "--help")
                            self.assertIn(b"Usage:\n  yq eval ", help_text)
            for flag in ("--tojson", "-j"):
                self.invoke(version, flag, "-n", "-I0", '{"x": 1}', stdout=b'{"x":1}\n', error=b"deprecated")
            for flags in (["-I", "0"], ["-I=0"], ["--indent=0"], ["--indent", "0"]):
                self.invoke(version, *flags, "-ojson", "-n", '{"x": 1}', stdout=b'{"x":1}\n')
            self.invoke(version, "--version", code=1, stdout=b"", error=b"unknown flag")
            self.invoke(version, "--in-place", code=1, stdout=b"", error=b"unknown flag")

    def test_expression_file_and_sequential_input(self):
        rule = self.root / "query file.yq"
        rule.write_bytes(b".name\r\n")
        (self.root / "a.yml").write_bytes(b"name: first\n---\nname: second\n")
        (self.root / "b.yml").write_bytes(b"name: last\n")
        for version in self.clients:
            for flags in (["--from-file", rule.name], ["--from-file=" + rule.name], [rule.name],
                          ["--expression", ".other", "--from-file", rule.name]):
                self.invoke(version, "-N", *flags, "a.yml", "-", "b.yml", data=b"name: piped\n",
                            stdout=b"first\nsecond\npiped\nlast\n")
            (self.root / ".name").write_bytes(b"text\n")
            self.invoke(version, "--expression", ".name", "b.yml", stdout=b"last\n")
            self.assertEqual(rule.read_bytes(), b".name\r\n")

    def test_split_destinations_and_collisions(self):
        for version in self.clients:
            directory = self.root / version
            directory.mkdir()
            prefix = version + "/"
            data = b'n: one\n---\nn: two\n'
            naming = '"%sitem-" + ($index | tostring)' % prefix
            names = self.root / "names.yq"
            names.write_text(naming)
            self.invoke(version, "-N", "--split-exp", '"unused"', "--split-exp-file", names.name,
                        ".", "-", data=data, stdout=b"")
            self.assertEqual({p.name: p.read_bytes() for p in directory.iterdir()},
                             {"item-0.yml": b"n: one\n", "item-1.yml": b"n: two\n"})
            self.assertFalse((self.root / "unused.yml").exists())
            target = directory / "fixed.txt"
            target.write_bytes(b"prior contents")
            self.invoke(version, "-N", "-s", '"' + prefix + 'fixed.txt"', ".", "-", data=data, stdout=b"")
            self.assertEqual(target.read_bytes(), b"n: two\n")
            args = ("-s", '"' + prefix + 'nested/file"', ".", "-")
            if version == "4.44.3":
                self.invoke(version, *args, data=b"ok", code=1, stdout=b"", error=b"no such file")
                self.assertFalse((directory / "nested").exists())
            else:
                self.invoke(version, *args, data=b"ok", stdout=b"")
                self.assertEqual((directory / "nested/file.yml").read_bytes(), b"ok\n")

    def test_inplace_success_and_failure(self):
        a, b = self.root / "a.yml", self.root / "b.yml"
        for version in self.clients:
            a.write_bytes(b"n: 1\n")
            b.write_bytes(b"n: 2\n")
            self.invoke(version, "-i", ".n += 1", a.name, b.name, stdout=b"")
            combined = b"n: 2\n---\nn: 3\n"
            self.assertEqual((a.read_bytes(), b.read_bytes()), (combined, b"n: 2\n"))
            for args, error in ((["-e", "select(false)", a.name], b"no matches"),
                                ([".", a.name, "missing.yml"], b"no such file"),
                                (["-s", '"out"', ".", a.name], b"cannot be used with split")):
                self.invoke(version, "-i", *args, code=1, stdout=b"", error=error)
                self.assertEqual((a.read_bytes(), b.read_bytes()), (combined, b"n: 2\n"))
                self.assertEqual({p.name for p in self.root.iterdir()}, {a.name, b.name})

    def test_null_status_and_framing(self):
        for version in self.clients:
            self.invoke(version, "-n", '"new"', data=b"ignored", stdout=b"new\n")
            self.invoke(version, "-n", ".", "-", code=1, stdout=b"", error=b"cannot pass files")
            for value in (b'0', b'""', b'False', b'true\n---\nfalse'):
                self.invoke(version, "-e", ".", "-", data=value)
            self.invoke(version, "-e", ".", "-", data=b"null\n---\nfalse", code=1, error=b"no matches")
            self.invoke(version, "-e", "select(false)", "-", data=b"true", code=1, stdout=b"", error=b"no matches")
            self.invoke(version, "-N", "-0", ".", "-", data=b"one\n---\ntwo", stdout=b"one\0two\0")
            self.invoke(version, "-r=false", ".name", "-", data=b'name: "two" # retained\n',
                        stdout=b'"two" # retained\n')

    def test_encoders_and_release_sensitive_formatting(self):
        (self.root / "a.json").write_bytes(b'{"n":1}')
        for version in self.clients:
            self.invoke(version, "-I0", ".", "a.json", stdout=b'{"n":1}\n')
            self.invoke(version, "-pjson", ".", "-", data=b'{"n":1}', stdout=b"n: 1\n")
            self.invoke(version, "-pjson", "-ojson", "-I0", ".", "-", data=b'{"n":1}', stdout=b'{"n":1}\n')
            for width, spaces in [(0, 4 if version == "4.44.3" else 2), (10, 2 if version == "4.44.3" else 9)]:
                self.invoke(version, "--indent", str(width), ".", "-", data=b"a:\n  b: 2\n",
                            stdout=b"a:\n" + b" " * spaces + b"b: 2\n")
            if version == "4.44.3":
                self.invoke(version, "-oini", ".", "-", data=b"n: 1", code=1, error=b"unknown format")
            else:
                self.invoke(version, "-pini", "--ini-key-value-delimiters", ":", "-oy",
                            ".k", "-", data=b"k:value\n", stdout=b"value\n")
