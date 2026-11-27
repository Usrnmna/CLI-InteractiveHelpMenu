"""Exercise Details geometry in terminal cells and the associated curses emphasis."""
import curses
import unittest

from test_numerical_presentation import Browser, CellScreen, draw, load_keys, specimen
from ui import cell_width, layout_details


class DetailColumnTests(unittest.TestCase):
    def test_prose_sections_and_terms_in_both_layouts(self):
        profile = specimen()
        option = profile["categories"][0]["options"][0]
        option.pop("value_semantics", None)
        option.update(summary="Select the output.", detail="Limits: Requires 界 --format and RATE.\n"
                      "Fallback: Use the default if the value is missing.")
        for width in (60, 112):
            for color in (0, 17):
                with self.subTest(width=width, color=color):
                    browser = Browser(profile, level="Expanded", guided=True)
                    browser.compact_page = "details"
                    browser.accent, browser.section_color = color, color * 2
                    screen = CellScreen(36, width)
                    draw(screen, browser, load_keys())
                    roles = {word: (y, x, attr) for (y, x, attr), word in screen.cells.items()
                             if word in {"Limits:", "Fallback:", "--format", "RATE"}}
                    y, x, attr = roles["Limits:"]
                    self.assertEqual((x, attr), (0, curses.A_BOLD | browser.section_color))
                    self.assertEqual(roles["--format"], (y, len("Limits: Requires ") + 3,
                                                         curses.A_UNDERLINE | browser.accent))
                    self.assertEqual(roles["RATE"][2], curses.A_UNDERLINE | browser.accent)
                    self.assertGreaterEqual(roles["Fallback:"][0], y + 2)

    def test_below_and_at_each_transition_in_both_color_modes(self):
        items = [f"v{i}: short" for i in range(12)]
        for width, starts in ((62, [0]), (63, [0, 33]), (95, [0, 49]), (96, [0, 33, 66])):
            with self.subTest(width=width):
                mono = layout_details(["Values:", *items], width, 0)
                self.assertEqual(mono, layout_details(["Values:", *items], width, curses.A_DIM))
                heading, *rows = mono
                self.assertEqual(heading.highlights, [(0, "Values:", curses.A_BOLD)])
                self.assertEqual([x for x, _, _ in rows[0].highlights], starts)
                names = [name for col in starts for row in rows for x, name, style in row.highlights if x == col]
                self.assertEqual(names, [f"v{i}" for i in range(12)])
                for row in rows:
                    self.assertLessEqual(len(row.text), width)
                    for x, name, style in row.highlights:
                        self.assertTrue(row.text[x:].startswith(name + ": short"))
                        self.assertEqual(style, curses.A_UNDERLINE)
                        if x:
                            self.assertEqual(row.text[x-3:x], "   ")

    def test_real_frame_reserves_the_right_margin_before_measuring_columns(self):
        profile = specimen()
        option = profile["categories"][0]["options"][0]
        option.pop("value_semantics", None)
        option["detail"] = "Values:\n" + "\n".join(f"v{i}: short" for i in range(12))
        browser = Browser(profile, level="Expanded")
        for terminal_width, starts in ((63, {0}), (64, {0, 33}), (96, {0, 49}), (97, {0, 33, 66})):
            with self.subTest(terminal_width=terminal_width):
                frames = []
                for accent in (0, curses.A_DIM):
                    browser.accent = accent
                    screen = CellScreen(40, terminal_width)
                    draw(screen, browser, load_keys())
                    positions = {(r, x, word) for (r, x, attr), word in screen.cells.items()
                                 if attr == curses.A_UNDERLINE}
                    self.assertEqual({x for _, x, _ in positions}, starts)
                    self.assertEqual({word for _, _, word in positions}, {f"v{i}" for i in range(12)})
                    frames.append((screen.detail_body(), positions))
                self.assertEqual(frames[0], frames[1])

    def test_mixed_lengths_keep_wrapped_meaning_in_its_column(self):
        items = [f"--flag{i}  Summary" for i in range(9)]
        items[3] = "--flag3  A description with several words that finishes here."
        mono = layout_details(items, 96, 0)
        color = layout_details(items, 96, curses.A_DIM)
        self.assertEqual([r.text for r in mono], [r.text for r in color])
        for plain, styled in zip(mono, color):
            self.assertEqual(styled.highlights, [(x, name, attr | curses.A_DIM) for x, name, attr in plain.highlights])
        starts = sorted({x for row in mono for x, _, _ in row.highlights})
        self.assertEqual(starts, [0, 33, 66])
        col = next(x for row in mono for x, word, _ in row.highlights if word == "--flag3")
        text = " ".join(row.text[col:col + 30].strip() for row in mono)
        self.assertIn(items[3], text)
        self.assertIn("--flag4", text[text.index("here."):])

    def test_prose_short_and_heavily_wrapped_lists_use_one_column(self):
        for lines in (["Input N · bytes"] * 5,
                      ["An ordinary sentence explains an option."] * 12,
                      ["--config  " + "configuration settings " * 5] * 9):
            rows = layout_details(lines, 96, 0)
            self.assertTrue(all(len(row.highlights) <= 1 for row in rows))
        rows = layout_details(["Input 界 · units"] * 9, 96, 0)
        self.assertEqual([x for x, _, _ in rows[0].highlights], [6, 39, 72])
        self.assertLessEqual(sum(map(cell_width, rows[0].text)), 96)

    def test_option_styles_preserve_explanations_and_selected_row(self):
        profile = specimen()
        category = profile["categories"][0]
        category["options"].append({"flag": "--next", "summary": "Second choice"})
        browser = Browser(profile)
        for accent in (0, curses.A_DIM):
            browser.accent = accent
            screen = CellScreen(24, 80)
            draw(screen, browser, load_keys())
            self.assertIn("--next", [v for (_, _, attr), v in screen.cells.items() if attr == curses.A_BOLD | accent])
            self.assertTrue(any(v.startswith("> --value") and attr == curses.A_REVERSE
                                for (_, _, attr), v in screen.cells.items()))
