"""Check fzf's native argument parser, terminal behavior and exact output bytes."""

from contextlib import contextmanager
import os
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile
import time
import unittest


@unittest.skipUnless(sys.platform.startswith("linux"), "Linux fzf fixtures")
class PackagedFzfTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Use an installed Ubuntu binary or an explicitly supplied release fixture."""
        cls.binary = Path(os.environ.get("FZF_TEST_BINARY", "/usr/bin/fzf")).resolve()
        if "FZF_TEST_BINARY" not in os.environ and not cls.binary.is_file():
            raise unittest.SkipTest("Ubuntu fzf fixture unavailable")
        banner = subprocess.check_output([cls.binary, "--version"], timeout=5).split()
        cls.release = banner[0].decode()
        if cls.release not in {"0.44.1", "0.67.0", "0.75.0"}:
            if "FZF_TEST_BINARY" in os.environ:
                raise ValueError(f"Unexpected fzf fixture {banner!r}")
            raise unittest.SkipTest(f"No release-specific expectations for {banner!r}")

    def setUp(self):
        private = tempfile.TemporaryDirectory(prefix="fzf-check-")
        self.addCleanup(private.cleanup)
        self.home = Path(private.name)
        self.env = {"HOME": private.name, "PATH": "/usr/bin:/bin", "LC_ALL": "C.UTF-8",
                    "SHELL": "/bin/sh", "TERM": "xterm-256color", "FZF_DEFAULT_OPTS": ""}

    def filtered(self, items, *options, query="", status=0, sorted_results=False):
        """Feed fixed records and return exact stdout after checking exit status."""
        args = [self.binary, "--filter", query, *options]
        if not sorted_results:
            args.append("--no-sort")
        result = subprocess.run(args, input=items, cwd=self.home, env=self.env,
                                capture_output=True, timeout=10)
        self.assertEqual(result.returncode, status, (options, result.stderr))
        return result.stdout

    @contextmanager
    def finder(self, data, *options):
        """Run one finder under a private tmux server, redirecting stdout away from its TTY."""
        with tempfile.TemporaryDirectory(dir=self.home) as name:
            case = Path(name)
            (case / "input").write_bytes(data)
            tmux = ["tmux", "-S", str(case / "socket"), "-f", "/dev/null"]

            def tm(*args, check=True):
                return subprocess.run([*tmux, *args], capture_output=True, text=True, timeout=8,
                                      env=self.env, cwd=case, check=check).stdout

            command = shlex.join([str(self.binary), "--layout=reverse", "--no-sort", "--no-mouse",
                                  "--prompt=Fixture> ", *options])
            # The shell waits on its own terminal after recording status so the
            # server retains the pane until the test has sampled the final state.
            script = f"{command} < input > output; printf '%s' \"$?\" > status; read -r finish"
            try:
                tm("new-session", "-d", "-s", "fzf", "-c", str(case), "-x", "100", "-y", "30",
                   "/bin/sh", "-c", script)
                yield tm, case
            finally:
                tm("kill-server", check=False)

    def wait_for(self, tm, predicate):
        """Poll rendered cells with a deadline and retain the last frame for diagnostics."""
        deadline = time.monotonic() + 8
        while time.monotonic() < deadline:
            cells = tm("capture-pane", "-p")
            if predicate(cells):
                return cells
            time.sleep(0.025)
        self.fail(f"Finder never reached expected state; last frame {cells!r}")

    def result(self, tm, case, expected_status):
        """Read output only after the finder has exited and the private shell recorded its status."""
        status = case / "status"
        self.wait_for(tm, lambda _: status.exists() and status.read_text() != "")
        self.assertEqual(status.read_text(), str(expected_status))
        return (case / "output").read_bytes()

    def test_matching_delimiters_and_record_bytes(self):
        data = b"cat\nscatter\ncXaXt\ndog\n"
        self.assertEqual(self.filtered(data, query="cat"), b"cat\nscatter\ncXaXt\n")
        self.assertEqual(self.filtered(data, "-e", query="cat"), b"cat\nscatter\n")
        self.assertEqual(self.filtered(data, "--exact", query="^cat$"), b"cat\n")
        self.assertEqual(self.filtered(data, query="absent", status=1), b"")
        items = b"a.ok\na.no\n"
        self.assertEqual(self.filtered(items, "-d[.]", "-n2", query="ok"), b"a.ok\n")
        noble = self.release == "0.44.1"
        self.assertEqual(self.filtered(items, "-d.", "-n2", query="ok", status=1 if noble else 0),
                         b"" if noble else b"a.ok\n")
        records = b"cat\nname\0dog\0"
        self.assertEqual(self.filtered(records, "--read0", query="cat"), b"cat\nname\n")
        self.assertEqual(self.filtered(records, "--read0", "--print0", query="cat"), b"cat\nname\0")
        self.assertEqual(self.filtered(data, "--print0", query="^cat$"), b"cat\0")

    def test_case_inverses_and_short_argument_boundaries(self):
        data = b"lowercase\n"
        self.assertEqual(self.filtered(data, "+i", query="LOWER", status=1), b"")
        self.assertEqual(self.filtered(data, "-i", query="LOWER"), data)
        noble = self.release == "0.44.1"
        self.assertEqual(self.filtered(data, "--ignore-case", query="LOWER", status=2 if noble else 0),
                         b"" if noble else data)
        self.assertEqual(self.filtered(data, "--no-ignore-case", query="LOWER",
                                       status=2 if noble else 1), b"")
        self.assertEqual(self.filtered(data, "--smart-case", query="LOWER",
                                       status=2 if noble else 1), b"")
        for invalid in (["-m=2"], ["--multi", "-2"]):
            self.assertEqual(self.filtered(data, *invalid, status=2), b"")

    def test_filter_output_across_sort_and_projection_modes(self):
        """Exercise streaming and sorted filter paths separately from terminal acceptance."""
        items = b"ID7:apple:red\nID8:pear:apple\n"
        fields = ["-d:", "--with-nth", "2..", "--nth", "1"]
        for sorted_results in (False, True):
            with self.subTest(sorted_results=sorted_results):
                original = b"ID7:apple:red\n"
                expected = original if sorted_results or self.release == "0.75.0" else b"apple:red\n"
                self.assertEqual(self.filtered(items, *fields, query="apple", sorted_results=sorted_results),
                                 expected)
                if self.release != "0.44.1":
                    output = b"ID7\n" if self.release == "0.75.0" else expected
                    self.assertEqual(self.filtered(items, *fields, "--accept-nth=1", query="apple",
                                                   sorted_results=sorted_results), output)

    def test_height_and_release_parser(self):
        for height in ("10", "45.5%", "~40%", "-2", "~-2"):
            rejected = ((height == "-2" and self.release == "0.44.1")
                        or (height == "~-2" and self.release != "0.75.0"))
            with self.subTest(height=height):
                self.assertEqual(self.filtered(b"row\n", f"--height={height}",
                                               status=2 if rejected else 0),
                                 b"" if rejected else b"row\n")

    def test_field_projection_search_and_acceptance(self):
        data = b"ID7:apple:red\nID8:pear:apple\n"
        opts = ["--delimiter", ":", "--with-nth", "2..", "--nth", "1", "--query", "apple"]

        def accept(*extra):
            with self.finder(data, *opts, *extra) as (tm, case):
                cells = self.wait_for(tm, lambda s: "apple:red" in s and "1/2" in s)
                self.assertNotIn("ID7", cells)
                self.assertNotIn("pear:apple", cells)
                tm("send-keys", "Enter")
                return self.result(tm, case, 0)

        self.assertEqual(accept(), b"ID7:apple:red\n")
        if self.release == "0.44.1":
            self.assertEqual(self.filtered(data, "--accept-nth=1", status=2), b"")
        else:
            self.assertEqual(accept("--accept-nth=1"), b"ID7\n")
            self.assertEqual(accept("--accept-nth", "{n}={3}/{1}"), b"0=red/ID7\n")

    def test_initial_query_zero_one_and_many(self):
        data = b"red-one\nred-two\n"
        for flag in ("-1", "--select-1", "-0", "--exit-0"):
            select_one = flag in {"-1", "--select-1"}
            for query, count in (("absent", 0), ("one", 1), ("red", 2)):
                automatic = count == (1 if select_one else 0)
                with self.subTest(flag=flag, query=query), self.finder(data, flag, "-q", query) as (tm, case):
                    if not automatic:
                        self.wait_for(tm, lambda s: f"{count}/2" in s and f"Fixture> {query}" in s)
                        tm("send-keys", "Enter" if count else "Escape")
                    status = (1 if automatic else 130) if count == 0 else 0
                    self.assertEqual(self.result(tm, case, status), b"red-one\n" if count else b"")

    def test_multiselect_optional_counts(self):
        """Two marking keys expose a one-item cap independently of filter-mode parsing."""
        two = b"one\ntwo\n"
        for spelling in ("--multi", "-m"):
            joined = "--multi=" if spelling == "--multi" else "-m"
            for args, expected in [
                    ([spelling], two), ([joined + "2"], two), ([spelling, "2"], two),
                    ([joined + "1"], b"one\n"), ([spelling, "1"], b"one\n"),
                    ([joined + "0"], b"one\n"), ([spelling, "0"], b"one\n"),
                    ([joined + "-1"], b"one\n"), ([joined + "+2"], two),
                    ([spelling, "-1"], two), ([spelling, "+1"], two)]:
                with self.subTest(args=args), self.finder(two, *args) as (tm, case):
                    self.wait_for(tm, lambda s: "2/2" in s and "two" in s)
                    tm("send-keys", "Tab", "Tab", "Enter")
                    self.assertEqual(self.result(tm, case, 0), expected)

    def test_preview_reload_and_accept_binding(self):
        """Record which item or event triggered each supplied command inside the private home."""
        helper = self.home / "record"
        helper.write_text(
            "#!/bin/sh\n"
            "printf '%s|%s\\n' \"$1\" \"$2\" >> \"$HOME/events\"\n"
            "case $1 in\n"
            "  preview) printf 'Preview-%s\\n' \"$2\" ;;\n"
            "  reload) printf 'Input title\\nnew:red\\n' ;;\n"
            "esac\n")
        helper.chmod(0o700)
        call = shlex.quote(str(helper))
        options = ["--delimiter", ":", "--header", "Fixed title", "--header-lines", "1",
                   "--preview", call + " preview {1}", "--preview-window", "right:40%",
                   "--bind", "ctrl-j:down,ctrl-r:reload(" + call + " reload),ctrl-y:execute-silent("
                   + call + " accept {1})+accept"]
        with self.finder(b"Input title\none:red\ntwo:blue\n", *options) as (tm, case):
            cells = self.wait_for(tm, lambda s: "Preview-one" in s and "2/2" in s)
            self.assertIn("Fixed title", cells)
            self.assertIn("Input title", cells)
            tm("send-keys", "C-j")
            self.wait_for(tm, lambda s: "Preview-two" in s)
            tm("send-keys", "C-r")
            self.wait_for(tm, lambda s: "Preview-new" in s)
            tm("send-keys", "C-y")
            self.assertEqual(self.result(tm, case, 0), b"new:red\n")
        events = (self.home / "events").read_text().splitlines()
        for event in ("preview|one", "preview|two", "reload|", "preview|new", "accept|new"):
            self.assertIn(event, events)
        self.assertEqual(events[-1], "accept|new")
