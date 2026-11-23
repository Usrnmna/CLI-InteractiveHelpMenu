"""Exercise GNU grep's byte output, status and option grammar on private inputs."""

import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest


CAPTURES = Path(__file__).resolve().parent / "fixtures" / "grep"


@unittest.skipUnless(sys.platform.startswith("linux") and shutil.which("grep"), "Requires Linux grep")
class PackagedGrepTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Identify the installed GNU release before asserting version-specific behavior."""
        cls.binary = shutil.which("grep")
        cls.env = {"LC_ALL": "C", "TERM": "xterm", "GREP_COLORS": "ms=01;31"}
        version = subprocess.run([cls.binary, "--version"], env=cls.env, capture_output=True, timeout=10)
        match = re.match(rb"grep \(GNU grep\) (3\.11|3\.12)\n", version.stdout)
        if not match or version.returncode:
            raise unittest.SkipTest("Behavior fixtures cover GNU grep 3.11 and 3.12")
        cls.version = match[1].decode("ascii")
        cls.version_output = version.stdout

    def setUp(self):
        """All file operands resolve relative to a fresh temporary directory."""
        temporary = tempfile.TemporaryDirectory(prefix="cli-help-grep-")
        self.addCleanup(temporary.cleanup)
        self.tree = Path(temporary.name)

    def put(self, name, data):
        path = self.tree / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    def grep(self, *args, data=b"", locale="C", **kwargs):
        """Keep raw bytes and exit status independent of the terminal and shell."""
        return subprocess.run([self.binary, *args], input=data, cwd=self.tree,
                              env={**self.env, "LC_ALL": locale}, timeout=10,
                              stderr=subprocess.PIPE, stdout=kwargs.pop("stdout", subprocess.PIPE), **kwargs)

    def check(self, args, output, status=0, **kwargs):
        """Assert ordinary (diagnostic-free) output, including literal file delimiters."""
        result = self.grep(*args, **kwargs)
        self.assertEqual((result.stdout, result.stderr, result.returncode), (output, b"", status), args)

    def test_fixed_help_and_packaged_version(self):
        self.check(["--help"], (CAPTURES / f"gnu-grep-{self.version}-help.txt").read_bytes())
        version_capture = (CAPTURES / f"gnu-grep-{self.version}-version.txt").read_bytes()
        # A distro can rebuild the same grep against another PCRE2 minor release.
        self.assertEqual(self.version_output.splitlines()[0], version_capture.splitlines()[0])

    def test_filename_and_record_delimiters(self):
        self.put("in", b"xx\ny\nz\0wxx\0")
        self.put("text", b"xx\nnone\n")
        self.check(["-HZ", "x", "text"], b"text\0xx\n")
        self.check(["-Hz", "x", "in"], b"in:xx\ny\nz\0in:wxx\0")
        self.check(["-HozZ", "x", "in"], b"in\0x\0" * 4)
        self.check(["-Hoz", "x", "in"], b"in:x\0" * 4)
        self.check(["-lz", "x", "in"], b"in\n")
        self.check(["-lzZ", "x", "in"], b"in\0")
        self.check(["-HzcZ", "x", "in"], b"in\x002\n")
        self.check(["-LzZ", "missing", "in"], b"in\0", 1)

    def test_pattern_sources_and_aliases(self):
        data = b"-x\nA.\nAy\nz\n"
        self.put("empty", b"")
        self.put("blank", b"\n")
        self.put("pats", b"^z$\n")
        self.check(["--", "-x"], b"-x\n", data=data)
        self.check(["-e", "-x", "-f", "pats", "-e", "A[.]"], b"-x\nA.\nz\n", data=data)
        self.check(["-e", ""], data, data=data)
        self.check(["-f", "blank"], data, data=data)
        self.check(["-f", "empty"], b"", 1, data=data)
        self.check(["-y", "--fixed-regexp", "a."], b"A.\n", data=data)
        self.check(["-X", "fgrep", "A."], b"A.\n", data=data)
        self.check(["-X", "awk", "A."], b"A.\nAy\n", data=data)
        self.assertEqual(self.grep("-X", "invalid-matcher", "x", data=data).returncode, 2)
        for name in ("-u", "--unix-byte-offsets"):
            with self.subTest(name=name):
                result = self.grep(name, "z", data=data)
                if self.version == "3.11":
                    self.assertEqual((result.stdout, result.returncode), (b"z\n", 0))
                    self.assertIn(b"obsolete", result.stderr)
                else:
                    self.assertEqual((result.stdout, result.returncode), (b"", 2))
                    self.assertTrue(result.stderr)

    def test_perl_patterns_on_the_linked_pcre2(self):
        release = re.search(rb"grep -P uses PCRE2 (\d+)\.(\d+)", self.version_output)
        if not release:
            self.skipTest("This GNU grep build does not advertise PCRE2")
        modern = tuple(map(int, release.groups())) >= (10, 43)
        digits = "٣\n3\n".encode("utf-8")
        cases = [(r"\d", b"3\n"), ("[[:digit:]]", digits if modern else b"3\n"), (r"\p{Nd}", digits)]
        for pattern, expected in cases:
            self.check(["-P", pattern], expected, data=digits, locale="C.UTF-8")
        for pattern, expected in [(r"(?aD)\d", b"3\n"), (r"(?-aD)\d", digits)]:
            if modern:
                self.check(["-P", pattern], expected, data=digits, locale="C.UTF-8")
            else:
                result = self.grep("-P", pattern, data=digits, locale="C.UTF-8")
                self.assertEqual((result.stdout, result.returncode), (b"", 2))
                self.assertTrue(result.stderr)
        result = self.grep("-P", "-e", "x", "-e", "y", data=b"x\n")
        self.assertEqual((result.stdout, result.returncode), (b"", 2))
        self.assertIn(b"single pattern", result.stderr)
        self.check(["-P", "(?s)a.b"], b"", 1, data=b"a\nb\n")
        self.check(["-zP", "(?s)a.b"], b"a\nb\0", data=b"a\nb\0")

    def test_counts_file_lists_and_error_status(self):
        self.put("hit", b"before\nx x\nafter\nx\n")
        self.put("miss", b"other\n")
        self.check(["-c", "x", "hit", "miss"], b"hit:2\nmiss:0\n")
        self.check(["-cvm1", "x", "hit", "miss"], b"hit:1\nmiss:1\n")
        self.check(["-om1", "x", "hit"], b"x\nx\n")
        self.check(["-vo", "x", "hit"], b"")
        self.check(["-l", "x", "hit", "miss"], b"hit\n")
        self.check(["-L", "x", "miss", "hit"], b"miss\n")
        self.check(["-L", "x", "miss"], b"miss\n", 1)
        self.check(["-L", "x", "hit"], b"")
        result = self.grep("-q", "x", "absent", "hit")
        self.assertEqual((result.returncode, result.stdout), (0, b""))
        self.assertIn(b"absent", result.stderr)
        self.check(["-sq", "x", "absent", "hit"], b"")
        self.check(["-s", "x", "absent", "hit"], b"hit:x x\nhit:x\n", 2)

    def test_limits_and_resume_position(self):
        """Distinguish the installed -m sentinels from ordinary per-file limits."""
        self.put("in", b"before\nhit\nafter\nhit\n")
        self.check(["-vc", "hit", "in"], b"2\n")
        self.check(["-vc", "-m-1", "hit", "in"], b"0\n", 1)
        self.check(["-v", "-m-1", "hit", "in"], b"", 1)
        self.check(["-m-1", "hit", "in"], b"hit\nhit\n")
        self.check(["-m0", "-c", "hit", "absent"], b"", 1)
        self.check(["-m0", "-L", "hit", "in"], b"in\n", 1)
        missing = self.grep("-m0", "-L", "hit", "absent")
        self.assertEqual((missing.returncode, missing.stdout), (2, b""))
        self.assertIn(b"absent", missing.stderr)
        with (self.tree / "in").open("rb") as stream:
            self.check(["-m1", "-A1", "hit"], b"hit\nafter\n", stdin=stream, data=None)
            self.assertEqual(stream.read(), b"after\nhit\n")

    def test_context_group_separators_and_offsets(self):
        data = b"1\n2\n3\n4\n5\n6\n7\n8\n9\n"
        groups = b"2\n3\n4\n--\n7\n8\n9\n"
        for switches in (["-1"], ["-C1"], ["-A1", "-B1"]):
            self.check([*switches, "[38]"], groups, data=data)
        self.check(["-o", "-C1", "[38]"], b"3\n--\n8\n", data=data)
        self.check(["-C0", "--group-separator=", "[38]"], b"3\n\n8\n", data=data)
        self.check(["-C0", "--no-group-separator", "[38]"], b"3\n8\n", data=data)
        self.check(["-zC0", "x"], b"x\0--\nx\0", data=b"x\0other\0x\0")
        self.check(["-nbo", "x"], b"2:3:x\n2:5:x\n", data="é\nx x\n".encode())

    def test_explicit_paths_and_recursive_symlinks(self):
        self.put("sub/a.txt", b"hit\n")
        self.put("sub/skip/b.txt", b"hit\n")
        (self.tree / "dirlink").symlink_to("sub", target_is_directory=True)
        (self.tree / "sub/link.txt").symlink_to("a.txt")
        self.check(["-l", "--include=sub/*.txt", "hit", "sub/a.txt"], b"sub/a.txt\n")
        self.check(["-rl", "--include=sub/*.txt", "hit", "sub"], b"", 1)
        self.check(["-rl", "--exclude-dir=skip", "hit", "dirlink"], b"dirlink/a.txt\n")
        listed = self.grep("-Rl", "--exclude-dir=skip", "hit", "dirlink")
        self.assertEqual((listed.returncode, listed.stderr), (0, b""))
        self.assertCountEqual(listed.stdout.splitlines(), [b"dirlink/a.txt", b"dirlink/link.txt"])
        self.check(["-rl", "--exclude=*", "--include=a.txt", "hit", "sub"], b"sub/a.txt\n")
        self.check(["-rl", "--include=a.txt", "--exclude=*", "hit", "sub"], b"", 1)

    def test_binary_policy_and_ubuntu_binary_mode(self):
        self.put("binary", b"prefix\0x\r\n")
        result = self.grep("x", "binary")
        self.assertEqual((result.returncode, result.stdout), (0, b""))
        self.assertIn(b"binary file matches", result.stderr)
        for name in ("-U", "--binary-files=binary"):
            other = self.grep(name, "x", "binary")
            self.assertEqual((other.returncode, other.stdout, other.stderr), (0, b"", result.stderr))
        for name in ("-a", "--binary-files=text"):
            self.check([name, "x", "binary"], b"prefix\0x\r\n")
        for name in ("-I", "--binary-files=without-match"):
            self.check([name, "x", "binary"], b"", 1)
        for switches in ([], ["-U"]):
            self.check([*switches, "x$"], b"", 1, data=b"x\r\n")

    def test_optional_color_value_and_terminal_detection(self):
        import pty
        import select
        self.put("input", b"x\nalways\n")
        self.check(["--color", "x", "input"], b"x\n")
        self.check(["--color", "always", "input"], b"always\n")
        self.check(["--color=never", "x", "input"], b"x\n")
        for flag in ("--color=", "--color=invalid"):
            self.check([flag, "x", "input"], (CAPTURES / f"gnu-grep-{self.version}-help.txt").read_bytes())
        forced = self.grep("--colour=always", "x", "input")
        self.assertEqual((forced.returncode, forced.stderr), (0, b""))
        self.assertIn(b"\x1b[", forced.stdout)
        master, slave = pty.openpty()
        try:
            colored = self.grep("--color", "x", "input", stdout=slave)
            self.assertEqual((colored.returncode, colored.stderr), (0, b""))
            self.assertTrue(select.select([master], [], [], 2)[0], "No terminal output from grep")
            self.assertIn(b"\x1b[", os.read(master, 1024))
        finally:
            os.close(slave)
            os.close(master)
