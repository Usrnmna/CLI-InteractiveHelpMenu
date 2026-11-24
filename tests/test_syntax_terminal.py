"""Real Bash/tmux checks for rendered Details, literal edits, and terminal key handling."""

import copy
import json
import shlex
import time
import unittest

from test_terminal_screen import TerminalTestCase, TMUX_AVAILABLE, PROMPT, HISTORY, ROOT
from test_argument_syntax import PROFILE
from presentation import option_label, option_text
from ui import ellipsize_cells, wrap_cells


@unittest.skipUnless(TMUX_AVAILABLE, "Rendered-screen tests require Linux and tmux")
class SyntaxScreenTests(TerminalTestCase):
    def configure(self, shell, profile, delay=None):
        folder = shell.folder / "profiles"
        folder.mkdir()
        (folder / "fixture.json").write_text(json.dumps(profile))
        extra = " CLI_HELP_ESCAPE_DELAY=" + str(delay) if delay else ""
        shell.text("typed() { printf executed > " + shlex.quote(str(shell.executed)) + "; }; export CLI_HELP_PROFILES="
                   + shlex.quote(str(folder)) + extra)
        shell.keys("Enter")
        shell.wait_for(lambda value: value.cells[value.y] == PROMPT.rstrip())
        shell.text("printf 'HISTORY-%03d\\n' {1..80}")
        shell.keys("Enter")
        shell.wait_for(lambda value: value.history_markers() == HISTORY)

    def test_wide_labels_do_not_spill_into_the_next_row(self):
        shell = self.start()
        self.configure(shell, {"command": ["typed"], "description": "Mixed 界 cafe\u0301 text",
            "categories": [{"name": "界" * 20, "options": [
                {"flag": "--flag", "summary": "語" * 60, "detail": "界" * 90}]}]})
        shell.text("typed --fl")
        before = shell.wait_for(lambda value: value.x == len(PROMPT + "typed --fl"))
        menu = shell.open_menu()
        self.assertEqual(menu.cells[5].strip(), "")
        self.assertIn("OPTIONS *", menu.cells[3])
        self.assertIn("> --flag", menu.cells[4])
        self.assertEqual(shell.cancel(), before)
        self.assertEqual(shell.read_buffer(), ("typed --fl", len("typed --fl")))
        self.assertFalse(shell.executed.exists())

    def test_combining_buffer_cursor_resize_and_keyboard_selection(self):
        shell = self.start()
        self.configure(shell, {"command": ["typed"], "description": "Fixture",
            "categories": [{"name": "Options", "options": [{"flag": "--flag", "summary": "cafe\u0301 界"}]}]})
        line = "typed 'cafe\u0301界' --fl"
        shell.text(line)
        before = shell.wait_for(lambda value: value.x == len(PROMPT + line))
        shell.open_menu()
        self.assertEqual(shell.cancel("C-c"), before)
        shell.open_menu()
        shell.resize(40, 10)
        shell.resize(100, 24)
        shell.keys("Enter")
        expected = "typed 'cafe\u0301界' --flag "
        after = shell.wait_for(lambda value: value.alternate == 0 and value.x == len(PROMPT + expected))
        self.assertEqual(after.history_markers(), HISTORY)
        self.assertEqual(shell.read_buffer(), (expected, len(expected)))
        self.assertFalse(shell.executed.exists())

    def pending_stubbed_command(self, command, suffix, columns, rows, stub_names):
        """Place the cursor before the suffix and record any target or child execution."""
        shell = self.start()
        for name in stub_names:
            stub = shell.folder / name
            stub.write_text("#!/bin/sh\nprintf '%s\\n' \"$0\" >> " + shlex.quote(str(shell.executed)) + "\nexit 1\n")
            stub.chmod(0o700)
        shell.text("export PATH=" + shlex.quote(str(shell.folder)) + ':"$PATH"')
        shell.keys("Enter")
        shell.wait_for(lambda state: state.cells[state.y] == PROMPT.rstrip())
        shell.resize(columns, rows)
        prefix = command + " "
        shell.text(prefix + suffix)
        shell.keys(*(["Left"] * len(suffix)))
        return shell, prefix, suffix

    def pending_extraction(self, executable, columns, rows):
        """Open a stubbed extractor before quoted archive and member operands."""
        return self.pending_stubbed_command(executable + " x", " 'archive name.zip' '*.txt'",
                                           columns, rows, (executable,))

    def pending_finder(self, executable, columns, rows):
        """Open a stubbed finder before a quoted pattern and search directory."""
        return self.pending_stubbed_command(executable, " 'quoted pattern' 'search root'",
                                           columns, rows, ("fd", "fdfind", "fd-child"))

    def test_extraction_all_rows_and_complete_details(self):
        for executable in ("7z", "7zz"):
            profile = json.loads((ROOT / "profiles" / (executable + "-x.json")).read_text())
            shell, prefix, suffix = self.pending_extraction(executable, 220, 120)
            self.check_rendered_rows(profile, shell, prefix, suffix)

    def test_fd_all_rows_and_complete_details(self):
        for executable in ("fd", "fdfind"):
            profile = json.loads((ROOT / "profiles" / (executable + ".json")).read_text())
            shell, prefix, suffix = self.pending_finder(executable, 220, 120)
            self.check_rendered_rows(profile, shell, prefix, suffix)

    def test_fzf_all_rows_and_complete_details(self):
        """Compare every fzf selection with its complete formatted Details."""
        profile = json.loads((ROOT / "profiles/fzf.json").read_text())
        shell, prefix, suffix = self.pending_stubbed_command("fzf", " --query 'some text'", 220, 120, ("fzf",))
        self.check_rendered_rows(profile, shell, prefix, suffix)

    def test_yq_all_rows_and_complete_details(self):
        """Read every selectable spelling with the Mike Farah identity guard enabled."""
        shell, prefix, suffix, probes = self.pending_yq(220, 120)
        profile = json.loads((ROOT / "profiles/yq-eval.json").read_text())
        self.check_rendered_rows(profile, shell, prefix, suffix)
        self.assertIn("--version", probes.read_text().splitlines())

    def test_yq_rejects_kislyuk_in_bash(self):
        """A jq-wrapper identity must stop lookup before any leaf-help probe."""
        shell, prefix, suffix, probes = self.pending_yq(100, 24, version="kislyuk")
        shell.keys("Escape", "h")
        shell.wait_for(lambda state: state.alternate == 0 and "requires Mike Farah" in " ".join(state.cells))
        self.assertEqual(probes.read_text().splitlines(), ["--version"])
        self.assertEqual(shell.read_buffer(), (prefix + suffix, len(prefix)))
        self.assertFalse(shell.executed.exists())

    def test_yq_expression_file_before_two_inputs(self):
        """Read the file distinction at minimum size and insert a quoted query path."""
        shell, prefix, suffix, _ = self.pending_yq(60, 16)
        for action in ("Escape", "Enter"):
            self.assertEqual(shell.open_menu().cells[2].rstrip(), "Filter:")
            shell.keys("/")
            shell.text("read the query")
            shell.keys("Enter")
            found = shell.wait_for(lambda state: state.cells[2] == "Filter: read the query"
                                   and "> --from-file" in state.cells[4])
            self.reach_detail(shell, found, "following filenames supply input documents.")
            shell.cancel(action)
            if action == "Escape":
                self.assertEqual(shell.read_buffer(), (prefix + suffix, len(prefix)))
        self.assertEqual(shell.read_buffer(), (prefix + "--from-file" + suffix, len(prefix + "--from-file ")))
        operand = "'query file.yq'"
        shell.text(operand + " ")
        edited = prefix + "--from-file " + operand
        self.assertEqual(shell.read_buffer(), (edited + suffix, len(edited) + 1))
        self.assertFalse(shell.executed.exists())

    def test_ffmpeg_all_rows_and_complete_details(self):
        """Read every FFmpeg selection between an existing input and a quoted output."""
        profile = json.loads((ROOT / "profiles/ffmpeg.json").read_text())
        shell, prefix, suffix = self.pending_stubbed_command(
            "ffmpeg -i 'first clip.mkv'", " 'final cut.mkv'", 220, 120, ("ffmpeg",))
        self.check_rendered_rows(profile, shell, prefix, suffix)

    def test_ffmpeg_seek_before_second_input_at_minimum_size(self):
        """Reach the input placement rule and edit a pending command with two inputs."""
        shell, prefix, suffix = self.pending_stubbed_command(
            "ffmpeg -i one.mkv", " -i 'last clip.mkv' out.mkv", 60, 16, ("ffmpeg",))
        qualification = "Place it before the input it should seek."
        for action in ("Escape", "Enter"):
            self.assertEqual(shell.open_menu().cells[2].rstrip(), "Filter:")
            shell.keys("/")
            shell.text("end of file")
            shell.keys("Enter")
            found = shell.wait_for(lambda state: state.cells[2] == "Filter: end of file"
                                   and "> -sseof " in state.cells[4])
            self.assertNotIn(qualification, " ".join(" ".join(found.cells[8:-3]).split()))
            self.reach_detail(shell, found, qualification)
            shell.cancel(action)
            if action == "Escape":
                self.assertEqual(shell.read_buffer(), (prefix + suffix, len(prefix)))
        self.assertEqual(shell.read_buffer(), (prefix + "-sseof" + suffix, len(prefix + "-sseof ")))
        shell.text("-2 ")
        self.assertEqual(shell.read_buffer(), ("ffmpeg -i one.mkv -sseof -2 -i 'last clip.mkv' out.mkv",
                                               len(prefix + "-sseof -2 ")))
        self.assertFalse(shell.executed.exists())

    def test_fzf_output_fields_before_quoted_query_at_minimum_size(self):
        """Find the field-numbering rule and insert a projection before an existing option."""
        shell, prefix, suffix = self.pending_stubbed_command("fzf", " --query 'some text'", 60, 16, ("fzf",))
        qualification = "Count fields in the original input."
        for action in ("Escape", "Enter"):
            self.assertEqual(shell.open_menu().cells[2].rstrip(), "Filter:")
            shell.keys("/")
            shell.text("output fields")
            shell.keys("Enter")
            found = shell.wait_for(lambda state: state.cells[2] == "Filter: output fields"
                                   and "> --accept-nth " in state.cells[4])
            self.assertNotIn(qualification, " ".join(" ".join(found.cells[8:-3]).split()))
            self.reach_detail(shell, found, qualification)
            shell.cancel(action)
            if action == "Escape":
                self.assertEqual(shell.read_buffer(), (prefix + suffix, len(prefix)))
        self.assertEqual(shell.read_buffer(), (prefix + "--accept-nth" + suffix, len(prefix + "--accept-nth ")))
        shell.text("3 ")
        self.assertEqual(shell.read_buffer(), ("fzf --accept-nth 3 --query 'some text'", len("fzf --accept-nth 3 ")))
        self.assertFalse(shell.executed.exists())

    def check_rendered_rows(self, profile, shell, prefix, suffix):
        """Read each selected declaration, summary, and complete formatted Details from terminal cells."""
        title = " ".join(profile["command"])
        self.assertEqual(shell.open_menu().cells[0], "Interactive help | " + title)
        for category_index, category in enumerate(profile["categories"]):
            if category_index:
                shell.keys("Right")
            for index, option in enumerate(category["options"]):
                if index:
                    shell.keys("Down")
                with self.subTest(command=title, flag=option["flag"]):
                    label = ellipsize_cells(option_label(option), 40)
                    view = option_text(profile, category, option)
                    details = [line for paragraph in view.details for line in wrap_cells(paragraph, 218)]
                    shell.wait_for_option(label, option["summary"], details)
        shell.cancel()
        self.assertEqual(shell.read_buffer(), (prefix + suffix, len(prefix)))
        self.assertFalse(shell.executed.exists())

    def test_extraction_overwrite_and_attached_destination_at_minimum_size(self):
        """Find the collision policy and insert a destination before an archive operand."""
        for executable in ("7z", "7zz"):
            with self.subTest(executable=executable):
                shell, prefix, suffix = self.pending_extraction(executable, 60, 16)
                shell.open_menu()
                shell.keys("/")
                shell.text("overwrite")
                shell.keys("Enter")
                found = shell.wait_for(lambda state: state.cells[2] == "Filter: overwrite")
                self.assertIn("> -y ", found.cells[4])
                self.reach_detail(shell, found, "Use -aos to skip existing files.")
                shell.cancel()
                self.assertEqual(shell.read_buffer(), (prefix + suffix, len(prefix)))

                menu = shell.open_menu()
                self.assertIn("> -oDirectory", menu.cells[4])
                self.reach_detail(shell, menu, "named after each archive.")
                shell.cancel("Enter")
                self.assertEqual(shell.read_buffer(), (prefix + "-o" + suffix, len(prefix + "-o")))
                shell.text("'out dir'")
                self.assertEqual(shell.read_buffer(), (prefix + "-o'out dir'" + suffix, len(prefix + "-o'out dir'")))
                self.assertFalse(shell.executed.exists())

    def reach_detail(self, shell, screen, text):
        """Read successive small-screen Details lines until a particular qualification is visible."""
        while text not in " ".join(" ".join(screen.cells[8:-3]).split()):
            progress = screen.cells[-3]
            visible, total = progress.split()[1].split("/")
            last = int(visible.split("-")[1])
            self.assertLess(last, int(total), text)
            shell.keys("]")
            screen = shell.wait_for(lambda state: state.cells[-3] != progress)

    def test_extraction_rename_and_selection_at_minimum_size(self):
        """Scroll to the collision outcome, cancel, then select the mode before existing operands."""
        for executable in ("7z", "7zz"):
            shell, prefix, suffix = self.pending_extraction(executable, 60, 16)
            query = "rename the existing file"
            qualification = "The extracted file keeps its original name."
            for action in ("Escape", "Enter"):
                with self.subTest(executable=executable, action=action):
                    self.assertEqual(shell.open_menu().cells[2].rstrip(), "Filter:")
                    shell.keys("/")
                    shell.text(query)
                    shell.keys("Enter")
                    found = shell.wait_for(lambda screen: screen.cells[2] == "Filter: " + query
                                           and "> -aot " in screen.cells[4])
                    self.assertNotIn(qualification, " ".join(" ".join(found.cells[8:-3]).split()))
                    self.reach_detail(shell, found, qualification)
                    shell.cancel(action)
                    if action == "Escape":
                        self.assertEqual(shell.read_buffer(), (prefix + suffix, len(prefix)))
                    else:
                        self.assertEqual(shell.read_buffer(), (prefix + "-aot" + suffix, len(prefix + "-aot ")))
            self.assertFalse(shell.executed.exists())

    def test_fd_batch_search_insertion_and_child_boundary_at_minimum_size(self):
        """Read the child terminator, insert before quoted operands, and reject an edit inside the child."""
        for executable in ("fd", "fdfind"):
            shell, prefix, suffix = self.pending_finder(executable, 60, 16)
            qualification = "Pass a quoted semicolon to resume fd options."
            for action in ("Escape", "Enter"):
                with self.subTest(executable=executable, action=action):
                    self.assertEqual(shell.open_menu().cells[2].rstrip(), "Filter:")
                    shell.keys("/")
                    shell.text("batch placeholder")
                    shell.keys("Enter")
                    found = shell.wait_for(lambda state: state.cells[2] == "Filter: batch placeholder"
                                           and "> --exec-batch " in state.cells[4])
                    self.assertNotIn(qualification, " ".join(" ".join(found.cells[8:-3]).split()))
                    self.reach_detail(shell, found, qualification)
                    shell.cancel(action)
                    if action == "Escape":
                        self.assertEqual(shell.read_buffer(), (prefix + suffix, len(prefix)))
                    else:
                        self.assertEqual(shell.read_buffer(), (prefix + "--exec-batch" + suffix,
                                                               len(prefix + "--exec-batch ")))

            child = "fd-child --hidden"
            terminator = " {} ';' "
            shell.text(child + terminator)
            shell.keys(*(["Left"] * len(terminator)))
            shell.keys("Escape", "h")
            shell.wait_for(lambda state: state.alternate == 0 and "child_argument_boundary" in " ".join(state.cells))
            child_line = prefix + "--exec-batch " + child
            self.assertEqual(shell.read_buffer(), (child_line + terminator + suffix[1:], len(child_line)))
            self.assertFalse(shell.executed.exists())

    def test_attached_only_insertion_retains_payload_and_does_not_execute(self):
        shell = self.start()
        profile = json.loads((ROOT / "profiles/7z-x.json").read_text())
        self.configure(shell, profile)
        shell.text("7z() { printf executed > " + shlex.quote(str(shell.executed)) + "; }")
        shell.keys("Enter")
        shell.wait_for(lambda value: value.cells[value.y] == PROMPT.rstrip())
        line = "7z x 'archive.7z' -o"
        shell.text(line)
        shell.wait_for(lambda value: value.x == len(PROMPT + line))
        shell.open_menu()
        shell.keys("Enter")
        after = shell.wait_for(lambda value: value.alternate == 0 and value.x == len(PROMPT + line))
        self.assertEqual(after.history_markers(), HISTORY)
        self.assertEqual(shell.read_buffer(), (line, len(line)))
        shell.text("'café dir' -y")
        expected = "7z x 'archive.7z' -o'café dir' -y"
        before = shell.wait_for(lambda value: value.x == len(PROMPT + expected))
        shell.open_menu()
        self.assertEqual(shell.cancel(), before)
        self.assertEqual(shell.read_buffer(), (expected, len(expected)))
        self.assertFalse(shell.executed.exists())

    def test_declared_bundles_survive_selection_through_bash_adapter(self):
        shell = self.start()
        self.configure(shell, PROFILE)
        shell.text("typed -abn5 --fl")
        shell.wait_for(lambda value: value.x == len(PROMPT + "typed -abn5 --fl"))
        shell.open_menu()
        shell.keys("Enter")
        expected = "typed -abn5 --flag "
        after = shell.wait_for(lambda value: value.alternate == 0 and value.x == len(PROMPT + expected))
        self.assertEqual(after.history_markers(), HISTORY)
        self.assertEqual(shell.read_buffer(), (expected, len(expected)))
        self.assertFalse(shell.executed.exists())

    def test_configured_escape_delay_accepts_fragmented_down_key(self):
        shell = self.start()
        self.configure(shell, {"command": ["typed"], "description": "Fixture",
            "categories": [{"name": "Options", "options": [
                {"flag": "--alpha", "summary": "First"}, {"flag": "--beta", "summary": "Second"}]}]}, delay=250)
        shell.text("typed --")
        shell.wait_for(lambda value: value.x == len(PROMPT + "typed --"))
        shell.open_menu()
        shell.text("\x1bO")
        time.sleep(0.08)
        shell.text("B")
        menu = shell.wait_for(lambda value: value.alternate == 1 and "> --beta" in value.cells[5])
        shell.keys("Enter")
        after = shell.wait_for(lambda value: value.alternate == 0 and "--beta" in "".join(value.cells))
        self.assertEqual(after.history_markers(), HISTORY)
        self.assertEqual(shell.read_buffer(), ("typed --beta ", len("typed --beta ")))
        self.assertFalse(shell.executed.exists())

    def test_combining_search_and_fragmented_unmapped_alt_preserve_input(self):
        shell = self.start()
        self.configure(shell, {"command": ["typed"], "description": "Fixture",
            "categories": [{"name": "Options", "options": [
                {"flag": "--alpha", "summary": "cafe\u0301 界"}, {"flag": "--beta", "summary": "Other"}]}]}, delay=250)
        line = "typed --"
        shell.text(line)
        before = shell.wait_for(lambda value: value.x == len(PROMPT + line))
        shell.open_menu()
        shell.text("/")
        shell.keys("C-u")
        shell.text("cafe\u0301")
        shell.keys("Enter")
        menu = shell.wait_for(lambda value: "> --alpha" in value.cells[4] and "--beta" not in "".join(value.cells))
        self.assertIn("cafe\u0301 界", menu.cells[4])
        self.assertEqual(shell.cancel(), before)
        shell.open_menu()
        shell.text("\x1b")
        time.sleep(0.08)
        shell.text("x")
        cancelled = shell.wait_for(lambda value: value.alternate == 0 and value.x == len(PROMPT + line))
        self.assertEqual(cancelled, before)
        self.assertEqual(shell.read_buffer(), (line, len(line)))
        self.assertFalse(shell.executed.exists())

    def test_incomplete_bundle_error_preserves_input_and_reopens(self):
        shell = self.start()
        profile = copy.deepcopy(PROFILE)
        profile["categories"][0]["options"][2]["argument_style"] = "attached_only"
        self.configure(shell, profile)
        line = "typed -abn 'REVIEW_PRIVATE_SENTINEL' --fl"
        shell.text(line)
        shell.wait_for(lambda value: value.x == len(PROMPT + line))
        shell.keys("Escape", "h")
        after = shell.wait_for(lambda value: value.alternate == 0 and value.x == len(PROMPT + line)
            and any("interactive-help: option_value_required:" in row for row in value.cells))
        self.assertEqual(after.cells[after.y], PROMPT + line)
        self.assertEqual(after.history_markers(), HISTORY)
        error = next(row for row in after.cells if "interactive-help: option_value_required:" in row)
        self.assertNotIn("REVIEW_PRIVATE_SENTINEL", error)
        self.assertEqual(shell.read_buffer(), (line, len(line)))
        shell.keys("C-u")
        shell.text("typed -abn5 --fl")
        before = shell.wait_for(lambda value: value.x == len(PROMPT + "typed -abn5 --fl"))
        shell.open_menu()
        self.assertEqual(shell.cancel(), before)
        self.assertFalse(shell.executed.exists())
