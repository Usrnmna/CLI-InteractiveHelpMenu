"""Compare packaged GNU and uutils ls on disposable directories and raw output."""

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


CAPTURES = Path(__file__).resolve().parent / "fixtures" / "ls"
ENV = {"LC_ALL": "C", "TZ": "UTC", "TERM": "xterm", "LS_COLORS": "di=31"}


@unittest.skipUnless(sys.platform.startswith("linux"), "Ubuntu ls fixtures require Linux")
class PackagedLsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Identify the default binary and any GNU comparator by their own version banners."""
        banners = {p.read_bytes().splitlines()[0]: p.name.removesuffix("-version.txt")
                   for p in CAPTURES.glob("*-version.txt")}
        cls.releases = {}
        for path in (Path("/usr/bin/ls"), Path("/usr/bin/gnuls")):
            if path.is_file():
                result = subprocess.run([path, "--version"], cwd=tempfile.gettempdir(), env=ENV,
                                        capture_output=True, timeout=10)
                if result.returncode or not result.stdout:
                    continue
                release = banners.get(result.stdout.splitlines()[0])
                if release:
                    cls.releases[path] = release
        if not cls.releases:
            raise unittest.SkipTest("Fixtures cover GNU ls 9.4/9.7 and uutils ls 0.10.0")

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="cli-help-ls-")
        self.addCleanup(temporary.cleanup)
        self.tree = Path(temporary.name)

    def raw(self, binary, *args, env=None, stdout=subprocess.PIPE):
        """Run in the private directory with no inherited ls aliases, locale or size settings."""
        return subprocess.run([binary, *args], cwd=self.tree, env={**ENV, **(env or {})},
                              stdin=subprocess.DEVNULL, stdout=stdout, stderr=subprocess.PIPE, timeout=10)

    def output(self, binary, *args, env=None):
        result = self.raw(binary, *args, env=env)
        self.assertEqual((result.returncode, result.stderr), (0, b""), (binary, args))
        return result.stdout

    def terminal_output(self, binary, *args):
        """A raw PTY supplies isatty() without changing LF into CRLF on stdout."""
        import pty
        import tty
        master, slave = pty.openpty()
        try:
            tty.setraw(slave)
            result = self.raw(binary, *args, stdout=slave)
            self.assertEqual((result.returncode, result.stderr), (0, b""), (binary, args))
            os.set_blocking(master, False)
            return os.read(master, 8192)
        finally:
            os.close(slave)
            os.close(master)

    def test_fixed_help_and_version(self):
        for binary, release in self.releases.items():
            with self.subTest(binary=binary):
                expected_help = (CAPTURES / (release + "-help.txt")).read_bytes()
                if release.startswith("gnu-"):
                    # GNU includes argv[0] in the usage line; the comparator is installed as gnuls.
                    _, rest = expected_help.split(b" [OPTION]", 1)
                    expected_help = b"Usage: " + os.fsencode(binary) + b" [OPTION]" + rest
                self.assertEqual(self.output(binary, "--help"), expected_help)
                # Package rebuild annotations can change within the same upstream release.
                expected = (CAPTURES / (release + "-version.txt")).read_bytes().splitlines()[0]
                self.assertEqual(self.output(binary, "--version").splitlines()[0], expected)

    def test_allocation_length_units_and_totals(self):
        """Use stat's allocation for this filesystem, independently of ls display units."""
        sparse, payload = self.tree / "sparse", self.tree / "written"
        with sparse.open("wb") as stream:
            stream.truncate(1048576)
        payload.write_bytes(b"x" * 4608)
        allocated = payload.stat().st_blocks * 512
        self.assertLess(sparse.stat().st_blocks * 512, sparse.stat().st_size)
        for binary, release in self.releases.items():
            with self.subTest(binary=binary):
                def fields(*opts, env=None):
                    row = self.output(binary, "-ls", *opts, "written", env=env).split()
                    return int(row[0]), int(row[5])
                self.assertEqual(fields(), (allocated // 1024, 4608))
                self.assertEqual(fields(env={"BLOCKSIZE": "2K"}), (allocated // 2048, 4608))
                self.assertEqual(fields(env={"BLOCK_SIZE": "2K", "LS_BLOCK_SIZE": "1K"}), (allocated // 1024, 5))
                self.assertEqual(fields(env={"POSIXLY_CORRECT": "1"}), (allocated // 512, 4608))
                self.assertEqual(fields("-k", env={"BLOCK_SIZE": "2K"}), (allocated // 1024, 3))
                self.assertEqual(fields("--block-size=1", env={"LS_BLOCK_SIZE": "2K"}), (allocated, 4608))
                self.assertEqual(self.output(binary, "-S", "written", "sparse"), b"sparse\nwritten\n")
                self.assertEqual(self.output(binary, "-Sr", "written", "sparse"), b"written\nsparse\n")
                for mode, length in (("-h", b"1.0M"), ("--si", b"1.1M")):
                    self.assertEqual(self.output(binary, "-ls", mode, "sparse").split()[5], length)
                unit = allocated + 1
                truncated = release.startswith("uutils")
                self.assertEqual(fields("--block-size=" + str(unit))[0], 0 if truncated else 1)

        # Pick a unit above either file's allocation, but below the combined allocation.
        (self.tree / "small").write_bytes(b"x")
        unit = max(allocated, (self.tree / "small").stat().st_blocks * 512) + 1
        for binary, release in self.releases.items():
            with self.subTest(total=binary):
                output = self.output(binary, "-s", "--block-size=" + str(unit), ".")
                self.assertEqual(output.splitlines()[0], b"total 0" if release.startswith("uutils") else b"total 2")

    def test_filtering_and_recursive_aliases(self):
        root = self.tree / "root"
        (root / "real").mkdir(parents=True)
        (root / "real/file").touch()
        (root / "link").symlink_to("real")
        (root / ".hidden").touch()
        (root / "backup~").touch()
        for binary, release in self.releases.items():
            with self.subTest(binary=binary):
                plain = b"backup~\nlink\nreal\n"
                self.assertEqual(self.output(binary, "-aA", "root"), b".hidden\n" + plain)
                self.assertEqual(self.output(binary, "-Aa", "root"), b".\n..\n.hidden\n" + plain)
                self.assertEqual(self.output(binary, "-A", "--hide=*~", "root"), b".hidden\n" + plain)
                self.assertEqual(self.output(binary, "-AB", "root"), b".hidden\nlink\nreal\n")
                self.assertEqual(self.output(binary, "--ignore", "*~", "root/backup~"), b"root/backup~\n")
                implied = b".\n..\n" if release.startswith("uutils") else b""
                self.assertEqual(self.output(binary, "-a", "--ignore=.*", "root"), implied + plain)
                self.assertEqual(self.output(binary, "root/link"), b"file\n")
                self.assertTrue(self.output(binary, "-ld", "root/link").startswith(b"l"))
                for args in (("-ldH",), ("-ldL",), ("-ld", "--dereference-command-line-symlink-to-dir")):
                    self.assertTrue(self.output(binary, *args, "root/link").startswith(b"d"), args)
                self.assertNotIn(b"root/link:", self.output(binary, "-RH", "root"))
                self.assertEqual(self.output(binary, "-RL", "root/link", "root/real").count(b"file\n"), 2)
                recursive = self.raw(binary, "-RL", "root")
                if release.startswith("uutils"):
                    self.assertEqual((recursive.returncode, recursive.stdout.count(b"file\n")), (2, 1))
                    self.assertIn(b"already-listed directory", recursive.stderr)
                else:
                    self.assertEqual((recursive.returncode, recursive.stderr, recursive.stdout.count(b"file\n")),
                                     (0, b"", 2))

    def test_display_time_sort_key_and_unsorted_formats(self):
        for name, times in (("a", (500000, 200000)), ("b", (300000, 400000))):
            path = self.tree / name
            path.touch()
            os.utime(path, times)
        for binary, release in self.releases.items():
            with self.subTest(binary=binary):
                self.assertEqual(self.output(binary, "-t"), b"b\na\n")
                self.assertEqual(self.output(binary, "-tr"), b"a\nb\n")
                self.assertEqual(self.output(binary, "--time=mtime"), b"a\nb\n" if release == "gnu-ls-9.4" else b"b\na\n")
                for args, records in ((("-lt",), [b"400000 b", b"200000 a"]),
                                      (("-lut",), [b"500000 a", b"300000 b"]),
                                      (("-l", "--time=ctime"), None)):
                    listing = self.output(binary, *args, "--time-style=+%s", "a", "b").splitlines()
                    if records is None:
                        records = [f"{(self.tree / n).stat().st_ctime_ns // 10**9} {n}".encode() for n in ("a", "b")]
                    self.assertEqual([b" ".join(line.split()[-2:]) for line in listing], records)
                old = release == "gnu-ls-9.4"
                self.assertEqual(self.output(binary, "-lsf", "a") == b"a\n", old)
                self.assertNotEqual(self.output(binary, "-fls", "a"), b"a\n")
                self.assertEqual(b"//DIRED//" in self.output(binary, "-D", "."), not old)
                self.assertIn(b"//DIRED//", self.output(binary, "-lD", "."))
                name_sort = self.raw(binary, "--sort=name")
                if old:
                    self.assertEqual((name_sort.returncode, name_sort.stdout), (1, b""))
                    self.assertIn(b"name", name_sort.stderr)
                else:
                    self.assertEqual((name_sort.returncode, name_sort.stderr, name_sort.stdout), (0, b"", b"a\nb\n"))

    def test_optional_policies_on_a_pipe_and_terminal(self):
        for name in ("dir", "auto"):
            (self.tree / name).mkdir()
        for binary, release in self.releases.items():
            for flag, marker in (("--color", b"\x1b["), ("--classify", b"/"), ("--hyperlink", b"\x1b]8;;file:")):
                with self.subTest(binary=binary, flag=flag):
                    always = self.output(binary, "-1d", flag, "dir")
                    self.assertIn(marker, always)
                    for when in ("always", "yes", "force"):
                        self.assertEqual(self.output(binary, "-1d", flag + "=" + when, "dir"), always)
                    for when in ("never", "no", "none", "auto", "tty", "if-tty"):
                        self.assertEqual(self.output(binary, "-1d", flag + "=" + when, "dir"), b"dir\n")
                    self.assertIn(marker, self.terminal_output(binary, "-1d", flag + "=auto", "dir"))
                    self.assertEqual(self.terminal_output(binary, "-1d", flag + "=never", "dir"), b"dir\n")
                    separated = self.output(binary, "-1d", flag, "auto", "dir")
                    self.assertIn(b"auto", separated)
                    self.assertIn(marker, separated)
                    for invalid in ("", "AUTO"):
                        result = self.raw(binary, flag + "=" + invalid, "dir")
                        self.assertNotEqual(result.returncode, 0)
                        self.assertTrue(result.stderr)
                        self.assertEqual(result.stdout, b"")
            with self.subTest(aliases=binary):
                for alias in ("--long", "-V", "-F=auto"):
                    result = self.raw(binary, alias, "-d", "dir")
                    if release.startswith("uutils"):
                        self.assertEqual((result.returncode, result.stderr), (0, b""))
                        self.assertIn({"--long": b"dr", "-V": b"0.10.0", "-F=auto": b"dir\n"}[alias], result.stdout)
                    else:
                        self.assertEqual((result.returncode, result.stdout), (2, b""))
                        self.assertTrue(result.stderr)

    def test_null_delimiters_quoting_and_later_layouts(self):
        names = ("new\nline", "space name")
        for n in names:
            (self.tree / n).touch()
        for binary, release in self.releases.items():
            with self.subTest(binary=binary):
                self.assertEqual(self.output(binary, "-Q", "--zero", *names), b"new\nline\0space name\0")
                self.assertEqual(self.terminal_output(binary, "--zero", *names), b"new\nline\0space name\0")
                self.assertEqual(self.output(binary, "--zero", "-Q", *names), b'"new\\nline"\0"space name"\0')
                self.assertEqual(self.output(binary, "-b", names[0]), b"new\\nline\n")
                self.assertEqual(self.output(binary, "--zero", "-m", *names), b"new\nline, space name\0")
                columns = self.output(binary, "--zero", "-C", *names)
                self.assertTrue(columns.endswith(b"\n" if release.startswith("uutils") else b"\0"))

    def test_layout_aliases_and_recent_time_pair(self):
        """Check selector spellings and the order of two literal time formats."""
        (self.tree / "old").touch()
        os.utime(self.tree / "old", (200000, 200000))
        (self.tree / "recent").touch()
        for binary, release in self.releases.items():
            with self.subTest(binary=binary):
                rust = release.startswith("uutils")
                style = "--time-style=+OLD\nRECENT"
                lines = self.output(binary, "-l", style, "old", "recent").splitlines()
                self.assertTrue(lines[0].endswith(b"RECENT old" if rust else b"OLD old"))
                self.assertTrue(lines[1].endswith(b"OLD recent" if rust else b"RECENT recent"))
                quoted = self.output(binary, "--quoting-style=c-maybe", "old")
                self.assertEqual(quoted, b'"old"\n' if rust else b"old\n")
                self.assertEqual(self.output(binary, "-Q", "--l", "old"), b"old\n")
                result = self.raw(binary, "--format=columns", "old")
                if rust:
                    self.assertEqual((result.returncode, result.stderr, result.stdout), (0, b"", b"old\n"))
                else:
                    self.assertEqual((result.returncode, result.stdout), (1, b""))
                    self.assertIn(b"columns", result.stderr)
                self.assertEqual(self.output(binary, "-l1", "old"), self.output(binary, "-l", "old"))
                self.assertEqual(self.output(binary, "-l", "--format=single-column", "old"), b"old\n")

    def test_attached_short_values_and_dash_leading_operand(self):
        for name in ("=name", "name", "-a"):
            (self.tree / name).touch()
        for binary, release in self.releases.items():
            with self.subTest(binary=binary):
                ignored_name = b"-a\n=name\n"
                ignored_equals = b"-a\nname\n"
                self.assertEqual(self.output(binary, "-Iname"), ignored_name)
                self.assertEqual(self.output(binary, "-I", "name"), ignored_name)
                self.assertEqual(self.output(binary, "-I=name"),
                                 ignored_name if release.startswith("uutils") else ignored_equals)
                self.assertEqual(self.output(binary, "--ignore==name"), ignored_equals)
                self.assertEqual(self.output(binary, "--", "-a"), b"-a\n")

    def test_unavailable_creation_time_on_private_pipe(self):
        """A pipefs inode has an mtime but no creation timestamp on these Linux packages."""
        read_fd, write_fd = os.pipe()
        self.addCleanup(os.close, read_fd)
        self.addCleanup(os.close, write_fd)
        self.assertGreater(os.fstat(read_fd).st_mtime, 0)
        operand = "/proc/self/fd/" + str(read_fd)
        for binary, release in self.releases.items():
            with self.subTest(binary=binary):
                result = subprocess.run([binary, "-ldL", "--time=birth", "--time-style=+%s", operand],
                                        cwd=self.tree, env=ENV, pass_fds=(read_fd,), capture_output=True, timeout=10)
                self.assertEqual((result.returncode, result.stderr), (0, b""))
                self.assertEqual(result.stdout.split()[-2], b"???" if release.startswith("uutils") else b"?")
