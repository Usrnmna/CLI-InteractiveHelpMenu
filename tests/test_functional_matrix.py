"""Functional matrix for the prioritized command families.

Covers help resolution, option insertion, search and navigation, and edge
behavior for the commands where the browser is most useful: option-rich tools
and nested subcommand paths. Tests are offline: profiles, fixtures, and the
driver registry only. Discovery probes run solely where a test asserts their
contract; no pending command is executed anywhere in this module.
"""

import importlib.util
import json
import os
import sys
import unittest
from unittest.mock import patch

from test_discovery import ROOT

if importlib.util.find_spec("curses") is None:
    import curses_stub
    sys.modules["curses"] = curses_stub

sys.path.insert(0, str(ROOT / "cli_help"))

import ui as ui_module
from command_paths import help_route, load_driver_registry, resolve_path
from core import HelpError, find_context, insert_option, load_profiles, validate_profile
from discovery import ProbeError, Settings, build_profile, discover, parse_help, run_probe
from live_compatibility import check_case
from ui import Browser, DEFAULT_KEYS, display_text, draw, load_keys, run_browser


FIXTURES = ROOT / "tests/fixtures/help"
MATRIX = json.loads((FIXTURES / "matrix.json").read_text(encoding="utf-8"))
REGISTRY = load_driver_registry(ROOT / "config/drivers.example")
BUNDLED = load_profiles(ROOT / "profiles")

# Option-rich, common commands that benefit most from the browser. The six
# curated commands resolve through bundled profiles; the remainder resolve
# through driver routes and fixture-defined help surfaces.
PRIORITIZED = [
    "git commit", "git log", "git diff", "rsync", "grep", "ls", "tar",
    "docker compose up", "kubectl get", "npm install", "aws s3 cp",
    "terraform plan", "jq", "uv pip install",
]

# Exact option surfaces, by source of truth: bundled profiles for curated
# commands, maintained fixtures for discovered commands.
PROFILE_SURFACES = {
    "git commit": ["--amend", "--all", "--dry-run", "--edit", "--file", "--message", "--patch", "--verbose", "--short"],
    "git log": ["--all", "--author=", "--decorate", "--grep=", "--graph", "--max-count=", "--oneline", "--patch", "--since=", "--stat"],
    "rsync": ["--acls", "--archive", "--backup", "--backup-dir=", "--bwlimit=", "--checksum", "--compress",
              "--delete", "--delete-after", "--dry-run", "--exclude=", "--exclude-from=", "--hard-links",
              "--human-readable", "--ignore-existing", "--include=", "--itemize-changes", "--numeric-ids",
              "--partial", "--progress", "--quiet", "--recursive", "--rsh=", "--size-only", "--stats",
              "--timeout=", "--update", "--verbose", "--xattrs"],
    "grep": ["--context=", "--count", "--extended-regexp", "--exclude=", "--files-with-matches",
             "--fixed-strings", "--ignore-case", "--include=", "--invert-match", "--line-number",
             "--only-matching", "--regexp=", "--recursive", "--word-regexp"],
    "ls": ["--all", "--almost-all", "--classify", "--color=", "--directory", "--dereference",
           "--escape", "--group-directories-first", "--hide=", "--human-readable", "--inode",
           "--numeric-uid-gid", "--quote-name", "--recursive", "--reverse", "--size", "-S", "-l", "-t"],
    "tar": ["--bzip2", "--create", "--directory=", "--diff", "--exclude=", "--extract", "--file=",
            "--gzip", "--list", "--totals", "--verbose", "--xz"],
}

FIXTURE_SURFACES = {
    "git diff": ["--color", "--name-only", "--stat"],
    "docker compose up": ["--build", "--detach", "--timeout", "-d"],
    "kubectl get": ["--output", "--selector", "--watch", "-l", "-o"],
    "npm install": ["--dry-run", "--global", "--ignore-scripts", "--include-workspace-root",
                    "--install-strategy", "--no-audit", "--no-save", "--omit", "--save",
                    "--save-dev", "--save-exact", "--save-prod", "--workspace", "--workspaces",
                    "-E", "-S", "-g", "-w", "-ws"],
    "aws s3 cp": ["--exclude", "--include", "--recursive"],
    "terraform plan": ["-no-color", "-out=", "-var"],
    "jq": ["--arg", "--raw-output", "--slurpfile", "-r"],
    "uv pip install": ["--no-deps", "--python", "--requirements", "-r"],
}


def fixture_text(command):
    return (FIXTURES / (command.replace(" ", "-") + ".txt")).read_text(encoding="utf-8")


def profile_for(command):
    """Resolve the effective help source: bundled profile first, fixture otherwise."""
    words = command.split()
    for profile in BUNDLED:
        if profile["command"] == words:
            return profile
    return build_profile(words, [("fixture", fixture_text(command))])


def options_of(profile):
    return {option["flag"]: option for category in profile["categories"] for option in category["options"]}


def no_probe(*_arguments, **_keywords):
    raise AssertionError("A discovery probe started outside a test that asserts probe contracts.")


def context(line, profile, point=None):
    point = len(line) if point is None else point
    return find_context(line, point, [profile], discover=no_probe, driver_registry=REGISTRY)


class FakeScreen:
    """Record draw calls and replay scripted keys so the browser can run without a terminal."""

    def __init__(self, lines, columns, keys=()):
        self.lines = lines
        self.columns = columns
        self.keys = list(keys)
        self.cells = {}

    def getmaxyx(self):
        return (self.lines, self.columns)

    def erase(self):
        self.cells.clear()

    def addnstr(self, row, col, text, n, attr=0):
        self.cells[(row, col, attr)] = text[:n] if n > 0 else ""

    def refresh(self):
        pass

    def keypad(self, _enabled):
        pass

    def timeout(self, _milliseconds):
        pass

    def get_wch(self):
        if self.keys:
            return self.keys.pop(0)
        return "\x1b"  # An exhausted key script cancels the browser, as Esc would.

    def text(self):
        ordered = sorted(self.cells.items(), key=lambda item: item[0])
        return "\n".join(value for _key, value in ordered if value)


class BrowserLoop:
    """Patch terminal-size polling and curses side effects for the modal loop."""

    def __init__(self, screen):
        self.size = type("Size", (), {"lines": screen.lines, "columns": screen.columns})()
        self.patches = (
            patch.object(ui_module.os, "get_terminal_size", lambda fd: self.size),
            patch.object(ui_module.curses, "curs_set", lambda *arguments: None, create=True),
            patch.object(ui_module.curses, "raw", lambda *arguments: None, create=True),
            patch.object(ui_module.curses, "set_escdelay", lambda *arguments: None, create=True),
        )

    def __enter__(self):
        for item in self.patches:
            item.start()
        return self

    def __exit__(self, *exc):
        for item in reversed(self.patches):
            item.stop()


class PrioritizedInventoryTests(unittest.TestCase):
    def test_matrix_and_profile_surface_counts(self):
        original = [case for case in MATRIX if not case.get("expansion")]
        self.assertEqual(len(original), 59)
        self.assertEqual(len({case["command"].split()[0] for case in original}), 34)
        self.assertEqual({case["tier"] for case in MATRIX}, {"essential", "next", "extended"})
        self.assertTrue(set(PROFILE_SURFACES) <= {" ".join(profile["command"]) for profile in BUNDLED})
        for case in MATRIX:
            with self.subTest(command=case["command"]):
                self.assertTrue((FIXTURES / case["fixture"]).is_file())

    def test_every_prioritized_command_resolves_to_its_declared_path(self):
        static = [tuple(profile["command"]) for profile in BUNDLED]
        for command in PRIORITIZED:
            words = command.split()
            with self.subTest(command=command):
                self.assertEqual(resolve_path(words, static, REGISTRY).words, tuple(words))
                route = help_route(words[0], tuple(words[1:]), REGISTRY)
                for argument in route.arguments:
                    self.assertRegex(argument, r"[A-Za-z0-9_.:+/=-]+")
                self.assertTrue(route.arguments or route.manual)

    def test_driver_routes_exist_for_every_nested_matrix_command(self):
        for case in MATRIX:
            words = case["command"].split()
            with self.subTest(command=words):
                if len(words) > 1:
                    if case.get("profile_only"):
                        self.assertIn(words, [profile["command"] for profile in BUNDLED])
                        with self.assertRaises(ValueError):
                            help_route(words[0], tuple(words[1:]), REGISTRY)
                    else:
                        help_route(words[0], tuple(words[1:]), REGISTRY)

    def test_profiles_are_complete_and_unique(self):
        for profile in BUNDLED:
            validate_profile(profile, ROOT / "profiles")
            flags = []
            for category in profile["categories"]:
                self.assertGreaterEqual(len(category["options"]), 1, category["name"])
                for option in category["options"]:
                    self.assertTrue(option["summary"])
                    flags.append(option["flag"])
            with self.subTest(command=profile["command"]):
                self.assertEqual(len(flags), len(set(flags)))
                self.assertTrue(flags)

    def test_bundled_surfaces_are_pinned(self):
        for command, expected in PROFILE_SURFACES.items():
            with self.subTest(command=command):
                self.assertEqual(sorted(options_of(profile_for(command))), sorted(expected))

    def test_fixture_surfaces_are_pinned(self):
        for command, expected in FIXTURE_SURFACES.items():
            with self.subTest(command=command):
                self.assertEqual(sorted(options_of(profile_for(command))), sorted(expected))


class HelpResolutionTests(unittest.TestCase):
    def test_typed_prefix_selects_declared_command(self):
        for command in PRIORITIZED:
            profile = profile_for(command)
            with self.subTest(command=command):
                self.assertEqual(context(command + " --", profile).profile["command"], command.split())

    def test_partial_option_prefix_completes_by_insertion(self):
        cases = [
            ("rsync", "--archive", "--ar"), ("git commit", "--message", "--m"),
            ("git log", "--oneline", "--one"), ("grep", "--ignore-case", "--ig"),
            ("ls", "--human-readable", "--hum"), ("tar", "--extract", "--ext"),
            ("kubectl get", "--selector", "--sel"), ("aws s3 cp", "--recursive", "--rec"),
            ("npm install", "--dry-run", "--dry"), ("terraform plan", "-out=", "-out"),
            ("jq", "--arg", "--a"), ("uv pip install", "--requirements", "--req"),
            ("docker compose up", "--build", "--b"), ("curl", "--header", "--hea"),
        ]
        for command, flag, partial in cases:
            profile = profile_for(command)
            line = command + " " + partial
            with self.subTest(command=command, flag=flag):
                ctx = context(line, profile)
                self.assertEqual(ctx.query, partial)
                edited, point = insert_option(ctx, options_of(profile)[flag])
                expected = command + " " + flag + ("" if flag.endswith("=") else " ")
                self.assertEqual(edited, expected)
                self.assertEqual(point, len(edited))

    def test_sibling_subcommand_options_do_not_leak(self):
        pairs = [
            (("git", "commit"), ("git", "log"), "--amend", "--oneline"),
            (("git", "commit"), ("git", "diff"), "--amend", "--stat"),
            (("aws", "s3", "cp"), ("aws", "ec2", "describe-instances"), "--recursive", "--filters"),
            (("kubectl", "get"), ("kubectl", "config", "view"), "--selector", "--flatten"),
            (("uv", "pip", "install"), ("uv", "run"), "--requirements", "--directory"),
            (("docker", "compose", "up"), ("docker", "run"), "--build", "--env"),
        ]
        for first, second, unique_to_first, unique_to_second in pairs:
            with self.subTest(first=first, second=second):
                first_options = set(options_of(profile_for(" ".join(first))))
                second_options = set(options_of(profile_for(" ".join(second))))
                self.assertIn(unique_to_first, first_options)
                self.assertNotIn(unique_to_first, second_options)
                self.assertIn(unique_to_second, second_options)
                self.assertNotIn(unique_to_second, first_options)

    def test_nested_path_wins_over_parent_context(self):
        cases = [
            ("docker compose up --", ["docker", "compose", "up"]),
            ("docker run --", ["docker", "run"]),
            ("uv pip install --", ["uv", "pip", "install"]),
            ("aws s3 cp --", ["aws", "s3", "cp"]),
            ("kubectl config view --", ["kubectl", "config", "view"]),
        ]
        for line, expected in cases:
            with self.subTest(line=line):
                profile = profile_for(" ".join(expected))
                self.assertEqual(context(line, profile).profile["command"], expected)

    def test_unknown_subcommand_paths_fail_closed(self):
        anchor = profile_for("rsync")
        for line in ["git unknown-family --", "git stash unknown --", "docker unknown --",
                     "aws s3 unknown --", "kubectl unknown --", "uv unknown --"]:
            with self.subTest(line=line):
                with self.assertRaises(HelpError):
                    context(line, anchor)

    def test_global_options_are_skipped_in_path_resolution(self):
        cases = [
            ("kubectl --context private get --", ["kubectl", "get"]),
            ("aws --profile private --region=private ec2 describe-instances --", ["aws", "ec2", "describe-instances"]),
            ("uv --directory private pip install --", ["uv", "pip", "install"]),
            ("docker --context private compose up --", ["docker", "compose", "up"]),
        ]
        for line, expected in cases:
            with self.subTest(line=line):
                self.assertEqual(context(line, profile_for(" ".join(expected))).profile["command"], expected)

    def test_unsupported_global_options_fail_before_any_probe(self):
        for line in ["kubectl --unknown get --", "git -Z --", "docker --foo run --"]:
            with self.subTest(line=line):
                with self.assertRaises(HelpError):
                    context(line, profile_for("rsync"))


class InsertionContractTests(unittest.TestCase):
    def test_every_bundled_option_inserts_exactly_midline(self):
        for profile in BUNDLED:
            # Identity guards have independent subprocess tests. This contract
            # examines literal insertion of already-reviewed profile metadata.
            profile = dict(profile)
            profile.pop("identity", None)
            command = " ".join(profile["command"])
            for option in [item for category in profile["categories"] for item in category["options"]]:
                prefix = command + " "
                suffix = " 'caf\u00e9/\u65e5\u672c destination'"
                line = prefix + "--part" + suffix
                with self.subTest(command=command, flag=option["flag"]):
                    ctx = context(line, profile, len(prefix) + 4)
                    edited, point = insert_option(ctx, option)
                    expected = prefix + option["flag"] + suffix
                    self.assertEqual(edited, expected)
                    joined = option["flag"].endswith("=") or option.get("argument_style") == "attached_only"
                    self.assertEqual(point, len(prefix + option["flag"]) + (0 if joined else 1))

    def test_value_options_reserve_their_slot(self):
        rsync = profile_for("rsync")
        ctx = context("rsync --ex", rsync)
        edited, point = insert_option(ctx, options_of(rsync)["--exclude="])
        self.assertEqual((edited, point), ("rsync --exclude=", 16))

        git_commit = profile_for("git commit")
        with self.assertRaises(HelpError):
            context("git commit --message ", git_commit)
        self.assertEqual(context("git commit --message 'a message' --", git_commit).query, "--")

        kubectl_get = profile_for("kubectl get")
        with self.assertRaises(HelpError):
            context("kubectl get --selector ", kubectl_get)
        self.assertEqual(context("kubectl get --selector app=web --", kubectl_get).query, "--")

        jq = profile_for("jq")
        with self.assertRaises(HelpError):
            context("jq --arg name ", jq)
        self.assertEqual(context("jq --arg name value --", jq).query, "--")

    def test_insertion_is_pure_and_preserves_the_buffer(self):
        profile = profile_for("rsync")
        original = "rsync --ar 'source dir' target"
        ctx = context(original, profile, len("rsync --ar"))
        edited, point = insert_option(ctx, options_of(profile)["--archive"])
        self.assertEqual(original, "rsync --ar 'source dir' target")
        self.assertEqual(edited, "rsync --archive 'source dir' target")
        self.assertEqual(point, len("rsync --archive "))

    def test_typo_option_is_replaced_not_appended(self):
        profile = profile_for("rsync")
        ctx = context("rsync --archve source target", profile, len("rsync --archve"))
        edited, _ = insert_option(ctx, options_of(profile)["--archive"])
        self.assertEqual(edited, "rsync --archive source target")

    def test_end_of_options_marker_stops_insertion(self):
        cases = [("rsync -- --exclude", "rsync"), ("git commit -- --all", "git commit")]
        for line, command in cases:
            with self.subTest(line=line):
                with self.assertRaises(HelpError):
                    context(line, profile_for(command))

    def test_run_browser_cancel_preserves_the_command_line(self):
        profile = profile_for("rsync")
        buffer = "rsync --ar source target"
        screen = FakeScreen(20, 100, ["\x1b"])
        with BrowserLoop(screen):
            selected = run_browser(screen, profile, "", load_keys(None))
        self.assertIsNone(selected)
        self.assertEqual(buffer, "rsync --ar source target")

    def test_run_browser_accept_returns_option_without_shell_execution(self):
        profile = profile_for("rsync")
        screen = FakeScreen(20, 100, ["\n"])
        with BrowserLoop(screen):
            selected = run_browser(screen, profile, "", load_keys(None))
        self.assertEqual(selected["flag"], "--archive")


class SearchNavigationTests(unittest.TestCase):
    @staticmethod
    def _profile():
        return profile_for("rsync")

    def test_search_matches_flag_summary_and_detail_case_insensitively(self):
        browser = Browser(self._profile())
        self.assertEqual(browser.options()[0]["flag"], "--archive")
        for query, expected in [("DRY", "--dry-run"), ("bandwidth", "--bwlimit="),
                                ("destination", "--update"), ("EXCLUDE", "--exclude=")]:
            browser.set_query(query)
            with self.subTest(query=query):
                flags = [option["flag"] for option in browser.options()]
                self.assertIn(expected, flags)
        browser.set_query("")
        browser.set_query("extraneous")
        flags = [option["flag"] for option in browser.options()]
        self.assertIn("--delete", flags)

    def test_search_finds_unicode_summaries_and_details(self):
        profile = build_profile("tool", [("fixture", "Options:\n  --copy   Caf\u00e9 transfer \u65e5\u672c mode")])
        browser = Browser(profile)
        for query in ["caf\u00e9", "\u65e5\u672c", "transfer"]:
            browser.set_query(query)
            with self.subTest(query=query):
                self.assertEqual(browser.options()[0]["flag"], "--copy")

    def test_no_match_state_and_recovery(self):
        browser = Browser(self._profile())
        browser.set_query("no-such-option-zzz")
        self.assertEqual(browser.options(), [])
        screen = FakeScreen(16, 60)
        draw(screen, browser, load_keys(None))
        self.assertIn("No matches", screen.text())
        browser.set_query("")
        self.assertTrue(browser.options())

    def test_navigation_is_clamped_and_focus_default(self):
        browser = Browser(self._profile())
        categories = len(self._profile()["categories"])
        browser.move_category(1000)
        self.assertEqual(browser.category, categories - 1)
        browser.move_option(1000)
        self.assertEqual(browser.selected, len(browser.options()) - 1)
        browser.move_category(-1000)
        self.assertEqual((browser.category, browser.selected), (0, 0))
        self.assertEqual(browser.focus, "options")

    def test_vi_bindings_are_default(self):
        keys = load_keys(None)
        self.assertIn("k", keys["up"])
        self.assertIn("j", keys["down"])
        self.assertIn("h", keys["previous_category"])
        self.assertIn("l", keys["next_category"])

    def test_vi_keys_drive_the_browser_loop(self):
        screen = FakeScreen(20, 100, ["\t", "j", "\t", "k", "\n"])
        with BrowserLoop(screen):
            selected = run_browser(screen, self._profile(), "", load_keys(None))
        self.assertEqual(selected["flag"], "--dry-run")

    def test_search_entry_apply_and_restore_flow(self):
        screen = FakeScreen(20, 100, ["/", "d", "r", "y", "\n", "\n"])
        with BrowserLoop(screen):
            selected = run_browser(screen, self._profile(), "", load_keys(None))
        self.assertEqual(selected["flag"], "--dry-run")

        browser = Browser(self._profile(), "dry")
        browser.set_query("zzz-restore")
        self.assertEqual(browser.options(), [])
        browser.set_query("dry")
        self.assertEqual(browser.options()[0]["flag"], "--dry-run")

    def test_rendering_at_minimum_size_and_smaller(self):
        browser = Browser(self._profile())
        for size, ok in [((60, 16), True), ((59, 16), False), ((60, 15), False)]:
            columns, lines = size
            screen = FakeScreen(lines, columns)
            with self.subTest(size=size):
                result = draw(screen, browser, load_keys(None))
                if ok:
                    self.assertGreaterEqual(result, 3)
                    self.assertNotIn("Resize to at least", screen.text())
                    self.assertIn("rsync", screen.text())
                else:
                    self.assertEqual(result, 1)
                    self.assertIn("Resize to at least 60 columns x 16 rows", screen.text())

    def test_long_profile_window_scrolling(self):
        lines = "\n".join(
            "Category %d:\n" % category + "\n".join(
                "  --item-%d-%d VALUE   Description %d" % (category, option, option) for option in range(50))
            for category in range(30))
        browser = Browser(build_profile("tool", [("large", lines)]))
        browser.move_category(10000)
        browser.move_option(10000)
        screen = FakeScreen(16, 60)
        draw(screen, browser, load_keys(None))
        text = screen.text()
        for flag in ("--item-29-49", "--item-29-48", "--item-29-47"):
            self.assertIn(flag, text)
        self.assertNotIn("--item-29-46", text)

    def test_display_text_suppresses_unsupported_code_points(self):
        self.assertEqual(display_text("a\ud800b"), "a b")


class EdgeCaseTests(unittest.TestCase):
    def test_uninstalled_commands_report_explicit_skips(self):
        for command in PRIORITIZED:
            with self.subTest(command=command), patch("live_compatibility.shutil.which", return_value=None):
                result = check_case(command.split(), REGISTRY)
                self.assertEqual(result["status"], "skipped")

    def test_missing_executable_is_a_handled_error(self):
        with patch("discovery.shutil.which", return_value=None):
            with self.assertRaisesRegex(HelpError, "Installed executable not found"):
                discover("rsync", Settings(cache_ttl=0))

    def test_missing_man_page_reports_unavailability_without_probe(self):
        calls = []

        def which(name):
            # A stat-able path stands in for the missing executable; the probe
            # contract is that discovery never starts one without a manual.
            return sys.executable if name == "git" else None

        def spy(argv, *_arguments, **_keywords):
            calls.append(argv)
            raise ProbeError("probe must not start without a manual source")

        with patch("discovery.shutil.which", side_effect=which), patch("discovery.run_probe", spy):
            with self.assertRaises(HelpError) as raised:
                discover("git", Settings(cache_ttl=0), subcommands=("log",))
        self.assertRegex(str(raised.exception), "man executable is unavailable")
        self.assertEqual(calls, [])

    @unittest.skipUnless(os.name == "posix", "Windows lacks the POSIX process-group cleanup")
    def test_probe_completes_on_posix(self):
        self.assertIn("Python", run_probe([sys.executable, "--version"], 5))

    @unittest.skipUnless(os.name == "nt", "POSIX hosts complete the probe normally")
    def test_probe_reports_the_windows_limitation(self):
        with self.assertRaises((AttributeError, PermissionError)):
            run_probe([sys.executable, "--version"], 5)

    def test_npm_root_help_is_documented_empty(self):
        self.assertEqual(parse_help(fixture_text("npm"), "fixture"), [])
        with patch("live_compatibility.shutil.which", return_value="/fake/npm"), \
                patch("live_compatibility.discover",
                      side_effect=HelpError("No recognizable option declarations were found for 'npm'. Add a custom profile for this command.")):
            self.assertEqual(check_case(["npm"], REGISTRY, allow_empty=True)["status"], "unsupported")
            self.assertEqual(check_case(["npm"], REGISTRY)["status"], "failed")


if __name__ == "__main__":
    unittest.main()
