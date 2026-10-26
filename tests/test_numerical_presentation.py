"""Protect visible and searchable value guidance without invoking target programs.

Factual expectations reuse the reviewed migration-evidence fixture. Synthetic
declarations test layout and failure handling without asserting upstream facts.
Fake windows establish browser draw behavior, not native terminal acceptance.
"""

from contextlib import ExitStack
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cli_help"))
if importlib.util.find_spec("curses") is None:
    import curses_stub
    sys.modules["curses"] = curses_stub

import presentation
import ui
from core import find_context, insert_option
from discovery import build_profile, merge_profiles
from presentation import option_label
from test_functional_matrix import BrowserLoop, FakeScreen
from test_value_semantics import contract, synthetic_node
from ui import Browser, cell_width, draw, ellipsize_cells, load_keys, run_browser, wrap_cells
from value_semantics import format_value_semantics


def specimen(*nodes, **option_fields):
    """Build a synthetic one-option profile with deliberately long context."""
    option = {"flag": "--value", "argument": "MAGNITUDE", "summary": "A synthetic selectable value",
              "detail": "Original useful prose remains accessible.", "value_semantics": contract(*nodes)}
    option.update(option_fields)
    return {"command": ["synthetic-contract"], "description": "Synthetic presentation specimen",
            "categories": [{"name": "Values", "description": "Long category context. " * 12,
                            "options": [option]}]}


def first_option(profile):
    return profile["categories"][0]["options"][0]


class CellScreen(FakeScreen):
    """Reject out-of-window writes using the same documented Unicode cell model."""

    def addnstr(self, row, col, text, n, attr=0):
        if not 0 <= row < self.lines or not 0 <= col < self.columns:
            raise AssertionError("Draw attempted an out-of-window location")
        if col + sum(cell_width(c) for c in text[:n]) > self.columns:
            raise AssertionError("Draw exceeded terminal cell width")
        super().addnstr(row, col, text, n, attr)


class NumericalPresentationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.profiles = {path.stem: json.loads(path.read_text(encoding="utf-8"))
                        for path in sorted((ROOT / "profiles").glob("*.json"))}
        cls.evidence = json.loads((ROOT / "tests/fixtures/value-semantics/migration-evidence.json")
                                  .read_text(encoding="utf-8"))["sources"]

    def setUp(self):
        """Block operational boundaries for every presentation test."""
        stack = ExitStack()
        self.addCleanup(stack.close)
        for target in ("subprocess.Popen", "subprocess.run", "os.system", "os.popen",
                       "socket.socket", "socket.create_connection", "socket.getaddrinfo", "discovery.run_probe"):
            stack.enter_context(patch(target, side_effect=AssertionError("Presentation attempted a non-passive operation")))

    def view(self, name, flag):
        profile = self.profiles[name]
        browser = Browser(profile, flag)
        option = next(o for c in profile["categories"] for o in c["options"] if o["flag"] == flag)
        return browser, option, browser.text(option)

    def all_details(self, browser, width=60, height=16):
        """Visit each scroll position through the real draw path until clamped."""
        screen = CellScreen(height, width)
        detail_row = 4 + max(3, (height - 9) // 2)
        collected = []
        for _ in range(4000):
            draw(screen, browser, load_keys(None))
            collected.extend(value for (row, _col, _attr), value in sorted(screen.cells.items())
                             if detail_row < row < height - 3)
            old = browser.detail_offset
            browser.detail_offset += 1
            draw(screen, browser, load_keys(None))
            if browser.detail_offset == old:
                break
        else:
            self.fail("Details did not reach a finite final scroll position")
        return " ".join(collected), screen

    def test_formatter_reaches_list_details_and_search_without_duplicate_interpretation(self):
        profile = specimen()
        with patch.object(presentation, "format_value_semantics", return_value=(
                "Value: distinctive-unit-marker.", "Accepted form: distinctive-suffix-marker.")) as formatter:
            browser = Browser(profile)
            self.assertEqual(formatter.call_count, 1)
            self.assertTrue(formatter.call_args.kwargs["presentation"])
            screen = CellScreen(24, 160)
            draw(screen, browser, load_keys(None))
            self.assertIn("distinctive-unit-marker", screen.text())
            for query in ("distinctive-unit-marker", "distinctive-suffix-marker", "MAGNITUDE"):
                browser.set_query(query)
                self.assertEqual(browser.options(), [first_option(profile)])
            self.assertEqual(formatter.call_count, 1)
            details, _ = self.all_details(browser)
            self.assertIn("distinctive-suffix-marker", details)

    def test_every_opted_in_bundled_option_retains_formatter_lines(self):
        selected = 0
        for profile in self.profiles.values():
            before = deepcopy(profile)
            browser = Browser(profile)
            for category in profile["categories"]:
                for option in category["options"]:
                    if "value_semantics" not in option:
                        continue
                    selected += 1
                    view = browser.text(option)
                    expected = format_value_semantics(option["value_semantics"],
                                                      definitions=profile.get("value_definitions"), presentation=True)
                    with self.subTest(command=profile["command"], flag=option["flag"]):
                        self.assertNotIn("could not be interpreted", " ".join(view.details))
                        for line in expected:
                            self.assertIn(line, view.details)
                            self.assertIn(line.casefold(), view.searchable)
            self.assertEqual(profile, before)
        self.assertGreater(selected, 0)  # Scope grows with explicit metadata, not historical totals.

    def test_reference_rates_keep_bits_bytes_and_version_scope_distinct(self):
        for name, flag, source, unit in (("rsync", "--bwlimit=", "rsync", "bytes/second"),
                                         ("scp", "-l", "openssh", "bits/second"),
                                         ("sftp", "-l", "openssh", "bits/second")):
            browser, option, view = self.view(name, flag)
            field = "bare_bytes_per_second" if source == "rsync" else "bare_bits_per_second"
            self.assertIn(self.evidence[source][field] + " " + unit, view.compact)
            self.assertIn("scoped", view.compact)
            self.assertIn(self.evidence[source]["version"], " ".join(view.details))
            self.assertIn("not established", " ".join(view.details))
            browser.set_query(unit)
            self.assertIn(option, browser.options())

    def test_reference_time_scales_and_specials_are_searchable(self):
        browser, option, view = self.view("ffmpeg", "-t")
        self.assertIn("bare: seconds", view.compact)
        for query in (self.evidence["ffmpeg_time"]["milliseconds"] + " seconds", "'ms'", "duration"):
            browser.set_query(query)
            self.assertIn(option, browser.options())
        browser, option, view = self.view("go-test", "-timeout")
        self.assertIn("ordinary bare numbers not accepted", view.compact)
        for query in ("negative", "disables", "omitted", "Nms"):
            browser.set_query(query)
            self.assertIn(option, browser.options())
        self.assertIn(self.evidence["go_test"]["version"], " ".join(view.details))

    def test_reference_binary_decimal_and_literal_token_meanings(self):
        _, _, view = self.view("rsync", "--bwlimit=")
        self.assertIn(self.evidence["rsync"]["decimal_kb"] + " bytes/second", " ".join(view.details))
        self.assertIn(self.evidence["rsync"]["binary_k"] + " bytes/second", " ".join(view.details))
        browser, option, view = self.view("esptool-write-flash", "--flash-size")
        self.assertIn("varies by applicability", view.compact)
        binary_bytes = str(4 * int(self.evidence["esptool5"]["bytes_per_MB"])) + " bytes"
        for query in ("4MB", binary_bytes, "ESP8266", self.evidence["esptool5"]["version"]):
            browser.set_query(query)
            self.assertIn(option, browser.options())
        self.assertNotIn("4000000 bytes", view.searchable)

    def test_reference_counts_indices_levels_percentages_and_identifiers(self):
        self.assertIn("all", self.evidence["pytest"]["zero"])
        cases = (("pytest", "--durations", ("count of", "all measured durations")),
                 ("fzf", "--nth", ("Index origin: " + self.evidence["fzf"]["origin"],)),
                 ("fzf", "--height", ("terminal rows", "0.01 of terminal height", "'%'")),
                 ("journalctl", "--priority=", ("Ordering:", "0", "7")),
                 ("journalctl", "--boot=", ("identifier",)))
        for name, flag, terms in cases:
            browser, option, view = self.view(name, flag)
            for term in terms:
                with self.subTest(name=name, flag=flag, term=term):
                    browser.set_query(term)
                    self.assertIn(option, browser.options())
                    self.assertIn(term.casefold(), " ".join(view.details).casefold())

    def test_all_other_meaning_kinds_use_the_shared_formatter(self):
        for kind in ("count", "identifier", "index", "level", "enumeration", "timestamp", "duration_expression"):
            profile = specimen(synthetic_node(kind, meaning="Select synthetic entries"))
            browser = Browser(profile)
            text = " ".join(browser.text(first_option(profile)).details)
            self.assertIn("Select synthetic entries", text)
            self.assertNotIn("guidance unavailable", text)
            if kind == "index":
                self.assertIn("Index origin: 0", text)
            if kind in {"timestamp", "duration_expression"}:
                self.assertIn("Time basis:", text)
        profile = specimen(synthetic_node("delegated", bare={"state": "not_applicable", "reason": "Per-key grammar"},
                                         forms=[{"id": "setting", "notation": "expression", "syntax": "KEY=VALUE",
                                                 "grammar": "Meaning depends on the selected key"}],
                                         grammar={"name": "Synthetic settings", "reference": {
                                             "source": "synthetic:settings", "locator": "per-key meanings"}}))
        view = Browser(profile).text(first_option(profile))
        self.assertIn("Delegated grammar: Synthetic settings", " ".join(view.details))
        self.assertNotIn("guidance unavailable", view.compact)

    def test_source_derived_and_unresolved_keep_specific_investigation(self):
        for status in ("source_derived", "unresolved"):
            node = synthetic_node("unresolved", meaning="Unconfirmed numerical rule",
                                  review={"status": status, "references": [{"source": "synthetic:unknown", "locator": "capture"}]},
                                  bare={"state": "unverified", "reason": "Default scale absent"},
                                  forms=[{"id": "unknown", "notation": "expression", "syntax": "EXPR",
                                          "grammar": "Captured expression without a verified scale"}],
                                  investigation="Determine the exact firmware version and scale")
            profile = specimen(node)
            browser = Browser(profile)
            view = browser.text(first_option(profile))
            self.assertIn(status.replace("_", " "), view.compact)
            self.assertIn("not verified", view.compact)
            browser.set_query("firmware version")
            self.assertEqual(browser.options(), [first_option(profile)])

    def test_malformed_metadata_is_nonfatal_and_does_not_guess_units(self):
        for metadata in ([], {"schema_version": 99}, contract({"ref": "missing"}),
                         contract(synthetic_node(kind="unknown"))):
            profile = specimen(value_semantics=metadata)
            browser = Browser(profile)
            self.assertIn("guidance unavailable", browser.text(first_option(profile)).compact)
            browser.set_query("Original useful prose")
            self.assertEqual(browser.options(), [first_option(profile)])
            draw(CellScreen(16, 60), browser, load_keys(None))

    def test_formatter_failure_retains_original_prose(self):
        profile = specimen()
        with patch.object(presentation, "format_value_semantics", side_effect=ValueError("synthetic failure")):
            browser = Browser(profile)
        text = " ".join(browser.text(first_option(profile)).details)
        self.assertIn("units have not been inferred", text)
        self.assertIn("Original useful prose", text)
        self.assertNotIn("synthetic failure", text)

    def test_partial_and_absent_contracts_do_not_become_loading_gates(self):
        for metadata in (None, {"schema_version": 1, "variants": [{"kind": "duration"}]}):
            profile = specimen(value_semantics=metadata)
            browser = Browser(profile)
            self.assertTrue(browser.options())
            self.assertIn("not documented", " ".join(browser.text(first_option(profile)).details))
        profile = specimen()
        del first_option(profile)["value_semantics"]
        browser = Browser(profile)
        self.assertEqual(browser.text(first_option(profile)).compact, "")
        for query in ("--value", "MAGNITUDE", "selectable", "Original useful prose"):
            browser.set_query(query.upper())
            self.assertEqual(browser.options(), [first_option(profile)])

    def test_multiple_unknown_matches_show_all_qualified_variants(self):
        a, b = synthetic_node("duration"), synthetic_node("duration")
        a["applicability"]["version"] = {"state": "known", "values": ["1"]}
        b["applicability"]["version"] = {"state": "known", "values": ["2"]}
        b["forms"][0]["unit"]["multiplier"] = "0.001"
        profile = specimen(a, b)
        browser = Browser(profile)
        view = browser.text(first_option(profile))
        self.assertIn("varies by applicability", view.compact)
        self.assertIn("Value variant 1", " ".join(view.details))
        self.assertIn("Value variant 2", " ".join(view.details))
        self.assertIn("0.001 seconds", " ".join(view.details))
        self.assertIn("No target match is assumed", view.details[0])
        for query in ("version: 1", "version: 2", "0.001 seconds"):
            browser.set_query(query)
            self.assertEqual(browser.options(), [first_option(profile)])

    def test_inactive_declarations_remain_unformatted_and_unsearchable_as_claims(self):
        profile = specimen()
        profile["documentation"] = {
            "semantic_sources": {"--value": "selected source"},
            "alternatives": [{"option": "--value", "source": "competing source",
                              "metadata": {"meaning": "INACTIVE_SCALE_CLAIM"}}],
            "diagnostics": [{"option": "--value", "source": "competing source", "code": "internal_code",
                             "message": "The documented units disagree; inspect the original sources."}]}
        original = deepcopy(profile)
        with patch.object(presentation, "format_value_semantics", wraps=format_value_semantics) as formatter:
            browser = Browser(profile)
            self.assertEqual(formatter.call_count, 1)
        view = browser.text(first_option(profile))
        self.assertIn("Source review", view.compact)
        self.assertIn("Source review", view.details[0])
        self.assertIn("not applied as value guidance", " ".join(view.details))
        self.assertIn("Numerical source: selected source", view.details)
        browser.set_query("INACTIVE_SCALE_CLAIM")
        self.assertEqual(browser.options(), [])
        self.assertNotIn("internal_code", " ".join(view.details))
        self.assertEqual(profile, original)

    def test_source_conflict_prose_remains_distinguishable_and_searchable(self):
        a = build_profile("tool", [("first capture", "Options:\n  --wait N  Wait in seconds")])
        b = build_profile("tool", [("second capture", "Options:\n  --wait N  Wait in milliseconds")])
        profile = merge_profiles([a, b])
        browser = Browser(profile)
        view = browser.text(first_option(profile))
        self.assertIn("Source review", view.compact)
        text = " ".join(view.details)
        for query in ("seconds", "milliseconds"):
            browser.set_query(query)
            self.assertEqual(len(browser.options()), 1)
            self.assertIn(query, text)
        self.assertIn("Source:", text)

    def test_assigned_shared_prose_is_searchable_unassigned_context_is_not_associated(self):
        profile = build_profile("tool", [("synthetic help", "Options:\n  --size SIZE  Buffer amount\n\n"
                                         "SIZE is measured in 1024-byte blocks.\n\n"
                                         "Units are unresolved-special-context.\n")])
        browser = Browser(profile)
        option = first_option(profile)
        browser.set_query("1024-byte")
        self.assertIn(option, browser.options())
        browser.set_query("unresolved-special-context")
        self.assertEqual(browser.options(), [])
        self.assertIn("unresolved-special-context", " ".join(browser.text(option).details))
        self.assertIn("relationship to this option is unverified", " ".join(browser.text(option).details))

    def test_shared_references_and_positional_components_reach_details_and_search(self):
        profile = json.loads((ROOT / "tests/fixtures/value-semantics/synthetic-profile.json").read_text(encoding="utf-8"))
        browser = Browser(profile, "0.001 seconds")
        self.assertEqual({o["flag"] for o in browser.options()}, {"--delay", "-d"})
        for name, profile in self.profiles.items():
            if "positional_value_semantics" not in profile:
                continue
            browser = Browser(profile)
            option = first_option(profile)
            view = browser.text(option)
            expected = format_value_semantics(profile["positional_value_semantics"],
                                              definitions=profile.get("value_definitions"), presentation=True)
            for line in expected:
                self.assertIn(line, view.details, name)
                self.assertIn(line.casefold(), view.searchable, name)
            browser.set_query("Repeated value group (command-wide)")
            self.assertTrue(browser.options())

    def test_selected_details_start_with_units_before_long_category_and_summary(self):
        node = synthetic_node("duration")
        profile = specimen(node, summary="A lengthy explanation " * 20)
        browser = Browser(profile)
        screen = CellScreen(16, 60)
        draw(screen, browser, load_keys(None))
        detail_row = 4 + max(3, (16 - 9) // 2)
        visible = " ".join(v for (r, _c, _a), v in sorted(screen.cells.items()) if detail_row < r < 13)
        self.assertIn("bare numbers: seconds", visible)
        self.assertNotIn("Long category context", visible)
        self.assertNotIn("A lengthy explanation", visible)

    def test_long_placeholder_leaves_room_for_summary_and_full_details(self):
        profile = specimen(synthetic_node("duration"), argument="LONG_PLACEHOLDER_" * 12)
        browser = Browser(profile)
        screen = CellScreen(24, 140)
        draw(screen, browser, load_keys(None))
        row = next(v for (r, c, _a), v in screen.cells.items() if r == 4 and c > 0)
        self.assertIn("A synthetic selectable value", row)
        self.assertIn("…", row)
        details, _ = self.all_details(browser)
        self.assertIn("seconds", details)
        self.assertIn("LONG_PLACEHOLDER_", details)
        self.assertIn(first_option(profile)["argument"], " ".join(browser.text(first_option(profile)).details))

    def test_option_descriptions_align_and_keep_the_same_column_when_scrolling(self):
        """Declaration length and selection cannot move the summary column."""
        profile = {"command": ["layout"], "description": "Layout specimen", "categories": [{
            "name": "Options", "options": [
                {"flag": flag, "summary": "Summary " + str(index)}
                for index, flag in enumerate(("-a", "--longer-name", "--third", "--last-option"))]}]}
        for width in (60, 100, 160):
            browser = Browser(profile)
            screen = CellScreen(16, width)
            columns = []
            for selected in (0, 3):
                browser.selected = selected
                draw(screen, browser, load_keys(None))
                rows = [v for (r, c, _a), v in screen.cells.items() if 4 <= r < 7 and c > 0]
                columns.extend(v.index("Summary") for v in rows)
            self.assertEqual(len(set(columns)), 1, (width, columns))

    def test_bundled_rows_prioritize_summaries_without_repeating_nonnumerical_guidance(self):
        cases = (("rsync", "--exclude="), ("ls", "--color="),
                 ("grep", "--regexp="), ("tar", "--file="))
        for name, flag in cases:
            for width in (60, 100, 160):
                with self.subTest(name=name, width=width):
                    browser, option, view = self.view(name, flag)
                    screen = CellScreen(16, width)
                    draw(screen, browser, load_keys(None))
                    row = next(v for (r, c, _a), v in screen.cells.items() if r == 4 and c > 0)
                    self.assertIn(option["summary"].split()[0], row)
                    self.assertNotIn("(scoped)", row)
                    self.assertIn(option["summary"], "\n".join(view.details))
                    browser.set_query("scoped")
                    self.assertIn(option, browser.options())

    def test_value_hint_is_complete_or_absent_and_summary_remains_visible(self):
        """Units and scope must never appear as a truncated fragment in a row."""
        for width in (60, 100, 240):
            browser, option, view = self.view("rsync", "--bwlimit=")
            screen = CellScreen(16, width)
            draw(screen, browser, load_keys(None))
            row = next(v for (r, c, _a), v in screen.cells.items() if r == 4 and c > 0)
            self.assertIn("Limit bandwidth", row)
            if "bare:" in row:
                self.assertIn(view.compact, row)
                self.assertIn(option["summary"], row)
            else:
                self.assertNotIn("(scoped)", row)
            if width == 240:
                self.assertIn("1024 bytes/second", row)

    def test_review_and_uncertainty_notices_survive_narrow_rows(self):
        """Hidden value hints cannot hide review requirements or uncertainty."""
        profiles = [specimen(value_semantics=[]), specimen(synthetic_node("duration"))]
        reviewed = specimen()
        reviewed["documentation"] = {"diagnostics": [{"option": "--value", "message": "Conflicting sources."}]}
        profiles.append(reviewed)
        for profile, notice in zip(profiles, ("[review]", "[unverified]", "[review]")):
            screen = CellScreen(16, 60)
            browser = Browser(profile)
            draw(screen, browser, load_keys(None))
            row = next(v for (r, c, _a), v in screen.cells.items() if r == 4 and c > 0)
            self.assertIn(notice, row)
            self.assertNotIn("bare:", row)

    def test_unicode_declarations_align_in_cells_and_empty_results_clear_rows(self):
        """Wide and combining characters use cells; a new filter erases old rows."""
        profile = {"command": ["layout"], "description": "Layout specimen", "categories": [{
            "name": "Options", "options": [
                {"flag": "--wide", "argument": "界界", "summary": "Summary wide"},
                {"flag": "--accent", "argument": "e\u0301", "summary": "Summary accent"}]}]}
        browser = Browser(profile)
        for width in (60, 100, 160, 60):
            screen = CellScreen(16, width)
            draw(screen, browser, load_keys(None))
            rows = [v for (r, c, _a), v in screen.cells.items() if 4 <= r <= 5 and c > 0]
            columns = [sum(cell_width(c) for c in row[:row.index("Summary")]) for row in rows]
            self.assertEqual(columns[0], columns[1])
            browser.set_query("no-such-option")
            draw(screen, browser, load_keys(None))
            self.assertIn("No matches", screen.text())
            self.assertNotIn("Summary wide", screen.text())
            browser.set_query("")

    def test_all_details_are_reachable_at_minimum_size_with_scroll_indicator(self):
        browser, _option, view = self.view("rsync", "--bwlimit=")
        text, screen = self.all_details(browser)
        self.assertIn("Details", screen.text())
        self.assertIn("scroll", screen.text())
        self.assertIn("No bandwidth limit", text)
        self.assertIn("Reference:", text)
        self.assertIn("3.4.1", text)
        # Compare the actual wrapped lines, including complete suffix rules.
        actual = text.replace(" ", "")
        for paragraph in view.details:
            for line in paragraph.splitlines():
                for wrapped in wrap_cells(line, 58):
                    self.assertIn(wrapped.replace(" ", ""), actual)

    def test_unicode_clipping_wrapping_and_controls_preserve_cell_limits(self):
        node = synthetic_node("count", meaning="Count e\u0301界 records", subject="e\u0301界 records")
        profile = specimen(node, summary="Unicode e\u0301界 " * 10, detail="Control: \x1b[31m text\ud800")
        for width in (60, 61, 80, 120):
            browser = Browser(profile)
            text, _ = self.all_details(browser, width=width)
            self.assertIn("e\u0301界", text)
            self.assertNotIn("\x1b", text)
            self.assertNotIn("\ud800", text)
        self.assertEqual(ellipsize_cells("界界x", 4), "界…")
        self.assertEqual(ellipsize_cells("e\u0301xy", 2), "e\u0301…")
        self.assertEqual(ellipsize_cells("x", 0), "")

    def test_resize_shrink_grow_and_reopen_preserve_selection_and_reachable_text(self):
        browser, option, _view = self.view("rsync", "--bwlimit=")
        screen = CellScreen(40, 140)
        browser.detail_offset = 7
        for height, width in ((40, 140), (16, 60), (10, 40), (24, 100), (16, 60)):
            screen.lines, screen.columns = height, width
            draw(screen, browser, load_keys(None))
            self.assertIs(browser.options()[browser.selected], option)
            if height < 16 or width < 60:
                self.assertIn("Resize to at least", screen.text())
            else:
                self.assertIn("Details", screen.text())
        browser.detail_offset = 0
        draw(screen, browser, load_keys(None))
        self.assertIn("1024 bytes/second", screen.text())
        reopened = Browser(browser.profile, "--bwlimit=")
        self.assertEqual(reopened.detail_offset, 0)
        self.assertEqual(reopened.text(option), browser.text(option))

    def test_search_changes_detail_height_and_repeated_queries_are_pure(self):
        profile = specimen()
        extra = {"flag": "--quiet", "summary": "Brief legacy flag"}
        profile["categories"][0]["options"].append(extra)
        before = deepcopy(profile)
        browser = Browser(profile)
        browser.detail_offset = 5000
        for query in ("MAGNITUDE", "bytes", "quiet", "nothing-matches", "", "bytes"):
            browser.set_query(query)
            self.assertEqual(browser.detail_offset, 0)
            draw(CellScreen(16, 60), browser, load_keys(None))
        self.assertEqual(profile, before)
        self.assertIs(browser.options()[0], first_option(profile))

    def test_browser_reopening_derives_fresh_text_without_persistent_cache(self):
        profile = specimen()
        first = Browser(profile)
        first_option(profile)["value_semantics"]["variants"][0]["forms"][0]["unit"]["multiplier"] = "1024"
        second = Browser(profile)
        self.assertNotEqual(first.text(first_option(profile)), second.text(first_option(profile)))
        self.assertIn("1024 bytes", second.text(first_option(profile)).compact)

    def test_scripted_search_restore_preview_and_literal_selection_use_existing_controls(self):
        profile = specimen()
        screen = CellScreen(24, 120, ["/", *"seconds", "\x1b", "\n"])
        with BrowserLoop(screen):
            selected = run_browser(screen, profile, "", load_keys(None), preview=True)
        self.assertIs(selected, first_option(profile))
        self.assertIn("inspect", screen.text())
        screen = CellScreen(16, 60, ["]", "]", "[", "\x1b"])
        with BrowserLoop(screen):
            self.assertIsNone(run_browser(screen, profile, "", load_keys(None)))

    def test_search_accept_and_insertion_preserve_surrounding_buffer_and_cursor(self):
        profile = self.profiles["rsync"]
        before = deepcopy(profile)
        line = 'rsync "café/日本" --bw target'
        point = len('rsync "café/日本" --bw')
        context = find_context(line, point, [profile])
        screen = CellScreen(24, 120, ["/", "\x15", *"bytes/second", "\n", "\n"])
        with BrowserLoop(screen):
            selected = run_browser(screen, profile, "--bw", load_keys(None))
        edited, cursor = insert_option(context, selected)
        self.assertEqual(edited, 'rsync "café/日本" --bwlimit= target')
        self.assertEqual(cursor, len('rsync "café/日本" --bwlimit='))
        self.assertEqual(line, 'rsync "café/日本" --bw target')
        self.assertEqual(profile, before)

    def test_labels_preserve_attached_equals_optional_and_keyword_declarations(self):
        cases = (({"flag": "--size=", "argument": "N"}, "--size=N"),
                 ({"flag": "-o", "argument": "PATH", "argument_style": "attached_only"}, "-oPATH"),
                 ({"flag": "--jobs", "argument": "N", "argument_optional": True}, "--jobs N"),
                 ({"flag": "--mode", "argument": "N", "argument_style": "equals"}, "--mode=N"),
                 ({"flag": "metric", "argument": "N", "kind": "keyword"}, "metric N [keyword]"))
        for option, expected in cases:
            before = deepcopy(option)
            self.assertEqual(option_label(option), expected)
            self.assertEqual(option, before)

    def test_legacy_cross_field_queries_result_order_and_category_selection_are_preserved(self):
        profile = specimen()
        first = first_option(profile)
        del first["value_semantics"]
        second = {"flag": "--other", "summary": "A synthetic selectable value", "detail": "Legacy detail"}
        profile["categories"][0]["options"].append(second)
        profile["categories"].append({"name": "Other", "options": [
            {"flag": "--remote", "summary": "Unique other category", "argument": "INDEX"}]})
        browser = Browser(profile)
        for query in ("--value A synthetic", "selectable value Original useful"):
            browser.set_query(query)
            self.assertEqual(browser.options(), [first])
        browser.set_query("selectable value")
        self.assertEqual(browser.options(), [first, second])
        browser.set_query("INDEX")
        self.assertEqual(browser.category, 1)
        self.assertEqual(browser.options()[0]["flag"], "--remote")

    def test_malformed_preservation_context_does_not_block_legacy_browsing(self):
        for document in (None, [], {"diagnostics": None, "alternatives": 4, "shared": False},
                         {"semantic_sources": [], "diagnostics": [None], "alternatives": ["invalid"], "shared": [42]}):
            profile = specimen(documentation=document)
            # documentation belongs to the profile, not the option declaration.
            profile["documentation"] = first_option(profile).pop("documentation")
            browser = Browser(profile)
            self.assertIn("Original useful prose", " ".join(browser.text(first_option(profile)).details))

    def test_formatter_presentation_preserves_reference_mode_and_semicolon_meanings(self):
        node = synthetic_node("duration", meaning="Wait; an explicit purpose qualification")
        metadata = contract(node)
        reference = format_value_semantics(metadata)
        self.assertTrue(reference[0].startswith("Value: Wait; an explicit purpose qualification; bare numbers: seconds"))
        formatted = format_value_semantics(metadata, presentation=True)
        self.assertIn("bare numbers: seconds; Wait; an explicit purpose qualification", formatted[0])
        self.assertTrue(formatted[1].startswith("Applies to:"))
        self.assertIn("Reference:", " ".join(formatted))
        self.assertEqual(format_value_semantics(metadata), reference)

    def test_partial_provenance_is_honest_and_nonnumerical_content_needs_no_unit(self):
        for references in (None, [{"source": "synthetic:partial", "note": "Locator still requires investigation"}],
                           [{"locator": "Missing source in a partial draft"}]):
            node = synthetic_node(review={"status": "source_derived", "references": references})
            lines = format_value_semantics(contract(node), presentation=True)
            self.assertIn("source derived", lines[0])
            self.assertIn("bytes", lines[0])
            if references:
                self.assertIn("not documented", " ".join(lines))
        node = synthetic_node("nonnumerical", meaning="Select a named configuration file",
                              bare={"state": "not_applicable", "reason": "A path is not a numerical magnitude"},
                              forms=[{"id": "path", "notation": "expression", "syntax": "PATH",
                                      "grammar": "A literal file path"}])
        profile = specimen(node)
        view = Browser(profile).text(first_option(profile))
        self.assertNotIn("guidance unavailable", view.compact)
        self.assertNotIn("unit/scale", " ".join(view.details))

    def test_custom_details_keys_and_scripted_resize_keep_existing_controls(self):
        profile = specimen(synthetic_node("duration"))
        keys = load_keys(None)
        keys["detail_up"], keys["detail_down"] = ["u"], ["d"]
        screen = CellScreen(16, 60, ["d", "d", "u", "\n"])
        with BrowserLoop(screen):
            selected = run_browser(screen, profile, "", keys)
        self.assertIs(selected, first_option(profile))
        self.assertIn("u/d scroll", screen.text())
        self.assertIn("Details 2-", screen.text())

        class ResizingScreen(CellScreen):
            """Replay a resize without a terminal, signal or launched process."""

            def get_wch(self):
                key = super().get_wch()
                if key == ui.curses.KEY_RESIZE:
                    self.lines, self.columns = 16, 60
                return key

        screen = ResizingScreen(24, 120, [ui.curses.KEY_RESIZE, "]", "\n"])
        with BrowserLoop(screen), patch.object(ui.os, "get_terminal_size", side_effect=lambda fd: type(
                "Size", (), {"lines": screen.lines, "columns": screen.columns})()):
            self.assertIs(run_browser(screen, profile, "", load_keys(None)), first_option(profile))
        self.assertIn("Details 2-", screen.text())

    def test_derived_views_require_no_file_network_process_or_evaluation_access(self):
        profile = specimen()
        before = deepcopy(profile)
        with ExitStack() as stack:
            for target in ("builtins.open", "builtins.eval", "builtins.exec", "pathlib.Path.open",
                           "pathlib.Path.write_text", "pathlib.Path.write_bytes"):
                stack.enter_context(patch(target, side_effect=AssertionError("Unexpected presentation side effect")))
            browser = Browser(profile)
            for query in ("seconds", "$(touch marker)", "`bad`", "MAGNITUDE"):
                browser.set_query(query)
                draw(CellScreen(16, 60), browser, load_keys(None))
        self.assertEqual(profile, before)


if __name__ == "__main__":
    unittest.main()
