"""Prove the base comparison reads the archive and the local pilot fails closed."""

import io
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import impacted_suite
import run_sandbox


class SnapshotDeltaTests(unittest.TestCase):
    def test_archived_bytes_modes_and_both_sides_of_moves(self):
        """Use independent index, working tree and archive contents in a private Git repository."""
        with tempfile.TemporaryDirectory() as folder, patch.object(run_sandbox, "ROOT", Path(folder)):
            root = Path(folder)

            def git(*args):
                return subprocess.check_output(["git", *args], cwd=root).decode().strip()

            git("init", "--quiet")
            for name in ("tracked", "unchanged", "mode", "staged", "removed", "old"):
                (root / name).write_text("base")
            git("add", ".")
            base = git("write-tree")
            git("mv", "old", "new")
            (root / "removed").unlink()
            (root / "mode").chmod(0o755)
            for name in ("staged", "tracked", "unchanged"):
                (root / name).write_text("staged")
                git("add", name)
            (root / "tracked").write_text("working-tree")
            (root / "unchanged").write_text("base")
            includes = {Path("extra space\nfile")}
            for name in [*includes, "unresolved"]:
                (root / name).write_text("new")
            archive = io.BytesIO()
            run_sandbox.snapshot(archive, includes)
            (root / "tracked").write_text("base")
            before = run_sandbox.snapshot_delta(archive, base, includes)
            self.assertEqual(before["changes"], {
                "tracked": "modified", "staged": "modified", "mode": "modified", "removed": "deleted",
                "old": "deleted", "new": "added", "extra space\nfile": "added"})
            self.assertEqual(before["unresolved"], ["unresolved"])
            self.assertEqual(archive.tell(), 0)
            self.assertEqual(before, run_sandbox.snapshot_delta(archive, base, includes))
            after = io.BytesIO()
            run_sandbox.snapshot(after, includes)
            replaced = run_sandbox.snapshot_delta(after, base, includes)
            self.assertNotIn("tracked", replaced["changes"])
            self.assertNotEqual(before["snapshot"], replaced["snapshot"])


class ImpactPlanTests(unittest.TestCase):
    """Exercise discovery resolution with a shifted index and an overlapping shared test."""

    def setUp(self):
        class Cases(unittest.TestCase):
            def test_path_998_example(self):
                raise AssertionError("explain ran the route")

            @unittest.skip("optional fixture")
            def test_shared(self):
                raise AssertionError("explain ran a case")

            def test_unrelated(self):
                raise AssertionError("explain ran a case")

        Cases.test_path_998_example.command_path = "pilot"
        self.cases = list(unittest.TestLoader().loadTestsFromTestCase(Cases))
        self.route, self.shared, self.unrelated = [case.id() for case in self.cases]
        self.path = "tests/test-impact.json"
        self.group = dict(inputs=[self.path], tests=[self.shared], routes=["pilot"], fixtures=[])
        self.config = dict(shared_tests=[self.shared], shared_fixtures=[], families={"pilot": self.group})
        self.delta = dict(changes={self.path: "modified"}, unresolved=[])

    def plan(self):
        """Resolve the synthetic group without requiring real terminal tools."""
        with patch.object(impacted_suite.shutil, "which", return_value="/test/bin/tmux"):
            return impacted_suite.selection(self.delta, self.config, self.cases, "host")

    def test_report_only_resolves_by_command_and_unions_in_discovery_order(self):
        plan = self.plan()
        self.assertEqual(plan["suite"], "selected")
        self.assertEqual(list(plan["tests"]), [self.route, self.shared])
        self.assertEqual(plan["tests"][self.shared], ["pilot: " + self.path])
        self.assertEqual(plan["expected_skips"], {self.shared: "optional fixture"})

    def test_missing_test_route_empty_group_or_fixture_requires_full(self):
        for field, value in (("tests", ["disappeared"]), ("tests", []), ("routes", ["gone"]),
                             ("fixtures", ["absent-pilot-fixture"])):
            with self.subTest(field=field, value=value), patch.dict(self.group, {field: value}):
                plan = self.plan()
                self.assertEqual(plan["suite"], "full")
                self.assertEqual(list(plan["tests"]), [case.id() for case in self.cases])
                self.assertTrue(plan["fallback"])
                if field == "fixtures":
                    self.assertEqual(plan["missing"], value)

    def test_markdown_requires_offline_checker_and_public_roots(self):
        self.delta["changes"] = {"docs/audit.md": "modified"}
        with patch.object(impacted_suite, "link_roots", return_value={}):
            plan = self.plan()
        self.assertIn(impacted_suite.LINK_GATE, plan["gates"])
        self.assertIn(impacted_suite.LYCHEE_CA, plan["missing"])
        with patch.object(impacted_suite, "link_roots", return_value={"SSL_CERT_FILE": "/public.pem"}):
            plan = self.plan()
        self.assertTrue(plan["fixtures"]["/public.pem"])
        self.assertFalse(plan["missing"])

    def test_unresolved_shared_deleted_unmapped_and_no_changes_fall_back(self):
        for changes, unresolved in (({}, []), ({self.path: "deleted"}, []),
                                    ({"cli_help/presentation.py": "modified"}, []),
                                    ({self.path: "modified"}, ["new-untracked"])):
            with self.subTest(changes=changes, unresolved=unresolved):
                self.delta.update(changes=changes, unresolved=unresolved)
                self.assertEqual(self.plan()["suite"], "full")


class ExecutionTests(unittest.TestCase):
    """Exercise both runner paths using real fixture callbacks and observable outcomes."""

    def test_report_matches_selected_execution_and_full_fallback(self):
        import json
        import shutil
        import sys

        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for directory in ("bash", "tests", "scripts", "cli_help"):
                (root / directory).mkdir()
            for path in ("tests/run.sh", "tests/impacted_suite.py", "tests/timed_unittest.py"):
                shutil.copy2(run_sandbox.ROOT / path, root / path)
            for script in ("bash/interactive-help.bash", "install.sh", "uninstall.sh",
                           "update.sh", "review-update.sh", "update-from-github.sh"):
                (root / script).touch()
            (root / "scripts/check_numerical_coverage.py").touch()
            (root / "cli_help/main.py").touch()
            source = root / "tests/test_fixture.py"
            source.write_text("""
from pathlib import Path
import unittest

class Cases(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with Path("fixtures").open("a") as stream:
            stream.write("setup\\n")

    def test_pass(self):
        self.assertTrue(Path("fixtures").is_file())

    @unittest.skip("recorded reason")
    def test_skip(self):
        self.fail()

    def test_unrelated(self):
        self.fail("fallback reached unrelated case")

Cases.test_pass.command_path = "pilot"
""")
            base = "test_fixture.Cases."
            selected = [base + "test_pass", base + "test_skip"]
            spec = dict(inputs=["tests/test_fixture.py"], tests=selected, routes=["pilot"], fixtures=[])
            (root / "tests/test-impact.json").write_text(json.dumps(dict(
                families={"example": spec}, shared_tests=[selected[0]], shared_fixtures=[])))
            env = dict(os.environ, CLI_HELP_TEST_TIMING="0", PYTHONDONTWRITEBYTECODE="1")
            # The synthetic pilot uses the same tmux prerequisite as the real families.
            (root / "tmux").touch(mode=0o755)
            env["PATH"] = str(root) + os.pathsep + env["PATH"]

            def run(mode, changed):
                delta = json.dumps(dict(changes={changed: "modified"}, unresolved=[]))
                return subprocess.run([sys.executable, "-I", "tests/impacted_suite.py", delta, "host", mode],
                                      cwd=root, env=env, capture_output=True, text=True, timeout=45)

            explain = run("explain", "tests/test_fixture.py")
            self.assertEqual(explain.returncode, 0, explain.stderr)
            self.assertEqual(list(json.loads(explain.stdout)["tests"]), selected)
            self.assertFalse((root / "fixtures").exists())
            execute = run("execute", "tests/test_fixture.py")
            self.assertEqual(execute.returncode, 0, execute.stderr)
            plan, _ = json.JSONDecoder().raw_decode(execute.stdout)
            self.assertEqual(plan, json.loads(explain.stdout))
            self.assertEqual((root / "fixtures").read_text(), "setup\n")
            self.assertIn("Ran 2 tests", execute.stderr)
            self.assertIn("skipped 'recorded reason'", execute.stderr)
            self.assertNotIn("test_unrelated", execute.stderr)
            full = run("execute", "unmapped")
            self.assertEqual(full.returncode, 1, full.stderr)
            self.assertIn("Ran 3 tests", full.stderr)
            self.assertIn("fallback reached unrelated case", full.stderr)
            self.assertEqual((root / "fixtures").read_text(), "setup\nsetup\n")

            (root / "scripts/check_numerical_coverage.py").write_text("raise SystemExit(37)")
            preflight = run("execute", "tests/test_fixture.py")
            self.assertEqual(preflight.returncode, 37)
            self.assertEqual((root / "fixtures").read_text(), "setup\nsetup\n")
