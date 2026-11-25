"""Check the three viewports against the approved FFmpeg layout and actual input units."""
import json
import tempfile
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

    def test_accent_respects_background_contrast_and_monochrome(self):
        colors = {0: (0, 0, 0), 7: (1000, 1000, 1000), 6: (0, 800, 800), 4: (0, 0, 800)}
        with patch.object(ui, "curses") as terminal:
            terminal.COLOR_PAIRS = 8
            terminal.COLOR_CYAN, terminal.COLOR_BLUE = 6, 4
            terminal.color_content.side_effect = colors.__getitem__
            terminal.color_pair.return_value = 123
            for background, accent in (("0", 6), ("7", 4)):
                with patch.dict(ui.os.environ, {"COLORFGBG": "7;" + background, "NO_COLOR": ""}):
                    self.assertEqual(ui.option_accent(), 123)
                    terminal.init_pair.assert_called_with(1, accent, -1)
            for background, no_color in (("", ""), ("0", "1")):
                with patch.dict(ui.os.environ, {"COLORFGBG": background, "NO_COLOR": no_color}):
                    self.assertEqual(ui.option_accent(), 0)

    def test_bundled_categories_fit_and_remain_distinct_at_minimum_width(self):
        for path in sorted((ROOT / "profiles").glob("*.json")):
            with self.subTest(path=path.name):
                categories = json.loads(path.read_text())["categories"]
                labels = [category_label(category["name"], 16) for category in categories]
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
