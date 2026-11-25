"""Real Bash/tmux checks for rendered Details, literal edits, and terminal key handling."""

import copy
import json
import shlex
import time
import unittest

from test_terminal_screen import TerminalTestCase, TMUX_AVAILABLE, PROMPT, HISTORY, ROOT
from test_argument_syntax import PROFILE
from presentation import option_label, option_text
from ui import ellipsize_cells, option_label_width, wrap_cells


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
        self.assertEqual(menu.cells[5].replace("│", "").strip(), "")
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

    def pending_stubbed_command(self, command, suffix, columns, rows, stub_names, flash_version=None):
        """Place the cursor before a suffix. Guarded flash routes allow only fixed help probes."""
        shell = self.start()
        export = "export PATH=" + shlex.quote(str(shell.folder)) + ':"$PATH"'
        for name in stub_names:
            stub = shell.folder / name
            script = "#!/bin/sh\n"
            if flash_version:
                leaf = command.split()[1]
                script += ('if [ "$#" = 1 ] && [ "$1" = --help ]; then echo ' +
                           shlex.quote("esptool v" + flash_version) + '; exit 0; fi\n')
                script += ('if [ "$#" = 2 ] && [ "$1" = ' + shlex.quote(leaf) +
                           ' ] && [ "$2" = --help ]; then printf "Options:\\n  --force  Force writing\\n"; exit 0; fi\n')
                export += " CLI_HELP_DISCOVERY=auto CLI_HELP_DRIVERS=" + shlex.quote(str(ROOT / "config/drivers.example"))
            stub.write_text(script + "echo executed >> " + shlex.quote(str(shell.executed)) + "\nexit 1\n")
            stub.chmod(0o700)
        shell.text(export)
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

    def check_command_menu(self, command, suffix, narrow=None, listing=False, flash_version=None):
        """Inspect every row in tmux, then exercise a command-specific edit at minimum size."""
        profile = json.loads((ROOT / "profiles" / (command.replace(" ", "-") + ".json")).read_text())
        pending = command + " show" if listing else command
        # Flash geometry includes per-chip value tables that need up to 63 Details lines.
        height = 160 if flash_version else 120
        shell, prefix, suffix = self.pending_stubbed_command(pending, suffix, 220, height, (command.split()[0],), flash_version)
        self.check_rendered_rows(profile, shell, prefix, suffix)
        if narrow is None:
            return  # An existing minimum-size regression covers this command.
        query, flag, qualification, operand = narrow
        shell.resize(60, 16)
        category, option = next((category, opt) for category in profile["categories"]
                                for opt in category["options"] if opt["flag"] == flag)
        # A 60-column menu has 39 cells for the options column.
        label = ellipsize_cells(option_label(option), option_label_width(category, 39))
        for action in ("Escape", "Enter"):
            self.assertEqual(shell.open_menu().cells[2].rstrip(), "Filter:")
            shell.keys("/")
            shell.text(query)
            shell.keys("Enter")
            found = shell.wait_for(lambda state: state.cells[2] == "Filter: " + query
                                   and "> " + label in state.cells[4])
            if action == "Escape":
                self.reach_detail(shell, found, qualification)
            shell.cancel(action)
            if action == "Escape":
                self.assertEqual(shell.read_buffer(), (prefix + suffix, len(prefix)))
        joined = flag.endswith("=")
        self.assertEqual(shell.read_buffer(), (prefix + flag + suffix, len(prefix + flag) + (0 if joined else 1)))
        shell.text(operand if joined else operand + " ")
        edited = prefix + flag + ("" if joined else " ") + operand
        self.assertEqual(shell.read_buffer(), (edited + suffix, len(edited) + (0 if joined else 1)))
        self.assertFalse(shell.executed.exists())

    def test_iproute2_manual_menus(self):
        """Inspect the three listing menus and the socket menu with pending filters."""
        cases = [
            ("ip address", " dev lo", ("protocol attribute", "proto", "Addresses lacking the protocol attribute also pass.", "42")),
            ("ip link", " up", ("vrf device", "vrf", "Members of that VRF appear in the listing.", "blue")),
            ("ip route", " table local", None),
            ("ss", " --tcp", ("socket-local storage from one", "--bpf-map-id=", "permission to read the map.", "42")),
        ]
        for command, suffix, narrow in cases:
            with self.subTest(command=command):
                self.check_command_menu(command, suffix, narrow, listing=command.startswith("ip "))

    def test_systemd_manual_menus(self):
        """Inspect the manager and journal menus without a connection to system services."""
        cases = [
            ("systemctl list-units", " 'demo*.service'", ("remote system manager", "--host=", "Remote transport requires system scope.", "demo.example")),
            ("systemctl show", " demo.service", ("values of selected properties", "-P", "Explicitly selected empty properties are included.", "MainPID")),
            ("systemctl status", " demo.service", ("select the timestamp format", "--timestamp=", "--output= controls journal-entry formatting.", "utc")),
            ("journalctl", " --no-pager", None),
        ]
        for command, suffix, narrow in cases:
            with self.subTest(command=command):
                self.check_command_menu(command, suffix, narrow)

    def test_openssl_manual_menus(self):
        """Inspect TLS, certificate and digest options with pending file operands."""
        cases = [
            ("openssl s_client", " -showcerts", None),
            ("openssl x509", " -in 'test cert.pem'", ("comma-separated extension names", "-ext", "the list limits which extensions are copied.", "subjectAltName,keyUsage")),
            ("openssl dgst", " 'input file'", ("extendable-output digest", "-xoflen", "Signing does not support this option.", "32")),
        ]
        for command, suffix, narrow in cases:
            with self.subTest(command=command):
                self.check_command_menu(command, suffix, narrow)

    def test_uv_manual_menus(self):
        """Inspect each uv menu before a pending package, environment or resolver option."""
        cases = [
            ("uv add", " 'example[cli]'", ("new requirement", "--bounds", "With --frozen, uv adds no inferred bound.", "minor")),
            ("uv lock", " --offline", ("distribution upload time", "--exclude-newer", "Months and years are rejected.", "'7 days'")),
            ("uv sync", " --extra docs", ("only the named distribution", "--only-install-package", "dependencies, are left out", "example")),
            ("uv tool install", " example", ("pytorch package index", "--torch-backend", "This option is in preview.", "cpu")),
            ("uv venv", " '.venv debug'", ("activation prompt label", "--prompt", "current directory supplies the label.", "debug")),
        ]
        for command, suffix, narrow in cases:
            with self.subTest(command=command):
                self.check_command_menu(command, suffix, narrow)

    def test_ruff_manual_menus(self):
        """Read configuration-dependent lint and formatting choices with a pending filename."""
        cases = [
            ("ruff check", ("suppress selected rules", "--per-file-ignores", "to preserve the pattern.", "'*.py:S101'")),
            ("ruff format", ("range within one file", "--range", "Notebook ranges are unsupported.", "2:1-5:1")),
        ]
        for command, narrow in cases:
            with self.subTest(command=command):
                self.check_command_menu(command, " 'demo file.py'", narrow)

    def test_pytest_manual_menu(self):
        """Walk the core options, including the optional log operand, before a quoted node ID."""
        self.check_command_menu("pytest", " 'test_cli.py::test_args[two words]'",
                                ("internal debug log", "--debug", "Opening the log truncates any existing file.", "trace.log"))

    def test_go_manual_menus(self):
        """Read Go build, test, program and module options at their insertion boundaries."""
        cases = [
            ("go build", " ./cmd/demo", ("replacement file", "-overlay", "still see the real files.", "overlay.json")),
            ("go test", " ./...", ("minimization attempt", "-fuzzminimizetime", "0x disables minimization.", "100x")),
            ("go run", " main.go --child", ("TOOLEXEC_IMPORTPATH", "-toolexec", "identifies the package being built.", "wrapper")),
            ("go mod tidy", " -v", ("alternate checksum", "-modfile", "review.mod with review.sum.", "review.mod")),
        ]
        for command, suffix, narrow in cases:
            with self.subTest(command=command):
                self.check_command_menu(command, suffix, narrow)

    def test_dotnet_manual_menus(self):
        """Read SDK options without building, restoring, publishing or running a project."""
        cases = [
            ("dotnet build", ("multi-targeted project", "-o", "mix files from different projects.", "'out dir'")),
            ("dotnet publish", ("nested publish folders", "-o", "avoids nested publish folders", "'out dir'")),
            ("dotnet restore", ("global packages folder for this restore", "--packages", "unless configuration or the environment overrides it.", "packages")),
            ("dotnet run", ("apply a named launch profile", "--launch-profile", "such as environment variables.", "Local")),
            ("dotnet test", ("vstest expression", "--filter", "Available properties depend on the test adapter.", "'Name~Demo'")),
        ]
        for command, narrow in cases:
            with self.subTest(command=command):
                self.check_command_menu(command, " 'Demo Project.csproj'", narrow)

    def test_bun_manual_menu_and_script_arguments(self):
        """Insert before a script and reject parent edits while its arguments are under the cursor."""
        self.check_command_menu("bun run", " task 'two words' --watch",
                                ("absolute path", "--cwd", "restart can find the directory again.", "'app dir'"))
        shell, prefix, suffix = self.pending_stubbed_command("bun run task 'two words' --watch", " --child-end",
                                                            60, 16, ("bun", "task"))
        shell.keys("Escape", "h")
        shell.wait_for(lambda state: state.alternate == 0 and "child_argument_boundary" in " ".join(state.cells))
        self.assertEqual(shell.read_buffer(), (prefix + suffix, len(prefix)))
        self.assertFalse(shell.executed.exists())

    def test_psql_and_playbook_manual_menus(self):
        """Inspect command-file ordering and host-list syntax before pending operands."""
        self.check_command_menu("psql", " demo", ("file line numbers", "--file", "without Readline.", "'input file.sql'"))
        self.check_command_menu("ansible-playbook", " site.yml",
                                ("inline host list", "--inventory", "trailing comma", "web1,"))

    def test_cloud_manual_menus(self):
        """Read leaf and inherited options without a cloud login or service request."""
        cases = [
            ("az account show", " --verbose", ("client-side query", "--query", "Quote shell metacharacters.", "'name'")),
            ("az vm list", " --verbose", ("scale set", "--vmss", "Supply its name or resource ID.", "demo-scale-set")),
            ("az storage blob list", " -c demo", ("per service call", "--timeout", "Pagination can take longer.", "30")),
            ("gcloud config list", " core", ("sort matching properties", "--sort-by", "Use ~ for descending order.", "'~name'")),
            ("gcloud compute instances list", " --uri", ("resources per API page", "--page-size", "Use --limit for the total.", "20")),
            ("gcloud storage ls", " 'gs://example/*'", ("object contexts", "--metadata-filter", "Buckets and folders still appear.", """'contexts."team"="qa"'""")),
        ]
        for command, suffix, narrow in cases:
            with self.subTest(command=command):
                self.check_command_menu(command, suffix, narrow)

    def test_platformio_and_arduino_manual_menus(self):
        """Inspect both PlatformIO executable names and the Arduino compilation menu."""
        for executable in ("pio", "platformio"):
            self.check_command_menu(executable + " run", " -e demo",
                                    ("shared endpoint", "-p", "dedicated option", "ttyFIXTURE"))
            self.check_command_menu(executable + " device monitor", " -e demo",
                                    ("line ending", "--eol", "default is CRLF", "LF"))
        self.check_command_menu("arduino-cli compile", " 'Sketch Dir'",
                                ("intermediate files", "--build-path", "Quote paths with spaces", "'build cache'"))

    def test_guarded_flash_manual_menus(self):
        """Read all guarded menus, refuse incomplete pairs and reject mismatched versions."""
        for command in ("esptool.py write_flash", "esptool.py write-flash", "esptool write-flash"):
            legacy = command.endswith("write_flash")
            version, wrong_version = ("4.8.1", "5.1.0") if legacy else ("5.1.0", "4.8.1")
            with self.subTest(command=command):
                self.check_command_menu(command, " 0x1000 app.bin",
                                        ("custom pin mapping", "--spi-connection", "CLK,Q,D,HD,CS", "SPI"),
                                        flash_version=version)
                pair_shell, first, second = self.pending_stubbed_command(
                    command + " 0x1000 one.bin", " 0x2000 two.bin", 100, 24, (command.split()[0],), version)
                if legacy:
                    pair_shell.keys("Escape", "h")
                    pair_shell.wait_for(lambda state: state.alternate == 0 and "positional_group_boundary" in " ".join(state.cells))
                    self.assertEqual(pair_shell.read_buffer(), (first + second, len(first)))
                else:
                    pair_shell.open_menu()
                    pair_shell.cancel("Enter")
                    self.assertEqual(pair_shell.read_buffer(), (first + "--flash-mode" + second, len(first + "--flash-mode ")))
                self.assertFalse(pair_shell.executed.exists())
                for extra, reported, diagnostic in ((" 0x1000", version, "positional_group_incomplete"),
                                                    ("", wrong_version, "requires v5")):
                    shell, prefix, suffix = self.pending_stubbed_command(
                        command + extra, " app.bin", 100, 24, (command.split()[0],), reported)
                    shell.keys("Escape", "h")
                    shell.wait_for(lambda state: state.alternate == 0 and diagnostic in " ".join(state.cells))
                    self.assertEqual(shell.read_buffer(), (prefix + suffix, len(prefix)))
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
            self.assertNotIn(qualification, " ".join(" ".join(found.detail_body).split()))
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
            self.assertNotIn(qualification, " ".join(" ".join(found.detail_body).split()))
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
        shell.verify_profile(profile)
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
        shell.find_detail(text)

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
                    self.assertNotIn(qualification, " ".join(" ".join(found.detail_body).split()))
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
                    self.assertNotIn(qualification, " ".join(" ".join(found.detail_body).split()))
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
        menu = shell.wait_for(lambda value: value.alternate == 1 and "> --beta" in value.selected_row)
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
