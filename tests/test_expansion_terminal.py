"""Rendered cells and cursor evidence for prefix and structured insertion."""

import json
import shlex
import sys
import unittest

from test_terminal_screen import TerminalTestCase, TMUX_AVAILABLE, PROMPT, HISTORY, ROOT

sys.path.insert(0, str(ROOT / "cli_help"))


@unittest.skipUnless(TMUX_AVAILABLE, "Rendered-screen tests require Linux and tmux")
class ExpansionScreenTests(TerminalTestCase):
    def test_podman_build_pull_policy_at_minimum_size(self):
        """Find the version caveat and enter a pull policy before the build context."""
        shell = self.start()
        shell.text("podman() { printf executed > " + shlex.quote(str(shell.executed)) + "; }")
        shell.keys("Enter")
        shell.wait_for(lambda state: state.cells[state.y] == PROMPT.rstrip())
        prefix, suffix = "podman build ", " ./context"
        shell.resize(60, 16)
        shell.text(prefix + suffix)
        shell.keys(*(["Left"] * len(suffix)))
        for action in ("Escape", "Enter"):
            shell.open_menu()
            shell.keys("/")
            shell.text("local images only")
            shell.keys("Enter")
            found = shell.wait_for(lambda state: state.cells[2] == "Filter: local images only")
            self.assertIn("> --pull=POLICY", found.cells[4])
            shell.find_detail("clients treat newer as missing.")
            shell.cancel(action)
            if action == "Escape":
                self.assertEqual(shell.read_buffer(), (prefix + suffix, len(prefix)))
        self.assertEqual(shell.read_buffer(), (prefix + "--pull=" + suffix, len(prefix + "--pull=")))
        shell.text("never")
        self.assertEqual(shell.read_buffer(), (prefix + "--pull=never" + suffix, len(prefix + "--pull=never")))
        self.assertFalse(shell.executed.exists())

    def test_bun_watch_working_directory_at_minimum_size(self):
        """Find the restart caveat and insert --cwd ahead of the script name."""
        shell = self.start()
        shell.text("bun() { printf executed > " + shlex.quote(str(shell.executed)) + "; }")
        shell.keys("Enter")
        shell.wait_for(lambda state: state.cells[state.y] == PROMPT.rstrip())
        prefix, suffix = "bun run --watch ", " ./app.ts"
        shell.resize(60, 16)
        shell.text(prefix + suffix)
        shell.keys(*(["Left"] * len(suffix)))
        for action in ("Escape", "Enter"):
            shell.open_menu()
            shell.keys("/")
            shell.text("absolute path")
            shell.keys("Enter")
            found = shell.wait_for(lambda state: state.cells[2] == "Filter: absolute path")
            self.assertIn("> --cwd DIRECTORY", found.cells[4])
            shell.find_detail("restart can find the directory again.")
            shell.cancel(action)
            if action == "Escape":
                self.assertEqual(shell.read_buffer(), (prefix + suffix, len(prefix)))
        self.assertEqual(shell.read_buffer(), (prefix + "--cwd" + suffix, len(prefix + "--cwd ")))
        self.assertFalse(shell.executed.exists())

    def test_dotnet_restore_http_cache_at_minimum_size(self):
        """Find the hidden restore spelling and its global packages behavior at 60×16."""
        shell = self.start()
        shell.text("dotnet() { printf executed > " + shlex.quote(str(shell.executed)) + "; }")
        shell.keys("Enter")
        shell.wait_for(lambda state: state.cells[state.y] == PROMPT.rstrip())
        prefix, suffix = "dotnet restore ", " Sample.csproj"
        shell.resize(60, 16)
        shell.text(prefix + suffix)
        shell.keys(*(["Left"] * len(suffix)))
        for action in ("Escape", "Enter"):
            shell.open_menu()
            shell.keys("/")
            shell.text("--no-http-cache")
            shell.keys("Enter")
            found = shell.wait_for(lambda state: state.cells[2] == "Filter: --no-http-cache")
            self.assertIn("> --no-cache", found.cells[4])
            shell.find_detail("from the global packages folder.")
            shell.cancel(action)
            if action == "Escape":
                self.assertEqual(shell.read_buffer(), (prefix + suffix, len(prefix)))
        self.assertEqual(shell.read_buffer(), (prefix + "--no-cache" + suffix, len(prefix + "--no-cache ")))
        self.assertFalse(shell.executed.exists())

    def test_go_tidy_diff_version_at_minimum_size(self):
        """Find the read-only preview and its Go version requirement at 60×16."""
        shell = self.start()
        shell.text("go() { printf executed > " + shlex.quote(str(shell.executed)) + "; }")
        shell.keys("Enter")
        shell.wait_for(lambda state: state.cells[state.y] == PROMPT.rstrip())
        prefix, suffix = "go mod tidy ", " -v"
        shell.resize(60, 16)
        shell.text(prefix + suffix)
        shell.keys(*(["Left"] * len(suffix)))
        for action in ("Escape", "Enter"):
            shell.open_menu()
            shell.keys("/")
            shell.text("unified diff")
            shell.keys("Enter")
            found = shell.wait_for(lambda state: state.cells[2] == "Filter: unified diff")
            self.assertIn("> -diff", found.cells[4])
            shell.find_detail("Go 1.22 rejects this flag.")
            shell.cancel(action)
            if action == "Escape":
                self.assertEqual(shell.read_buffer(), (prefix + suffix, len(prefix)))
        self.assertEqual(shell.read_buffer(), (prefix + "-diff" + suffix, len(prefix + "-diff ")))
        self.assertFalse(shell.executed.exists())

    def test_pytest_basetemp_at_minimum_size(self):
        """Find the cleanup warning and supply a temporary base before a pending test path."""
        shell = self.start()
        shell.text("pytest() { printf executed > " + shlex.quote(str(shell.executed)) + "; }")
        shell.keys("Enter")
        shell.wait_for(lambda state: state.cells[state.y] == PROMPT.rstrip())
        prefix, suffix = "pytest ", " test_sample.py"
        shell.resize(60, 16)
        shell.text(prefix + suffix)
        shell.keys(*(["Left"] * len(suffix)))
        for action in ("Escape", "Enter"):
            shell.open_menu()
            shell.keys("/")
            shell.text("dedicated directory")
            shell.keys("Enter")
            found = shell.wait_for(lambda state: state.cells[2] == "Filter: dedicated directory")
            self.assertIn("> --basetemp DIR", found.cells[4])
            shell.find_detail("recreates the directory.")
            shell.cancel(action)
            if action == "Escape":
                self.assertEqual(shell.read_buffer(), (prefix + suffix, len(prefix)))
        self.assertEqual(shell.read_buffer(), (prefix + "--basetemp" + suffix, len(prefix + "--basetemp ")))
        shell.text("scratch ")
        self.assertEqual(shell.read_buffer(), (prefix + "--basetemp scratch" + suffix, len(prefix + "--basetemp scratch ")))
        self.assertFalse(shell.executed.exists())

    def test_ruff_check_diff_exit_status_at_minimum_size(self):
        """Find the fix-only exit rule and insert --diff before a pending filename."""
        shell = self.start()
        shell.text("ruff() { printf executed > " + shlex.quote(str(shell.executed)) + "; }")
        shell.keys("Enter")
        shell.wait_for(lambda state: state.cells[state.y] == PROMPT.rstrip())
        prefix, suffix = "ruff check ", " sample.py"
        shell.resize(60, 16)
        shell.text(prefix + suffix)
        shell.keys(*(["Left"] * len(suffix)))
        for action in ("Escape", "Enter"):
            shell.open_menu()
            shell.keys("/")
            shell.text("unfixable violation")
            shell.keys("Enter")
            found = shell.wait_for(lambda state: state.cells[2] == "Filter: unfixable violation")
            self.assertIn("> --diff", found.cells[4])
            shell.find_detail("produces no diff and exits 0.")
            shell.cancel(action)
            if action == "Escape":
                self.assertEqual(shell.read_buffer(), (prefix + suffix, len(prefix)))
        self.assertEqual(shell.read_buffer(), (prefix + "--diff" + suffix, len(prefix + "--diff ")))
        self.assertFalse(shell.executed.exists())

    def test_uv_sync_frozen_explains_stale_lock_at_minimum_size(self):
        """Find the stale-lock warning and insert the flag before an existing extra."""
        shell = self.start()
        shell.text("uv() { printf executed > " + shlex.quote(str(shell.executed)) + "; }")
        shell.keys("Enter")
        shell.wait_for(lambda state: state.cells[state.y] == PROMPT.rstrip())
        prefix, suffix = "uv sync ", " --extra docs"
        shell.resize(60, 16)
        shell.text(prefix + suffix)
        shell.keys(*(["Left"] * len(suffix)))
        for action in ("Escape", "Enter"):
            shell.open_menu()
            shell.keys("/")
            shell.text("skip the freshness check")
            shell.keys("Enter")
            found = shell.wait_for(lambda state: state.cells[2] == "Filter: skip the freshness check")
            self.assertIn("> --frozen", found.cells[4])
            shell.find_detail("A missing lockfile is an error.")
            shell.cancel(action)
            if action == "Escape":
                self.assertEqual(shell.read_buffer(), (prefix + suffix, len(prefix)))
        self.assertEqual(shell.read_buffer(), (prefix + "--frozen" + suffix, len(prefix + "--frozen ")))
        self.assertFalse(shell.executed.exists())

    def test_openssl_client_verification_depth_at_minimum_size(self):
        """Find the chain-limit distinction and insert the client depth before a suffix."""
        shell = self.start()
        shell.text("openssl() { printf executed > " + shlex.quote(str(shell.executed)) + "; }")
        shell.keys("Enter")
        shell.wait_for(lambda state: state.cells[state.y] == PROMPT.rstrip())
        prefix, suffix = "openssl s_client ", " -showcerts"
        shell.text(prefix + suffix)
        shell.keys(*(["Left"] * len(suffix)))
        shell.resize(60, 16)
        for key in ("Escape", "Enter"):
            shell.open_menu()
            shell.keys("/")
            shell.text("to limit intermediate")
            shell.keys("Enter")
            found = shell.wait_for(lambda state: state.cells[2] == "Filter: to limit intermediate")
            self.assertIn("> -verify DEPTH", found.cells[4])
            shell.find_detail("-verify_return_error to stop on errors.")
            shell.cancel(key)
            if key == "Escape":
                self.assertEqual(shell.read_buffer(), (prefix + suffix, len(prefix)))
        self.assertEqual(shell.read_buffer(), (prefix + "-verify" + suffix, len(prefix + "-verify ")))
        shell.text("2 ")
        self.assertEqual(shell.read_buffer(), (prefix + "-verify 2" + suffix, len(prefix + "-verify 2 ")))
        self.assertFalse(shell.executed.exists())

    def test_journalctl_boot_offset_before_existing_filter(self):
        """Reach the version-specific boot rule and fill its joined value at 60×16."""
        shell = self.start()
        shell.text("journalctl() { printf executed > " + shlex.quote(str(shell.executed)) + "; }")
        shell.keys("Enter")
        shell.wait_for(lambda state: state.cells[state.y] == PROMPT.rstrip())
        prefix, suffix = "journalctl ", " --no-pager"
        shell.text(prefix + suffix)
        shell.keys(*(["Left"] * len(suffix)))
        shell.resize(60, 16)
        for key in ("Escape", "Enter"):
            shell.open_menu()
            shell.keys("/")
            shell.text("ignores the offset")
            shell.keys("Enter")
            found = shell.wait_for(lambda state: state.cells[2] == "Filter: ignores the offset")
            self.assertIn("> --boot=ID", found.cells[4])
            shell.find_detail("ignores the offset in ID+offset.")
            shell.cancel(key)
            if key == "Escape":
                self.assertEqual(shell.read_buffer(), (prefix + suffix, len(prefix)))
        self.assertEqual(shell.read_buffer(), (prefix + "--boot=" + suffix, len(prefix + "--boot=")))
        shell.text("-1")
        self.assertEqual(shell.read_buffer(), (prefix + "--boot=-1" + suffix, len(prefix + "--boot=-1")))
        self.assertFalse(shell.executed.exists())

    def test_ip_route_prefix_modifiers_at_minimum_size(self):
        """Find the routing-table match rule and insert to before an existing filter."""
        shell = self.start()
        shell.text("ip() { printf executed > " + shlex.quote(str(shell.executed)) + "; }")
        shell.keys("Enter")
        shell.wait_for(lambda state: state.cells[state.y] == PROMPT.rstrip())
        prefix, suffix = "ip route show ", " table local"
        shell.text(prefix + suffix)
        shell.keys(*(["Left"] * len(suffix)))
        shell.resize(60, 16)
        for action in ("Escape", "Enter"):
            shell.open_menu()
            shell.keys("/")
            shell.text("covering routes")
            shell.keys("Enter")
            found = shell.wait_for(lambda state: state.cells[2] == "Filter: covering routes")
            self.assertIn("> to PREFIX", found.cells[4])
            shell.find_detail("to match PREFIX to include covering routes.")
            shell.cancel(action)
            if action == "Escape":
                self.assertEqual(shell.read_buffer(), (prefix + suffix, len(prefix)))
        self.assertEqual(shell.read_buffer(), (prefix + "to" + suffix, len(prefix + "to ")))
        self.assertFalse(shell.executed.exists())

    def test_yq_first_file_warning_and_explicit_expression(self):
        """Read the multi-file write rule and insert an expression before two filenames."""
        shell, prefix, suffix, _ = self.pending_yq(60, 16)
        shell.open_menu()
        shell.keys("/")
        shell.text("combined results")
        shell.keys("Enter")
        found = shell.wait_for(lambda state: state.cells[2] == "Filter: combined results")
        self.assertIn("> --inplace", found.cells[4])
        shell.find_detail("Later files keep their original contents.")
        shell.cancel()
        self.assertEqual(shell.read_buffer(), (prefix + suffix, len(prefix)))

        shell.open_menu()
        shell.keys("/")
        shell.text("existing file")
        shell.keys("Enter")
        shell.wait_for(lambda state: "> --expression" in state.cells[4])
        shell.cancel("Enter")
        self.assertEqual(shell.read_buffer(), (prefix + "--expression" + suffix, len(prefix + "--expression ")))
        shell.text("'.items[] | .name' ")
        self.assertEqual(shell.read_buffer(), (prefix + "--expression '.items[] | .name'" + suffix,
                                               len(prefix + "--expression '.items[] | .name' ")))
        self.assertFalse(shell.executed.exists())

    def test_ffmpeg_optional_audio_map_at_minimum_size(self):
        """Reach the input-index rule and insert an optional map before the output."""
        shell = self.start()
        shell.text("ffmpeg() { printf executed > " + shlex.quote(str(shell.executed)) + "; }")
        shell.keys("Enter")
        shell.wait_for(lambda state: state.cells[state.y] == PROMPT.rstrip())
        prefix, suffix = "ffmpeg -i input.mkv ", " output.mkv"
        shell.text(prefix + suffix)
        shell.keys(*(["Left"] * len(suffix)))
        shell.resize(60, 16)
        for action in ("Escape", "Enter"):
            shell.open_menu()
            shell.keys("/")
            shell.text("optional audio")
            shell.keys("Enter")
            found = shell.wait_for(lambda state: state.cells[2] == "Filter: optional audio")
            self.assertIn("> -map", found.cells[4])
            shell.find_detail("The input number must still exist.")
            shell.cancel(action)
            if action == "Escape":
                self.assertEqual(shell.read_buffer(), (prefix + suffix, len(prefix)))
        self.assertEqual(shell.read_buffer(), (prefix + "-map" + suffix, len(prefix + "-map ")))
        shell.text("'0:a?' ")
        self.assertEqual(shell.read_buffer(), (prefix + "-map '0:a?'" + suffix, len(prefix + "-map '0:a?' ")))
        self.assertFalse(shell.executed.exists())

    def test_fzf_literal_dot_delimiter_at_minimum_size(self):
        """Read both delimiter interpretations and insert a portable field separator."""
        shell = self.start()
        shell.text("fzf() { printf executed > " + shlex.quote(str(shell.executed)) + "; }")
        shell.keys("Enter")
        shell.wait_for(lambda state: state.cells[state.y] == PROMPT.rstrip())
        prefix, suffix = "fzf ", " --nth 2"
        shell.text(prefix + suffix)
        shell.keys(*(["Left"] * len(suffix)))
        shell.resize(60, 16)
        for action in ("Escape", "Enter"):
            shell.open_menu()
            shell.keys("/")
            shell.text("literal dot")
            shell.keys("Enter")
            found = shell.wait_for(lambda state: state.cells[2] == "Filter: literal dot")
            self.assertIn("> --delimiter", found.cells[4])
            shell.find_detail("a literal dot in 0.67.0.")
            shell.cancel(action)
            if action == "Escape":
                self.assertEqual(shell.read_buffer(), (prefix + suffix, len(prefix)))
        self.assertEqual(shell.read_buffer(), (prefix + "--delimiter" + suffix, len(prefix + "--delimiter ")))
        shell.text("'[.]' ")
        self.assertEqual(shell.read_buffer(), ("fzf --delimiter '[.]' --nth 2", len("fzf --delimiter '[.]' ")))
        self.assertFalse(shell.executed.exists())

    def test_fd_hidden_directory_guidance_and_midline_exclusion(self):
        """Read the version-specific .git rule and insert an exclusion before a pattern."""
        for command in ("fd", "fdfind"):
            with self.subTest(command=command):
                shell = self.start()
                shell.text(command + "() { printf executed > " + shlex.quote(str(shell.executed)) + "; }")
                shell.keys("Enter")
                shell.wait_for(lambda state: state.cells[state.y] == PROMPT.rstrip())
                prefix, suffix = command + " ", " needle"
                shell.text(prefix + suffix)
                shell.keys(*(["Left"] * len(suffix)))
                shell.resize(60, 16)
                shell.open_menu()
                shell.keys("/")
                shell.text("fd 9.0")
                shell.keys("Enter")
                selected = shell.wait_for(lambda state: state.cells[2] == "Filter: fd 9.0")
                self.assertIn("> --hidden", selected.cells[4])
                shell.find_detail("use --exclude .git to omit it.")
                shell.cancel()
                self.assertEqual(shell.read_buffer(), (prefix + suffix, len(prefix)))

                shell.open_menu()
                shell.keys("/")
                shell.text("quote wildcards")
                shell.keys("Enter")
                selected = shell.wait_for(lambda state: state.cells[2] == "Filter: quote wildcards")
                self.assertIn("> --exclude", selected.cells[4])
                shell.cancel("Enter")
                self.assertEqual(shell.read_buffer(), (prefix + "--exclude" + suffix, len(prefix + "--exclude ")))
                shell.text("'*.log' ")
                self.assertEqual(shell.read_buffer(), (prefix + "--exclude '*.log'" + suffix,
                                                       len(prefix + "--exclude '*.log' ")))
                self.assertFalse(shell.executed.exists())

    def test_commit_preview_and_log_date_filter_at_minimum_size(self):
        """Reach the dry-run and history-walk qualifications before a midline edit."""
        cases = (("git commit", "short status format", "--short", "no commit is created."),
                 ("git log", "committer timestamp", "--since=", "when timestamps are out of order."))
        for command, query, flag, qualification in cases:
            with self.subTest(command=command):
                shell = self.start()
                shell.text("git() { printf executed > " + shlex.quote(str(shell.executed)) + "; }")
                shell.keys("Enter")
                shell.wait_for(lambda state: state.cells[state.y] == PROMPT.rstrip())
                prefix, suffix = command + " ", " -- tracked.txt"
                shell.text(prefix + suffix)
                shell.keys(*(["Left"] * len(suffix)))
                shell.resize(60, 16)
                for action in ("Escape", "Enter"):
                    shell.open_menu()
                    shell.keys("/")
                    shell.text(query)
                    shell.keys("Enter")
                    selected = shell.wait_for(lambda state: state.cells[2] == "Filter: " + query)
                    self.assertIn("> " + flag, selected.cells[4])
                    shell.find_detail(qualification)
                    shell.cancel(action)
                    if action == "Escape":
                        self.assertEqual(shell.read_buffer(), (prefix + suffix, len(prefix)))
                point = len(prefix + flag) + (0 if flag.endswith("=") else 1)
                self.assertEqual(shell.read_buffer(), (prefix + flag + suffix, point))
                self.assertFalse(shell.executed.exists())

    def test_git_stash_count_and_locked_worktree_guidance(self):
        """Find the negative-count and double-force rules before editing a pending command."""
        cases = (("git stash list", "negative count", "--max-count=", "Omit the option for no limit."),
                 ("git worktree remove", "locked worktree", "--force", "requires --force twice."))
        for command, query, flag, guidance in cases:
            with self.subTest(command=command):
                shell = self.start()
                shell.text("git() { printf executed > " + shlex.quote(str(shell.executed)) + "; }")
                shell.keys("Enter")
                shell.wait_for(lambda state: state.cells[state.y] == PROMPT.rstrip())
                prefix, suffix = command + " ", " existing"
                shell.text(prefix + suffix)
                shell.keys(*(["Left"] * len(suffix)))
                shell.resize(60, 16)
                for action in ("Escape", "Enter"):
                    shell.open_menu()
                    shell.keys("/")
                    shell.text(query)
                    shell.keys("Enter")
                    shell.wait_for(lambda state: state.cells[2] == "Filter: " + query)
                    shell.keys("Down")  # Each search returns the short alias, then the long one.
                    shell.wait_for(lambda state: any("> " + flag in row for row in state.cells[4:7]))
                    shell.find_detail(guidance)
                    shell.cancel(action)
                    if action == "Escape":
                        self.assertEqual(shell.read_buffer(), (prefix + suffix, len(prefix)))
                point = len(prefix + flag) + (0 if flag.endswith("=") else 1)
                self.assertEqual(shell.read_buffer(), (prefix + flag + suffix, point))
                self.assertFalse(shell.executed.exists())

    def test_attached_parent_value_rejection_preserves_midline_cursor_and_history(self):
        for flag in ("-f", "-p"):
            with self.subTest(flag=flag):
                shell = self.start()
                shell.text("docker() { printf executed > " + shlex.quote(str(shell.executed))
                           + "; }; export CLI_HELP_DRIVERS=" + shlex.quote(str(ROOT / "config/drivers.example")))
                shell.keys("Enter")
                shell.wait_for(lambda state: state.cells[state.y] == PROMPT.rstrip())
                line = "docker compose " + flag + "'café.yml' up --"
                self.pending(shell, line)
                point = line.index("café") + 2
                shell.keys(*(["Left"] * (len(line) - point)))
                shell.wait_for(lambda state: state.x == len(PROMPT) + point)
                shell.keys("Escape", "h")
                state = shell.wait_for(lambda value: value.alternate == 0 and "cursor_in_value" in " ".join(value.cells))
                self.assertEqual(state.x, len(PROMPT) + point)
                self.assertEqual(state.history_markers(), HISTORY)
                self.assertEqual(shell.read_buffer(), (line, point))
                self.assertFalse(shell.executed.exists())

    def test_root_global_literal_values_preserve_rendered_leaf_edits(self):
        for value in ("''", "-fixture"):
            with self.subTest(value=value):
                shell = self.start()
                shell.text("git() { printf executed > " + shlex.quote(str(shell.executed)) + "; }")
                shell.keys("Enter")
                shell.wait_for(lambda state: state.cells[state.y] == PROMPT.rstrip())
                line = "git -C " + value + " commit --m"
                before = self.pending(shell, line)
                menu = shell.open_menu()
                self.assertIn("git commit", menu.cells[0])
                shell.cancel("C-c")
                self.assert_restored(shell, line, before)
                shell.open_menu()
                shell.keys("Enter")
                self.assert_restored(shell, line[:-3] + "--message ")

    def test_parent_options_keep_leaf_context_cancel_resize_and_literal_edit(self):
        from test_context_diagnostics import LEAF, ROOT

        shell = self.start()
        self.configure(shell, [LEAF])
        shell.text("docker() { printf executed > " + shlex.quote(str(shell.executed))
                   + "; }; export CLI_HELP_DRIVERS=" + shlex.quote(str(ROOT / "config/drivers.example")))
        shell.keys("Enter")
        shell.wait_for(lambda state: state.cells[state.y] == PROMPT.rstrip())
        line = "docker compose -f 'café.yml' --profile debug up --det"
        before = self.pending(shell, line)
        menu = shell.open_menu()
        self.assertIn("docker compose up", menu.cells[0])
        shell.cancel("C-c")
        self.assert_restored(shell, line, before)
        shell.open_menu()
        shell.resize(60, 16)
        shell.resize(100, 24)
        shell.keys("Enter")
        self.assert_restored(shell, line[:-5] + "--detach ")

    def test_redacted_error_preserves_pending_line_cursor_and_scrollback(self):
        from test_context_diagnostics import ROOT

        shell = self.start()
        shell.text("kubectl() { printf executed > " + shlex.quote(str(shell.executed))
                   + "; }; export CLI_HELP_DRIVERS=" + shlex.quote(str(ROOT / "config/drivers.example")))
        shell.keys("Enter")
        shell.wait_for(lambda state: state.cells[state.y] == PROMPT.rstrip())
        line = "kubectl --token=SCREEN_PRIVATE_SENTINEL get --"
        self.pending(shell, line)
        shell.keys("Escape", "h")
        state = shell.wait_for(lambda value: value.alternate == 0 and "unsupported_option" in " ".join(value.cells))
        # The pending input remains visible by design. Only the error row is
        # inspected for disclosure; command buffers are not diagnostic reports.
        error_rows = [row for row in state.cells if "interactive-help:" in row]
        self.assertTrue(error_rows)
        self.assertTrue(all("SCREEN_PRIVATE_SENTINEL" not in row for row in error_rows))
        self.assertEqual(state.history_markers(), HISTORY)
        self.assertEqual(state.x, (len(PROMPT) + len(line)) % state.columns)
        self.assertEqual(shell.read_buffer(), (line, len(line)))
        self.assertFalse(shell.executed.exists())

    def test_optional_numeric_value_preserves_rendered_edit_and_argument_entry(self):
        from test_optional_integer_values import PROFILE

        shell = self.start()
        self.configure(shell, [PROFILE])
        line = "counted -m 2 --qu"
        before = self.pending(shell, line)
        shell.open_menu()
        shell.cancel()
        self.assert_restored(shell, line, before)
        shell.open_menu()
        shell.keys("Enter")
        expected = "counted -m 2 --query "
        self.assert_restored(shell, expected)
        shell.text("'日本'")
        state = shell.wait_for(lambda value: "日本" in "".join(value.cells))
        self.assertEqual(state.x, len(PROMPT + expected + "'日本'") + 2)
        self.assertEqual(shell.read_buffer(), (expected + "'日本'", len(expected + "'日本'")))
        self.assertFalse(shell.executed.exists())

    def configure(self, shell, profiles):
        """Install isolated fixture profiles without invoking any target command."""
        folder = shell.folder / "profiles"
        folder.mkdir()
        for index, profile in enumerate(profiles):
            (folder / f"{index}.json").write_text(json.dumps(profile))
        shell.text("export CLI_HELP_PROFILES=" + shlex.quote(str(folder)))
        shell.keys("Enter")
        shell.wait_for(lambda state: state.cells[state.y] == PROMPT.rstrip())

    def pending(self, shell, line):
        shell.text("printf 'HISTORY-%03d\\n' {1..80}")
        shell.keys("Enter")
        shell.wait_for(lambda state: state.history_markers() == HISTORY)
        shell.text(line)
        return shell.wait_for(lambda state: line in "".join(state.cells))

    def assert_restored(self, shell, line, before=None):
        state = shell.wait_for(lambda state: state.alternate == 0 and line.rstrip() in "".join(state.cells))
        self.assertEqual(state.history_markers(), HISTORY)
        self.assertEqual(state.x, (len(PROMPT) + len(line)) % state.columns)
        if before:
            self.assertEqual((state.cells, state.x, state.y), (before.cells, before.x, before.y))
        self.assertEqual(shell.read_buffer(), (line, len(line)))
        self.assertFalse(shell.executed.exists())

    def test_prefix_chain_cancel_resize_insert_and_argument_entry(self):
        shell = self.start()
        line = "command sudo -n env NOTE='café' rsync --ar"
        before = self.pending(shell, line)
        shell.open_menu()
        shell.cancel("C-c")
        self.assert_restored(shell, line, before)
        shell.open_menu()
        shell.resize(40, 10)
        shell.resize(100, 24)
        shell.keys("Enter")
        expected = line[:-4] + "--archive "
        self.assert_restored(shell, expected)
        shell.text("'日本 folder'")
        # Wide characters occupy two rendered cells each; buffer offsets remain
        # Unicode character offsets, independent of terminal column width.
        state = shell.wait_for(lambda state: "日本 folder" in "".join(state.cells))
        self.assertEqual(state.x, len(PROMPT + expected + "'日本 folder'") + 2)
        self.assertEqual(shell.read_buffer(), (expected + "'日本 folder'", len(expected + "'日本 folder'")))

    def test_keyword_selection_and_repeated_group_browser_labels(self):
        shell = self.start()
        fixture = {"command": ["structured"], "description": "Structured fixture",
                   "positional_group": {"argument": "ADDRESS FILE", "argument_count": 2, "repeatable": True},
                   "categories": [{"name": "Selection", "options": [
                       {"kind": "keyword", "flag": "device", "argument": "NAME", "summary": "Choose a device"}]}]}
        self.configure(shell, [fixture])
        line = "structured 0x1000 'café.bin' de"
        before = self.pending(shell, line)
        menu = shell.open_menu()
        self.assertIn("[keyword]", " ".join(menu.cells))
        shell.find_detail("ADDRESS FILE")
        shell.cancel()
        self.assert_restored(shell, line, before)
        shell.open_menu()
        shell.keys("Enter")
        self.assert_restored(shell, line[:-2] + "device ")

    def test_explicit_module_profile_and_joined_selector_cells(self):
        shell = self.start()
        fixture = {"command": ["python3", "-m", "pytest"], "description": "Explicit module profile",
                   "categories": [{"name": "Selection", "options": [
                       {"flag": "--maxfail", "argument": "NUM", "summary": "Stop after NUM failures"}]}]}
        self.configure(shell, [fixture])
        line = "env NOTE=café python3 -I -m pytest --max"
        before = self.pending(shell, line)
        shell.open_menu()
        shell.cancel()
        self.assert_restored(shell, line, before)
        shell.open_menu()
        shell.keys("Enter")
        self.assert_restored(shell, line[:-5] + "--maxfail ")
        shell.keys("C-u")
        shell.text("ffmpeg -i 'café.mp4' -c:v")
        shell.wait_for(lambda state: "ffmpeg -i" in " ".join(state.cells))
        shell.open_menu()
        shell.keys("Enter")
        self.assert_restored(shell, "ffmpeg -i 'café.mp4' -c:v ")


if __name__ == "__main__":
    unittest.main()
