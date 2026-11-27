"""Cover deterministic CI assignments and the manual pilot's evidence gate."""

from contextlib import redirect_stderr, redirect_stdout
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import ci_shards


TARGET = f"{sys.version_info.major}.{sys.version_info.minor}"
COMMIT = "a" * 40


class AssignmentTests(unittest.TestCase):
    def test_balance_by_target_and_keep_modules_in_discovery_order(self):
        ids = ["a.C.first", "a.C.second", "b.C.first", "c.C.first", "d.C.first"]
        weights = {"a": 30, "b": 90, "c": 60, "removed": 45}
        groups, loads, unknown = ci_shards.partition(ids, weights)
        self.assertEqual(groups, [["d.C.first"], ["b.C.first"], ["a.C.first", "a.C.second", "c.C.first"]])
        self.assertEqual(loads, [97.5, 90, 90])
        self.assertEqual(unknown, ["d"])
        self.assertEqual(ci_shards.partition(ids, dict(reversed(list(weights.items()))))[0], groups)
        self.assertNotEqual(ci_shards.partition(ids, {**weights, "a": 120})[0], groups)

    def test_new_small_modules_get_nonempty_shards_and_duplicates_fail(self):
        ids = ["a.C.m", "b.C.m", "c.C.m"]
        groups, _, _ = ci_shards.partition(ids, {"old": 0.1})
        self.assertEqual(sorted(sum(groups, [])), ids)
        self.assertTrue(all(groups))
        with self.assertRaisesRegex(ValueError, "unique"):
            ci_shards.partition(ids + ids[:1], {"old": 1})


class PilotEvidenceTests(unittest.TestCase):
    """Exercise actual planning, shell preflight, selected execution and control discovery once."""

    @classmethod
    def setUpClass(cls):
        temporary = tempfile.TemporaryDirectory()
        cls.addClassCleanup(temporary.cleanup)
        cls.root = Path(temporary.name)
        cls.shards = cls.root / "shards"
        cls.control = cls.root / "control"
        for folder in ("bash", "cli_help", "scripts", "tests"):
            (cls.root / folder).mkdir()
        for script in ("bash/interactive-help.bash", "install.sh", "uninstall.sh", "update.sh",
                       "review-update.sh", "update-from-github.sh"):
            (cls.root / script).write_text("true\n")
        for script in ("scripts/check_numerical_coverage.py", "cli_help/main.py"):
            (cls.root / script).write_text("pass\n")
        for script in ("run.sh", "timed_unittest.py", "ci_shards.py"):
            shutil.copy(ci_shards.TESTS / script, cls.root / "tests")
        (cls.root / "tests/ci-module-seconds.json").write_text(json.dumps({TARGET: {"test_a": 20}}))
        cases = {
            "test_a": "    def test_pass(self): pass",
            "test_b": "    def test_skip(self): self.skipTest('unavailable')",
            "test_c": ("    @classmethod\n    def setUpClass(cls): raise unittest.SkipTest('fixture absent')\n"
                       "    def test_unreachable(self): self.fail()"),
        }
        for module, body in cases.items():
            (cls.root / f"tests/{module}.py").write_text("import unittest\nclass Cases(unittest.TestCase):\n" + body + "\n")
        env = dict(os.environ, CLI_HELP_TEST_TIMING="1", PYTHONDONTWRITEBYTECODE="1")
        env.pop("CLI_HELP_TEST_TIMING_STREAM", None)
        for shard in (0, *ci_shards.SHARDS):
            base = cls.shards if shard else cls.control
            suffix = f"-shard-{shard}" if shard else ""
            folder = base / f"linux-tests-python-{TARGET}{suffix}"
            subprocess.run([sys.executable, "tests/ci_shards.py", "plan", str(folder), "--commit", COMMIT,
                            "--shard", str(shard)], cwd=cls.root, env=env, check=True, capture_output=True)
            args = ["--selected", *(folder / "selected.txt").read_text().splitlines()] if shard else []
            result = subprocess.run(["bash", "tests/run.sh", *args], cwd=cls.root, env=env,
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=60)
            if result.returncode:
                raise AssertionError(result.stdout)
            events = result.stdout.splitlines()[0].removeprefix("Test timing report: ")
            shutil.copyfile(events, folder / "events.jsonl")

    def verify(self, shards, control=None, commit=COMMIT):
        """Use the actual aggregate gate with the single interpreter in this fixture."""
        output = io.StringIO()
        with patch.object(ci_shards, "TARGETS", (TARGET,)), redirect_stdout(output), redirect_stderr(output):
            code = ci_shards.verify(shards, commit, control)
        return code, output.getvalue()

    def test_shard_control_parity_including_case_and_fixture_skips(self):
        code, summary = self.verify(self.shards, self.control)
        self.assertEqual(code, 0, summary)
        self.assertIn("3 IDs, 2 with skips", summary)

    def test_missing_artifact_wrong_commit_or_skip_reason_fails(self):
        self.assertEqual(self.verify(self.root / "absent")[0], 1)
        self.assertEqual(self.verify(self.shards, commit="other")[0], 1)
        with tempfile.TemporaryDirectory() as temporary:
            control = Path(temporary) / "control"
            shutil.copytree(self.control, control)
            events, = control.glob("*/events.jsonl")
            events.write_text(events.read_text().replace("fixture absent", "different reason"))
            code, message = self.verify(self.shards, control)
            self.assertEqual(code, 1)
            self.assertIn("test_c.Cases.test_unreachable", message)

    def test_duplicate_assignments_and_truncated_execution_fail(self):
        for corruption, expected in (("duplicate", "repeated IDs"), ("truncated", "Incomplete timing stream"),
                                     ("lost-case", "Execution differs"), ("fixture-error", "Unresolved fixture")):
            with self.subTest(corruption=corruption), tempfile.TemporaryDirectory() as temporary:
                shards = Path(temporary) / "shards"
                shutil.copytree(self.shards, shards)
                first, second, _ = sorted(shards.iterdir())
                if corruption == "duplicate":
                    for name in ("manifest.json", "events.jsonl"):
                        shutil.copyfile(first / name, second / name)
                    path = second / "manifest.json"
                    manifest = json.loads(path.read_text())
                    manifest["shard"] = 2
                    path.write_text(json.dumps(manifest))
                elif corruption == "truncated":
                    (first / "events.jsonl").write_text("")
                else:
                    path = next(p for p in shards.glob("*/events.jsonl") if '"event": "fixture-outcome"' in p.read_text())
                    lines = path.read_text().splitlines()
                    if corruption == "lost-case":
                        lines = [line for line in lines if '"event": "fixture-outcome"' not in line]
                    else:
                        lines = [line.replace('"status": "skip"', '"status": "error"') for line in lines]
                    path.write_text("\n".join(lines))
                code, message = self.verify(shards)
                self.assertEqual(code, 1)
                self.assertIn(expected, message)
