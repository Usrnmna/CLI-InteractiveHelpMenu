"""Check the three viewports against the approved FFmpeg layout and actual input units."""
import json
import tempfile
import time
from pathlib import Path
import unittest
from unittest.mock import patch
from test_numerical_presentation import Browser, CellScreen, ROOT, draw, load_keys
from test_terminal_screen import TerminalTestCase, TMUX_AVAILABLE, TmuxShell
import ui
from ui import category_label


class MenuLevelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.profile = json.loads((ROOT / "profiles/ffmpeg.json").read_text())

    def test_stream_codecs_at_both_sizes(self):
        browser = Browser(self.profile)
        browser.category, browser.selected = 1, 4
        keys = load_keys()
        for width, height, counts in ((80, 24, (9, 7, 3)), (60, 16, (5, 3, 2))):
            for level, count in zip(("Simple", "Detailed", "Expanded"), counts):
                browser.level = level
                screen = CellScreen(height, width)
                self.assertEqual(draw(screen, browser, keys), count)
                self.assertIn(level, screen.text())
                self.assertIn("bps", screen.text())
                if level == "Expanded":
                    self.assertIn("Result (bps)", screen.text())

    def test_semantic_matches_are_independent_of_viewport(self):
        browser = Browser(self.profile, "bps")
        self.assertEqual([o["flag"] for o in browser.options(1)], ["-b:v", "-b:a"])
        self.assertNotIn("-bufsize", [o["flag"] for o in browser.options(13)])
        for name, flag, query in (("ss", "--info", "bps"), ("scp", "-l", "bps"),
                                  ("rsync", "--bwlimit=", "KiB/s"), ("go-test", "-timeout", "microseconds"),
                                  ("go-test", "-timeout", "MICROSECONDS"),
                                  ("esptool-write-flash", "--flash-freq", "MHz")):
            profile = json.loads((ROOT / f"profiles/{name}.json").read_text())
            browser = Browser(profile, query)
            self.assertIn(flag, [o["flag"] for i in range(len(profile["categories"])) for o in browser.options(i)])

    def test_citation_free_levels_and_semantic_prose_search(self):
        from test_numerical_presentation import read_expanded, specimen
        profile = specimen(summary="Set a bandwidth. Source: https://example.org/bps",
                           detail="Use --endpoint https://service.test/api. Read the guide at https://manual.test/guide")
        browser = Browser(profile)
        for level in ui.LEVELS:
            browser.level = level
            screen = CellScreen(16, 60)
            draw(screen, browser, load_keys())
            self.assertNotIn("example.org", screen.text())
            self.assertNotIn("manual.test", screen.text())
        text, _ = read_expanded(browser)
        self.assertIn("https://service.test/api", text)
        self.assertNotIn("manual.test", text)
        self.assertNotIn("example.org", text)
        option = profile["categories"][0]["options"][0]
        self.assertNotIn("bps", browser.text(option).prose_units)
        option["detail"] = "Report bytes per second and milliseconds, with a second column in b/s."
        browser = Browser(profile)
        self.assertTrue({"bps", "B/s", "ms"} <= browser.text(option).prose_units)

    def test_palette_uses_three_distinct_readable_roles_and_honors_no_color(self):
        colors = [(0, 0, 0), (700, 0, 0), (0, 800, 0), (900, 900, 0),
                  (0, 0, 700), (550, 0, 550), (0, 800, 800), (1000, 1000, 1000)]
        with patch.object(ui.curses, "has_colors", return_value=True), \
                patch.object(ui.curses, "COLORS", 8, create=True), \
                patch.object(ui.curses, "COLOR_PAIRS", 8, create=True), \
                patch.object(ui.curses, "use_default_colors"), \
                patch.object(ui.curses, "color_content", side_effect=colors.__getitem__), \
                patch.object(ui.curses, "color_pair", side_effect=lambda index: index), \
                patch.object(ui.curses, "init_pair") as init:
            for report, bg, choices in (("7;0", -1, [6, 3, 2]), ("0;7", -1, [4, 5, 1]),
                                        ("", 0, [6, 3, 2]), ("999", 0, [6, 3, 2])):
                with self.subTest(report=report), patch.dict(ui.os.environ, {"COLORFGBG": report, "NO_COLOR": ""}):
                    init.reset_mock()
                    self.assertEqual(ui.menu_colors(), (1, 2, 3))
                    self.assertEqual([call.args for call in init.call_args_list],
                                     [(i, fg, bg) for i, fg in enumerate(choices, 1)])
            with patch.dict(ui.os.environ, {"NO_COLOR": "1"}):
                init.reset_mock()
                self.assertEqual(ui.menu_colors(), (0, 0, 0))
                init.assert_not_called()

    def test_split_lists_share_the_baseline_and_leave_gutters(self):
        browser = Browser(self.profile)
        browser.category, browser.selected = 1, 4
        for height, width in ((16, 60), (24, 80), (40, 160)):
            left = min(26, width // 3)
            screen = CellScreen(height, width)
            draw(screen, browser, load_keys())
            rows = [(y, x, v) for (y, x, _), v in screen.cells.items() if v.startswith(("> ", "  "))]
            names = [y for y, x, _ in rows if x == 0]
            flags = [y for y, x, _ in rows if x == left]
            self.assertEqual(names[0], flags[0])
            self.assertEqual(names, list(range(names[0], names[-1] + 1, 2)))
            self.assertEqual(flags, list(range(flags[0], flags[-1] + 1, 2)))
            self.assertTrue(all(sum(map(ui.cell_width, v)) <= left - 3 for _, x, v in rows if x == 0))
            self.assertEqual(screen.cells[height - 2, 0, 0], "━" * (width - 1))
            self.assertIn("↑↓ move", screen.text())

    def test_short_details_have_no_paging_hint_and_custom_space_is_preserved(self):
        profile = {"command": ["short"], "description": "Short command", "categories": [{
            "name": "General", "options": [{"flag": "-v", "summary": "Print version"}]}]}
        browser = Browser(profile, guided=True)
        screen = CellScreen(16, 60)
        draw(screen, browser, load_keys())
        self.assertEqual(browser.compact_page, "options")
        browser.compact_page = "details"
        draw(screen, browser, load_keys())
        self.assertNotIn("Space", screen.text())
        self.assertIn("Print version", screen.text())
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "keys.json"
            path.write_text(json.dumps({"keys": {"accept": [" "]}}))
            keys = load_keys(path)
            self.assertEqual(keys["accept"], [" "])
            self.assertEqual(keys["detail_page"], ["P"])

    def test_level_hint_shows_shift_and_respects_remapped_keys(self):
        profile = {"command": ["example"], "description": "Example", "categories": [{
            "name": "General", "options": [{"flag": "-v", "summary": "Show version"}]}]}
        for width in (60, 80, 200):
            for binding, label in (("D", "Shift+D"), ("V", "Shift+V"), ("v", "v"), ("f6", "f6")):
                keys = load_keys()
                keys["cycle_detail"] = [binding]
                screen = CellScreen(24, width)
                browser = Browser(profile, guided=True)
                browser.key_color = 17
                draw(screen, browser, keys)
                self.assertIn("Simple   " + label + " change view", screen.text())
                hint = "Simple   " + label + " change view"
                start = width - 1 - len(hint)
                self.assertEqual(screen.cells[0, start, 0], hint)
                self.assertEqual(screen.cells[0, start + len("Simple   "), ui.curses.A_BOLD | 17], label)
                self.assertNotIn("motion", screen.text())

    def test_command_title_yields_its_prefix_before_clipping_the_path(self):
        """Keep the path and effective level binding visible in split and narrow layouts."""
        cases = (
            (80, "git stash push", "Interactive help | git stash push", " change view"),
            (60, "git stash push", "Help | git stash push", " change view"),
            (60, "git some longer subcommand", "git some longer subcommand", " change view"),
            (60, "tool example-界界界 long subcommand", "tool example-界界界 long subcommand", ""),
        )
        profile = {"description": "Title test", "categories": [{"name": "Options", "options": [
            {"flag": "-v", "summary": "Show version"}]}]}
        for width, command, title, suffix in cases:
            for guided in (False, True):
                for level in ui.LEVELS:
                    with self.subTest(width=width, command=command, guided=guided, level=level):
                        browser = Browser(dict(profile, command=command.split()), guided=guided)
                        browser.level = level
                        screen = CellScreen(16, width)
                        draw(screen, browser, load_keys())
                        self.assertEqual(screen.cells[0, 0, ui.curses.A_BOLD], title)
                        hint = level + "   Shift+D" + suffix
                        self.assertEqual(screen.cells[0, width - 1 - len(hint), 0], hint)

    def test_motion_deadline_unicode_and_final_frame(self):
        screen = CellScreen(16, 60)
        motion = ui.SummaryScroll()
        field = (1, 4, 24, 5, "界e\u0301ABCDE")
        motion.select(field, 10)
        motion.tick(screen, 11.999)
        self.assertFalse(screen.cells)
        motion.tick(screen, 12)
        self.assertEqual(screen.cells[4, 24, ui.curses.A_REVERSE], "…e\u0301AB…")
        motion.select(field, 12.1)
        self.assertEqual(motion.deadline, 12.25)
        motion.tick(screen, 12.25)
        motion.tick(screen, 12.5)
        self.assertEqual(screen.cells[4, 24, ui.curses.A_REVERSE], "…BCDE")
        self.assertIsNone(motion.deadline)
        motion.select((2, *field[1:]), 17)
        self.assertEqual(motion.deadline, 19)
        self.assertEqual(motion.visible, "")

    def test_motion_requires_a_clipped_focused_summary(self):
        profile = {"command": ["scroll"], "description": "Geometry", "categories": [{
            "name": "General", "options": [{"flag": "--a", "summary": "A" * 120},
                                           {"flag": "--b", "summary": "Short text"}]}]}
        keys = load_keys()
        for guided in (False, True):
            browser = Browser(profile, guided=guided)
            screen = CellScreen(16, 60)
            self.assertTrue(browser.scroll_summaries)
            draw(screen, browser, keys)
            width = browser.summary_field[3]
            text = browser.summary_field[4]
            self.assertGreater(len(text), width)
            draw(screen, browser, keys, searching=True)
            self.assertIsNone(browser.summary_field)
            browser.move_option(1)
            draw(screen, browser, keys)
            self.assertIsNone(browser.summary_field)
            browser.move_option(-1)
            browser.focus = browser.compact_page = "categories"
            draw(screen, browser, keys)
            self.assertIsNone(browser.summary_field)

    def test_existing_m_binding_takes_precedence(self):
        with tempfile.TemporaryDirectory() as folder:
            config = Path(folder) / "keys.json"
            config.write_text(json.dumps({"keys": {"last": ["m"]}}))
            keys = load_keys(config)
            self.assertEqual(keys["last"], ["m"])
            self.assertNotIn("toggle_summary_scroll", keys)
            config.write_text(json.dumps({"keys": {"last": ["m"], "toggle_summary_scroll": ["M"]}}))
            self.assertEqual(load_keys(config)["toggle_summary_scroll"], ["M"])

    def test_bundled_categories_fit_and_remain_distinct_at_minimum_width(self):
        for path in sorted((ROOT / "profiles").glob("*.json")):
            with self.subTest(path=path.name):
                categories = json.loads(path.read_text())["categories"]
                labels = [category_label(category["name"], 15) for category in categories]
                self.assertTrue(all("…" not in label for label in labels), labels)
                self.assertEqual(len(labels), len(set(labels)), labels)



@unittest.skipUnless(TMUX_AVAILABLE, "Rendered menu checks require Linux and tmux")
class TerminalMenuLevelTests(TerminalTestCase):
    def test_ffmpeg_views_and_search_at_both_sizes(self):
        """Drive the real Bash shortcut and verify selection, layout and cancellation."""
        shell = self.start()
        shell.text("ffmpeg ")
        for width, height, counts in ((80, 24, (9, 7, 3)), (60, 16, (5, 3, 2))):
            shell.resize(width, height)
            shell.open_menu()
            shell.keys("Right", *(["Down"] * 4))
            for mode, capacity in zip(("Simple", "Detailed", "Expanded"), counts):
                if mode != "Simple":
                    shell.keys("D")
                frame = shell.wait_for(lambda s: mode in s.cells[0] and any("> -b:v BITRATE" in r for r in s.cells))
                self.assertIn("Stream codecs", frame.cells[1])
                left = min(26, width // 3)
                rows = [row[left:] for row in frame.cells if row[left:].startswith(("  -", "> -"))]
                self.assertEqual(len(rows), capacity, frame.cells)
                self.assertIn("bits/second (bps)", "\n".join(frame.cells))
                if mode == "Expanded":
                    self.assertIn("Result (bps)", "\n".join(frame.cells))
            shell.keys("/", "b", "p", "s", "Enter")
            shell.wait_for(lambda s: s.cells[2] == "Filter: bps" and "1/2" in s.cells[3])
            shell.keys("D")
            shell.wait_for(lambda s: "Simple" in s.cells[0] and "1/2" in s.cells[3])
            shell.cancel()
            self.assertEqual(shell.read_buffer(), ("ffmpeg ", len("ffmpeg ")))

    def test_guided_narrow_flow_and_single_key_details_paging(self):
        """Visit each real narrow pane and both width boundaries with a pending Bash line."""
        shell = self.start()
        shell.text("export CLI_HELP_NARROW_MENU=1")
        shell.keys("Enter")
        shell.resize(60, 16)
        pending = "rsync "
        shell.text(pending)
        frame = shell.open_menu()
        self.assertIn("Simple   Shift+D change view", frame.cells[0])
        self.assertTrue(frame.cells[1].startswith("Categories"))
        self.assertIn("↑↓ move", frame.cells[-1])
        self.assertNotIn("Space", frame.cells[-1])
        shell.keys("D")
        shell.wait_for(lambda s: "Detailed" in s.cells[0] and s.cells[1].startswith("Categories"))
        shell.keys(*(["Down"] * 6), "Right", "/", "C-u")
        shell.text("--")
        shell.keys("Enter", "Down")
        for level in ("Detailed", "Expanded", "Simple"):
            if level != "Detailed":
                shell.keys("D")
            options = shell.wait_for(lambda s: level in s.cells[0] and s.cells[1].startswith("Options  ·  Filter: --"))
            self.assertIn("2/38", options.cells[1])
            self.assertTrue(any("> --bwlimit=RATE" in row for row in options.cells))
        shell.keys("Right")
        simple = shell.wait_for(lambda s: "Simple" in s.cells[0] and s.cells[1].startswith("Details"))
        self.assertIn("Limit bandwidth", simple.cells[4])
        self.assertNotIn("For transfers", " ".join(simple.cells))
        shell.keys("D")
        detailed = shell.wait_for(lambda s: "Detailed" in s.cells[0] and s.cells[1].startswith("Details"))
        self.assertIn("For transfers", " ".join(detailed.cells))
        self.assertNotIn("Input N ·", " ".join(detailed.cells))
        shell.keys("D")
        frame = shell.wait_for(lambda s: "Expanded" in s.cells[0] and "--bwlimit=RATE" in s.cells[3]
                               and "Space next" in s.cells[-1])
        opening = frame.cells[4:-3]
        seen = []
        while "Space next" in frame.cells[-1]:
            body = frame.cells[4:-3]
            seen.extend(body)
            shell.keys("Space")
            frame = shell.wait_for(lambda s: s.cells[4:-3] != body)
            self.assertLess(len(seen), 200)
        seen.extend(frame.cells[4:-3])
        self.assertIn("granularity", " ".join(seen))
        self.assertIn("Space top", frame.cells[-1])
        shell.keys("Space")
        shell.wait_for(lambda s: s.cells[4:-3] == opening)
        for width in (79, 80, 160, 60):
            state = shell.resize(width, 24)
            self.assertEqual("OPTIONS" in state.cells[3], width >= 80)
        self.assertTrue(state.cells[1].startswith("Details"))
        shell.keys("D")
        shell.wait_for(lambda s: "Simple" in s.cells[0] and s.cells[1].startswith("Details")
                       and "Limit bandwidth" in s.cells[4])
        shell.keys("Left")
        options = shell.wait_for(lambda s: "Simple" in s.cells[0] and s.cells[1].startswith("Options  ·  Filter: --"))
        self.assertIn("2/38", options.cells[1])
        self.assertTrue(any("> --bwlimit=RATE" in row for row in options.cells))
        shell.keys("Left")
        shell.wait_for(lambda s: any("> Network" in row for row in s.cells))
        shell.cancel()
        self.assertEqual(shell.read_buffer(), (pending, len(pending)))
        shell.keys("C-u")
        suffix = " 'untouched file'"
        shell.text("rsync --arch" + suffix)
        shell.keys(*(["Left"] * len(suffix)))
        shell.open_menu()
        shell.keys("Right", "Enter")
        shell.wait_for(lambda s: s.alternate == 0)
        self.assertEqual(shell.read_buffer(), ("rsync --archive" + suffix, len("rsync --archive ")))
        self.assertFalse(shell.executed.exists())

    def test_alt_h_scrolls_only_the_highlighted_summary(self):
        """Check default motion, the static override, and the unlisted keyboard toggle through Bash."""
        shell = self.start()
        shell.resize(60, 16)
        pending = "rsync "
        for guided in (False, True):
            with self.subTest(guided=guided):
                if guided:
                    shell.text("export CLI_HELP_NARROW_MENU=1 CLI_HELP_SCROLL_SUMMARIES=0")
                    shell.keys("Enter")
                shell.text(pending)
                shell.open_menu()
                navigation = ["Down"] * 6 + ["Right"] if guided else ["Right"] * 6
                shell.keys(*navigation, "Down")
                opening = shell.wait_for(lambda state: any("> --bwlimit=RATE" in line for line in state.cells))
                row = next(i for i, v in enumerate(opening.cells) if "> --bwlimit=RATE" in v)
                column = opening.cells[row].index("Limit bandwidth"[:8])
                self.assertTrue(opening.cells[row].endswith("…"))
                self.assertNotIn("motion", opening.cells[-1])
                if guided:
                    time.sleep(2.1)
                    self.assertEqual(shell.capture().cells, opening.cells)
                    shell.keys("m")
                # Observe the moving field in raw captures without requiring an animated frame to settle.
                start = time.monotonic()
                while time.monotonic() - start < 5:
                    cells = shell.capture().cells
                    if cells[row][column:].startswith("…"):
                        break
                    time.sleep(.04)
                self.assertTrue(cells[row][column:].startswith("…"))
                self.assertEqual(cells[row][:column], opening.cells[row][:column])
                self.assertEqual(cells[:row] + cells[row+1:-1], opening.cells[:row] + opening.cells[row+1:-1])
                shell.keys("m")
                stopped = shell.wait_for(lambda state: state.cells[row] == opening.cells[row])
                self.assertEqual(stopped.cells[-1], opening.cells[-1])
                time.sleep(2.1)
                self.assertEqual(shell.capture().cells, stopped.cells)
                shell.cancel()
                self.assertEqual(shell.read_buffer(), (pending, len(pending)))
                shell.keys("C-u")
                self.assertFalse(shell.executed.exists())

    def test_complete_custom_category_reachable_at_both_sizes(self):
        """Navigate to a clipped category and read its original words through the last line."""
        title = "Discovery and diagnostic options for an unusually long category with a distinctive ending"
        with tempfile.TemporaryDirectory() as directory:
            profile_dir = Path(directory) / "profiles"
            profile_dir.mkdir()
            profile = {"command": ["longcategory"], "description": "Test category navigation",
                       "categories": [{"name": name, "options": [{"flag": f"--info{index}", "summary": "Show status"}]}
                                      for index, name in enumerate(("Start", title))]}
            (profile_dir / "longcategory.json").write_text(json.dumps(profile))
            shell = TmuxShell(directory, profile_directory=profile_dir)
            try:
                shell.text("longcategory ")
                for width, height in ((80, 24), (60, 16)):
                    shell.resize(width, height)
                    shell.open_menu()
                    shell.keys("Right")
                    state = shell.wait_for(lambda s: "Category 2/2" in s.cells[1])
                    self.assertIn("…", state.cells[1])
                    for level in ("Simple", "Detailed", "Expanded"):
                        if level != "Simple":
                            shell.keys("D")
                            state = shell.wait_for(lambda s: level in s.cells[0])
                        rendered = list(state.detail_body)
                        while title not in " ".join(rendered):
                            start, end, total = state.detail_range
                            self.assertLess(end, total, state.cells)
                            shell.keys("]")
                            state = shell.wait_for(lambda s: s.detail_range[0] > start)
                            rendered.append(state.detail_body[-1])
                        self.assertIn(title, " ".join(rendered))
                    shell.cancel()
            finally:
                shell.close()
