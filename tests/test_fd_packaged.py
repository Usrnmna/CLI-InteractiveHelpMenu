"""Measure release differences with real fd binaries and disposable files."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


@unittest.skipUnless(sys.platform.startswith("linux"), "Linux fd fixtures")
class PackagedFdTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Select the Ubuntu client or an explicitly supplied release comparator."""
        cls.binary = Path(os.environ.get("FD_TEST_BINARY", "/usr/bin/fdfind"))
        if "FD_TEST_BINARY" not in os.environ and not cls.binary.exists():
            raise unittest.SkipTest("Ubuntu fdfind fixture unavailable")
        banner = subprocess.check_output([cls.binary, "--version"], timeout=5).strip()
        if banner not in {b"fdfind 9.0.0", b"fdfind 10.3.0", b"fd 10.5.2"}:
            if "FD_TEST_BINARY" in os.environ:
                raise ValueError(f"Unexpected fd fixture {banner!r}")
            raise unittest.SkipTest(f"No release-specific expectations for {banner!r}")
        cls.noble = banner == b"fdfind 9.0.0"
        cls.upstream = banner == b"fd 10.5.2"

    def setUp(self):
        private = tempfile.TemporaryDirectory(prefix="cli-help-fd-")
        self.addCleanup(private.cleanup)
        self.tree = Path(private.name) / "tree"
        self.tree.mkdir()
        self.env = {"HOME": private.name, "LC_ALL": "C", "TZ": "UTC", "PATH": "/usr/bin:/bin"}

    def invoke(self, *args, status=0):
        """Return raw stdout and diagnose unexpected status without a shell."""
        result = subprocess.run([self.binary, *args], cwd=self.tree, env=self.env,
                                stdin=subprocess.DEVNULL, capture_output=True, timeout=10)
        self.assertEqual(result.returncode, status, (args, result.stderr))
        if status == 0:
            self.assertEqual(result.stderr, b"", args)
        return result.stdout

    def test_unrestricted_repetition_and_inverses(self):
        subprocess.run(["git", "init", "-q"], cwd=self.tree, env=self.env, check=True)
        for name in ("ignored", ".dot"):
            (self.tree / name).touch()
        (self.tree / ".fdignore").write_text("ignored\n")
        probes = {b".git/HEAD", b"ignored", b".dot"}

        def selected(*options):
            return probes.intersection(self.invoke(*options).splitlines())

        self.assertEqual(selected("-H"), {b".dot"} if self.noble else {b".dot", b".git/HEAD"})
        for count in ("-u", "-uu", "-uuu"):
            self.assertEqual(selected(count), probes)
        self.assertEqual(selected("-u", "--exclude", ".git"), {b"ignored", b".dot"})
        self.assertEqual(selected("-u", "--ignore"), probes - {b"ignored"} if self.upstream else set())
        self.assertEqual(selected("-u", "--no-hidden"), {b"ignored"} if self.upstream else set())

    def test_size_time_and_limit_boundaries(self):
        for name, size in (("decimal", 1000), ("binary", 1024)):
            path = self.tree / name
            path.write_bytes(b"x" * size)
            os.utime(path, (1704067200, 1704067200))
        self.assertEqual(self.invoke("-S+1k", "-S-1k"), b"decimal\n")
        self.assertEqual(self.invoke("-S1KiB"), b"binary\n")
        self.invoke("-S1000", status=2)
        for flag in ("--older", "--newer"):
            self.assertEqual(self.invoke(flag, "@1704067200", status=1 if self.noble else 0), b"")
            self.assertEqual(self.invoke(flag, "2024-01-01"), b"")
        self.assertEqual(set(self.invoke("--max-results=0").splitlines()), {b"decimal", b"binary"})
        self.assertEqual(len(self.invoke("-1").splitlines()), 1)
        self.assertEqual(self.invoke("--has-results", "absent", status=1), b"")
        self.assertEqual(self.invoke("-q", "decimal"), b"")
        self.assertEqual(self.invoke("absent"), b"")

    def test_matching_formatting_and_output_bytes(self):
        for name in ("r.dot", "r.dot.bak", "line\nbreak"):
            (self.tree / name).touch()
        self.assertEqual(set(self.invoke("-F", "r.dot").splitlines()), {b"r.dot", b"r.dot.bak"})
        self.assertEqual(self.invoke("-g", "r.dot"), b"r.dot\n")
        self.assertEqual(self.invoke("--exact", "r.dot", status=0 if self.upstream else 2),
                         b"r.dot\n" if self.upstream else b"")
        self.assertEqual(self.invoke("-0", "line"), b"./line\nbreak\0")
        self.assertEqual(self.invoke("--strip-cwd-prefix", "-0", "line"), b"line\nbreak\0")
        if self.noble:
            self.invoke("--strip-cwd-prefix=never", status=2)
            self.invoke("--format", "{/.}", "line", status=2)
        else:
            self.assertEqual(self.invoke("--strip-cwd-prefix=never", "line"), b"./line\nbreak\n")
            self.assertEqual(self.invoke("--format", "entry={/.}", "-g", "r.dot"), b"entry=r\n")

    def test_exec_vectors_and_parent_filter_after_child(self):
        """Use JSON argv records so spaces, delimiters and option ownership are observable."""
        paths = {"./a.txt", "./b file.txt"}
        for name in paths:
            (self.tree / name).touch()
        recorder = self.tree.parent / "args.py"
        recorder.write_text("import json, sys\nprint(json.dumps(sys.argv[1:]))\n")
        child = [sys.executable, str(recorder)]

        def records(*args):
            return [json.loads(line) for line in self.invoke(*args).splitlines()]

        per_match = records("-x", *child, "--size", ";", "-S0b")
        self.assertCountEqual(per_match, [["--size", path] for path in paths])
        self.assertEqual(records("-x", *child, "--size", ";", "-S1b"), [])
        batch, = records("-X", *child, "--child", "{}")
        self.assertEqual(batch[0], "--child")
        self.assertCountEqual(batch[1:], paths)
        self.assertCountEqual(records("--batch-size", "1", "-X", *child), [[path] for path in paths])
        expanded, = records("-X", *child, "{/.}~{/}")
        self.assertCountEqual(expanded, ["a~a.txt", "b file~b file.txt"])
        self.invoke("-X", *child, "{}", "{/}", status=2)
        self.assertEqual(records("absent", "-X", *child), [])
        self.invoke("-x", *child, ";", "-X", *child, status=2)
