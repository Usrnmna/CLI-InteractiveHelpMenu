"""Exercise block-level merging and guided review without an external editor."""

from contextlib import redirect_stdout
import io
import itertools
import random
import shlex
import unittest
from unittest.mock import patch

import test_update_review
from test_bash_pty import BashSession
from test_discovery import ROOT
from guided_merge import GuidedMerge
import update_review as review


class GuidedMergeTests(unittest.TestCase):
    def test_all_decisions_preserve_exact_selected_input(self):
        examples = [(b"a\nb\nc\n", b"x\nb\ny\n"), (b"a\r\nb\r\n", b"a\r\nc\r\n"),
                    (b"no newline", b"new\n"), (None, b""), (b"", None),
                    (None, b"new\n"), (b"old\n", None), (b"", b""),
                    ("café\n日本\n".encode(), "café\n更新\n".encode())]
        for local, incoming in examples:
            for accept in (True, False):
                with self.subTest(local=local, incoming=incoming, accept=accept):
                    draft = GuidedMerge(local, incoming)
                    for index in range(len(draft.changes)):
                        draft.decide(index, accept)
                    self.assertEqual(draft.result(), incoming if accept else local)

    def test_replacement_insertion_deletion_and_mixed_choices(self):
        local = b"old\nanchor1\nremove\nanchor2\nend\n"
        incoming = b"new\nanchor1\nanchor2\ninsert\nend\n"
        draft = GuidedMerge(local, incoming)
        self.assertEqual([change[0] for change in draft.changes], ["replace", "delete", "insert"])
        for index, accept in enumerate((True, False, True)):
            draft.decide(index, accept)
        self.assertEqual(draft.result(), b"new\nanchor1\nremove\nanchor2\ninsert\nend\n")

    def test_preview_does_not_decide_undecided_blocks(self):
        draft = GuidedMerge(b"a\nkeep\nb", b"x\nkeep\ny")
        draft.decide(0, True)
        self.assertEqual(draft.result(False), b"x\nkeep\nb")
        with self.assertRaises(ValueError):
            draft.result()
        draft.decide(1, False)
        self.assertEqual(draft.result(), b"x\nkeep\nb")
        draft.decide(0, False)
        self.assertEqual(draft.result(), b"a\nkeep\nb")

    def test_invalid_decisions_are_refused(self):
        draft = GuidedMerge(b"a", b"b")
        for index, value in ((-1, True), (1, True), (True, True), (0, 1), (0, None)):
            with self.assertRaises(ValueError):
                draft.decide(index, value)

    def test_seeded_mixed_decisions_never_change_equal_lines(self):
        randomizer = random.Random(1011)
        for case in range(200):
            local = [f"old {case} {index}\n".encode() for index in range(4)]
            incoming = [f"new {case} {index}\n".encode() for index in range(4)]
            separators = [f"anchor {index}\n".encode() for index in range(4)]
            left = b"".join(itertools.chain.from_iterable(zip(local, separators)))
            right = b"".join(itertools.chain.from_iterable(zip(incoming, separators)))
            decisions = [randomizer.choice((True, False)) for _ in range(4)]
            draft = GuidedMerge(left, right)
            self.assertEqual(len(draft.changes), 4)
            for index, choice in enumerate(decisions):
                draft.decide(index, choice)
            expected = b"".join((incoming[index] if choice else local[index]) + separators[index]
                                for index, choice in enumerate(decisions))
            self.assertEqual(draft.result(), expected)


class GuidedReviewTests(unittest.TestCase):
    run_script = test_update_review.UpdateReviewTests.run_script
    upgrade = test_update_review.UpdateReviewTests.upgrade
    manifest = test_update_review.UpdateReviewTests.manifest
    backups = test_update_review.UpdateReviewTests.backups
    new_report = test_update_review.UpdateReviewTests.new_report
    session = test_update_review.UpdateReviewTests.session

    def setUp(self):
        test_update_review.UpdateReviewTests.setUp(self)
        (self.prefix / self.name).write_bytes((self.source / self.name).read_bytes())
        self.name = "cli_help/guided_fixture.py"
        self.local = b"# local first\n# stable\n# local last\n"
        self.incoming = b"# incoming first\n# stable\n# incoming last\n"
        (self.prefix / self.name).write_bytes(self.local)
        (self.source / self.name).write_bytes(self.incoming)
        self.new_report()

    def guided(self, session, commands):
        output = io.StringIO()
        with patch("builtins.input", side_effect=commands), redirect_stdout(output), \
                patch.object(review.subprocess, "run", side_effect=AssertionError("Editor must not run")):
            review.guided_edit(session, self.name)
        return output.getvalue()

    def test_accept_reject_preview_and_save_with_backup(self):
        session = self.session()
        output = self.guided(session, ["a", "r", "v", "d"])
        expected = b"# incoming first\n# stable\n# local last\n"
        self.assertIn("Guided result queued", output)
        self.assertEqual(session.choices[self.name], ("edit", expected))
        self.assertEqual((self.prefix / self.name).read_bytes(), self.local)
        backup = session.save()
        self.assertEqual((backup / "previous" / self.name).read_bytes(), self.local)
        self.assertEqual((self.prefix / self.name).read_bytes(), expected)
        self.run_script(self.prefix / "uninstall.sh")
        self.assertEqual((self.prefix / self.name).read_bytes(), expected)

    def test_back_retains_decisions_and_all_accept_adopts_incoming(self):
        session = self.session()
        self.guided(session, ["a", "b"])
        self.assertNotIn(self.name, session.choices)
        self.guided(session, ["n", "a", "p", "r", "p", "a", "d"])
        self.assertEqual(session.choices[self.name], ("incoming", self.incoming))
        session.save()
        self.run_script(self.prefix / "uninstall.sh")
        self.assertFalse(self.prefix.exists())

    def test_undecided_blocks_and_cancel_do_not_replace_prior_choice(self):
        session = self.session()
        session.choose(self.name, "local")
        output = self.guided(session, ["d", "n", "p", "unknown", "b"])
        self.assertIn("Accept or reject every change", output)
        self.assertEqual(session.choices[self.name], ("local", None))
        self.assertEqual((self.prefix / self.name).read_bytes(), self.local)

    def test_invalid_mixed_python_returns_to_guided_mode(self):
        (self.prefix / self.name).write_bytes(b"items = [\n# stable\n]\n")
        (self.source / self.name).write_bytes(b"items = {\n# stable\n}\n")
        self.new_report()
        session = self.session()
        output = self.guided(session, ["a", "r", "d", "a", "d"])
        self.assertIn("does not match", output)
        self.assertEqual(session.choices[self.name][0], "incoming")

    def test_deleted_file_and_empty_file_are_distinct_choices(self):
        session = self.session()
        session.choose(self.name, "incoming")
        session.save()
        (self.prefix / self.name).unlink()
        (self.source / self.name).write_bytes(b"")
        self.new_report()
        session = self.session()
        self.guided(session, ["a", "d"])
        self.assertEqual(session.choices[self.name], ("incoming", b""))
        session.save()
        self.assertEqual((self.prefix / self.name).read_bytes(), b"")

    def test_changed_comparison_refuses_existing_guided_draft(self):
        session = self.session()
        self.guided(session, ["a", "b"])
        (self.prefix / self.name).write_bytes(self.local + b"# external edit\n")
        with self.assertRaisesRegex(ValueError, "Comparison files changed"):
            self.guided(session, ["d"])

    def test_real_terminal_guided_changes_save_and_pending_command_is_unexecuted(self):
        folder = self.home / "guided-terminal"
        folder.mkdir()
        shell = BashSession(folder, extra_environment={"PYTHONDONTWRITEBYTECODE": "1", "EDITOR": "/missing-editor"})
        try:
            shell.send("bash " + shlex.quote(str(ROOT / "review-update.sh")) + " " + shlex.quote(str(self.report)) + "\n")
            shell.expect(b"Review >")
            shell.send("1\n")
            shell.expect(b"Choice >")
            shell.send("g\n")
            shell.expect(b"Guided >")
            shell.send("a\n")
            shell.expect(b"Guided change 2/2")
            shell.expect(b"Guided >")
            shell.send("r\n")
            shell.expect(b"Guided >")
            shell.send("d\n")
            shell.expect(b"Guided result queued")
            shell.expect(b"Choice >")
            shell.send("b\n")
            shell.expect(b"Review >")
            shell.send("s\n")
            shell.expect(b"Apply queued choices with backups?")
            shell.send("y\n")
            shell.expect(b"Choices saved.")
            shell.expect(b"Review >")
            shell.send("q\n")
            shell.expect(b"__HELP_TEST_PROMPT__")
            self.assertEqual((self.prefix / self.name).read_bytes(), b"# incoming first\n# stable\n# local last\n")
            shell.send("cli_help_unbind; source " + shlex.quote(str(self.prefix / "bash/interactive-help.bash")) + "\n")
            shell.expect(b"__HELP_TEST_PROMPT__")
            shell.open("rsync --ar")
            shell.finish("\n")
            self.assertEqual(shell.read_buffer(), ("rsync --archive ", 16))
            self.assertFalse(shell.executed.exists())
        finally:
            shell.close()


if __name__ == "__main__":
    unittest.main()
