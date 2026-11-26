"""Ubuntu command ownership, source editions and insertion through the interactive resolver."""

import json
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "cli_help"))
from bash_builtins import BUILTINS, HELP_SCRIPT, RELATED
from command_paths import help_route
from core import HelpError, find_context, insert_option, validate_profile
from discovery import Settings, build_profile, discover

FIXTURES = ROOT / "tests/fixtures/ubuntu-coverage"


def rows(profile):
    return {row["flag"]: row for category in profile["categories"] for row in category["options"]}


class UbuntuPackagingTests(unittest.TestCase):
    def menu(self, edition, line, cursor=None):
        captures = json.loads((FIXTURES / f"{edition}-help.json").read_text())
        def lookup(program, subcommands=()):
            name = Path(program).name
            route = help_route(name, tuple(subcommands))
            self.assertEqual(route.arguments, ("--help",))
            self.assertEqual(route.manual, name)
            documents = [(f"{name} --help", captures[name]),
                         (f"man {name}", (FIXTURES / f"{edition}-{name}.txt").read_text())]
            return build_profile([name, *subcommands], documents)
        return find_context(line, len(line) if cursor is None else cursor, [], lookup)

    def test_apt_verb_edition_alias_and_operand_boundaries(self):
        for edition in ("noble", "resolute"):
            with self.subTest(edition=edition):
                root = self.menu(edition, "apt ins")
                self.assertEqual(insert_option(root, rows(root.profile)["install"]), ("apt install ", 12))
                self.assertEqual("history-undo" in rows(root.profile), edition == "resolute")
                self.assertEqual("--cli-version" in rows(root.profile), edition == "resolute")
                line = "command sudo -n apt -o 'X=private' list --ins\t'café'"
                context = self.menu(edition, line, line.index("\t"))
                self.assertEqual(context.profile["command"], ["apt", "list"])
                self.assertEqual(insert_option(context, rows(context.profile)["--installed"])[0],
                                 line.replace("--ins\t", "--installed\t"))
                for verb in ("autoremove", "auto-remove"):
                    self.assertIn("--simulate", rows(self.menu(edition, "apt-get " + verb + " ").profile))
                self.assertNotIn("--simulate", rows(self.menu(edition, "apt-cache search ").profile))
                for line in ("apt -o ", "apt install --target-release ", "apt install -- ",
                             "apt install example ", "apt-config dump --format "):
                    with self.subTest(line=line), self.assertRaises(HelpError):
                        self.menu(edition, line)

    def test_dpkg_action_aliases_and_fixed_operand_counts(self):
        for edition in ("noble", "resolute"):
            for program, flags, arity in (("dpkg", ("--compare-versions",), 3),
                                         ("dpkg-deb", ("--extract", "-x"), 2),
                                         ("dpkg-query", ("--control-show",), 2)):
                options = rows(self.menu(edition, program + " ").profile)
                for flag in flags:
                    self.assertEqual(options[flag]["argument_count"], arity)
                    for count in range(arity):
                        with self.assertRaises(HelpError):
                            self.menu(edition, program + " " + flag + " " + "private " * count)
            main = rows(self.menu(edition, "dpkg ").profile)
            for flag in ("--extract", "-x", "--vextract", "-X"):
                self.assertEqual(main[flag]["argument_count"], 2)
            for template in ("--assert-feature", "--validate-thing"):
                self.assertNotIn(template, main)
            self.assertIn("--validate-archname", main)
            self.assertNotIn("--install", rows(self.menu(edition, "dpkg-query ").profile))


class UbuntuBuiltinTests(unittest.TestCase):
    def test_all_builtins_use_only_exact_bash_help(self):
        guidance = set(": bg break builtin caller continue eval exit false fg getopts let logout return shift times true".split())
        for edition in ("resolute", "noble"):
            topics = json.loads((FIXTURES / f"{edition}-bash.json").read_text())
            self.assertEqual(set(topics), BUILTINS)
            for name in sorted(topics):
                with self.subTest(edition=edition, name=name):
                    def probe(argv, timeout, check):
                        self.assertTrue(check)
                        self.assertEqual(argv[:-1], ["/bin/bash", "--noprofile", "--norc", "-c", HELP_SCRIPT, "help"])
                        self.assertIn(argv[-1], {name, RELATED.get(name)})
                        return topics[argv[-1]]
                    line = name + " "
                    with patch("discovery.run_probe", side_effect=probe):
                        lookup = lambda command, subcommands=(): discover(command, Settings(), subcommands=subcommands)
                        if name in guidance or edition == "noble" and name in (".", "source"):
                            with self.assertRaises(HelpError) as error:
                                find_context(line, len(line), [], lookup)
                            self.assertEqual(error.exception.code, "usage_guidance")
                        else:
                            ctx = find_context(line, len(line), [], lookup)
                            validate_profile(ctx.profile, Path("Bash"))
                            self.assertEqual(ctx.profile["command"], ["builtin", name])
                            if name == "read":
                                self.assertEqual("-E" in rows(ctx.profile), edition == "resolute")
                                self.assertEqual(rows(ctx.profile)["-u"]["argument"], "fd")
                            if name in ("dirs", "pushd", "popd"):
                                self.assertNotIn("-N", rows(ctx.profile))
                            if name in ("test", "["):
                                self.assertEqual(rows(ctx.profile)["-d"]["argument"], "FILE")

    def test_qualified_external_and_prefix_ownership(self):
        for prefix, exe in (("env echo", "echo"), ("sudo echo", "echo"), ("/bin/echo", "/bin/echo")):
            lookup = Mock(side_effect=HelpError("external"))
            with self.assertRaises(HelpError):
                find_context(prefix + " ", len(prefix) + 1, [], lookup)
            lookup.assert_called_once_with(exe)
        for cmd in ("echo", "command -- echo", "builtin echo"):
            lookup = Mock(side_effect=HelpError("builtin"))
            with self.assertRaises(HelpError):
                find_context(cmd + " ", len(cmd) + 1, [], lookup)
            lookup.assert_called_once_with("builtin", subcommands=("echo",))


class UbuntuReferenceTests(unittest.TestCase):
    def test_digit_leading_model_selection_preserves_pending_arguments(self):
        from ubuntu_reference import lookup_record, reference_profile
        record = lookup_record("getweb", "resolute", "/usr/sbin", "/usr/sbin/getweb")
        profile = reference_profile(record, build_profile, validate_profile)
        for partial, model in (("10", "1025"), ("26", "2600n")):
            line = "getweb " + partial + " 'untouched value'"
            ctx = find_context(line, len("getweb " + partial), [profile])
            updated, cursor = insert_option(ctx, rows(profile)[model])
            self.assertEqual(updated, "getweb " + model + " 'untouched value'")
            self.assertGreaterEqual(cursor, len("getweb " + model))
        for invalid in ("1;id", "1/2", "1 2", "1$var"):
            bad = {**profile, "categories": [{"name": "Models", "options": [
                {"flag": invalid, "kind": "keyword", "summary": "Model"}]}]}
            with self.assertRaises(HelpError):
                validate_profile(bad, Path("<invalid>"))

    def test_online_manual_operands_and_source_guidance(self):
        from ubuntu_reference import lookup_record, reference_profile
        examples = (
            ("hp-align", "/usr/share/hplip/align.py", "-d", "device-uri", "attached_only"),
            ("hp-align", "/usr/share/hplip/align.py", "--device", "device-uri", "equals"),
            ("cftp3", "/usr/bin/cftp3", "-b", "COMMAND_FILE", "separate"),
            ("brltty-ctb", "/usr/bin/brltty-ctb", "--tables-directory", "directory", "equals"),
            ("ubuntu-report", "/usr/bin/ubuntu-report", "--verbose", "", None),
            ("umax_pp", "/usr/bin/umax_pp", "-h", "HEIGHT", "separate"),
        )
        for name, target, flag, arg, style in examples:
            with self.subTest(name=name, flag=flag):
                record = lookup_record(name, "resolute", "/usr/bin", target)
                profile = reference_profile(record, build_profile, validate_profile)
                option = rows(profile)[flag]
                self.assertEqual((option.get("argument", ""), option.get("argument_style")), (arg, style))
        record = lookup_record("hp-plugin-ubuntu", "resolute", "/usr/bin", "/usr/bin/hp-plugin-ubuntu")
        with self.assertRaisesRegex(HelpError, "wrapper selects"):
            reference_profile(record, build_profile, validate_profile)

    def test_shared_manual_groups_and_keyword_boundaries(self):
        from ubuntu_reference import lookup_record, reference_profile
        for edition in ("resolute", "noble"):
            def menu(name, target):
                record = lookup_record(name, edition, "/usr/bin", target)
                return rows(reference_profile(record, build_profile, validate_profile))
            with self.subTest(edition=edition):
                self.assertEqual(menu("jq", "/usr/bin/jq")["--argjson"]["argument_count"], 2)
                gsettings = menu("gsettings", "/usr/bin/gsettings")
                self.assertEqual(gsettings["list-schemas"]["kind"], "keyword")
                self.assertNotIn("--print-paths", gsettings)
                self.assertIn("device", menu("btrfs", "/usr/bin/btrfs"))
        target = "/usr/sbin/xtables-nft-multi"
        save = rows(reference_profile(lookup_record("iptables-nft-save", "resolute", "/usr/sbin", target),
                                      build_profile, validate_profile))
        arp = rows(reference_profile(lookup_record("arptables-nft-save", "resolute", "/usr/sbin", target),
                                     build_profile, validate_profile))
        self.assertEqual(save["--file"]["argument"], "FILE")
        self.assertNotIn("--file", arp)
        self.assertNotIn("--help", save)

    def test_noble_optional_fixed_sources(self):
        import hashlib
        from ubuntu_reference import lookup_record, reference_profile
        for name, flag, operand in (("redis-cli", "-p", "PORT"), ("sqlite3", "-cmd", "COMMAND")):
            record = lookup_record(name, "noble", "/usr/bin", "/usr/bin/" + name)
            capture = (FIXTURES / f"noble-{name}-help.txt").read_bytes()
            self.assertEqual(record["sha256"], hashlib.sha256(capture).hexdigest())
            self.assertEqual(rows(reference_profile(record, build_profile, validate_profile))[flag]["argument"], operand)
        record = lookup_record("atop", "noble", "/usr/bin", "/usr/bin/atop")
        self.assertEqual(rows(reference_profile(record, build_profile, validate_profile))["-w"]["argument"], "RAWFILE")

    def test_snap_revision_and_debian_provider_are_independent(self):
        from ubuntu_reference import installed_reference, lookup_record, reference_profile
        for name in ("firefox.geckodriver", "geckodriver"):
            record = lookup_record(name, "resolute", "/snap/bin", "/usr/bin/snap")
            self.assertEqual(rows(reference_profile(record, build_profile, validate_profile))["--port"]["argument"], "PORT")
            with patch.object(Path, "readlink", return_value=Path("8763")):
                installed_reference(record)
            with patch.object(Path, "readlink", return_value=Path("9000")), self.assertRaisesRegex(HelpError, "revision 8763"):
                installed_reference(record)
        binary = lookup_record("hwctl", "resolute", "/usr/bin", "/usr/bin/hwctl")
        snap = lookup_record("hwctl", "resolute", "/snap/bin", "/usr/bin/snap")
        self.assertNotIn("snap_revision", binary)
        self.assertEqual(snap["snap_revision"], "123")
        launcher = lookup_record("firefox", "resolute", "/usr/bin", "/usr/bin/firefox")
        self.assertEqual(launcher["launcher_package"], "firefox")
        from io import StringIO
        status = "Package: firefox\nStatus: install ok installed\nVersion: different\n\n"
        with patch.object(Path, "readlink", return_value=Path("8763")), patch.object(Path, "open", return_value=StringIO(status)):
            with self.assertRaisesRegex(HelpError, "differs"):
                installed_reference(launcher)

    def test_ranked_sources_and_arity_without_optional_executables(self):
        from ubuntu_reference import reference_profile, reference_record
        for edition in ("noble", "resolute"):
            for program, flag, argument in (("smartctl", "--device", "TYPE"), ("sensors", "-c", "config-file"),
                                            ("sshfs", "-o", "OPTION[,OPTION...]"), ("nginx", "-c", "file"),
                                            ("tree", "-L", "level"), ("apache2ctl", "configtest", "")):
                with self.subTest(edition=edition, program=program), patch("ubuntu_reference.ubuntu_edition", return_value=edition):
                    record = reference_record(program, "/usr/bin/" + program)
                    profile = reference_profile(record, build_profile, validate_profile)
                    entry = rows(profile)[flag]
                    self.assertEqual(entry.get("argument", ""), argument)
                    self.assertEqual(entry.get("kind") == "keyword", flag == "configtest")

    def test_optional_rank_bands_and_kernel_declarations(self):
        """Check source spellings and argument ownership across the three ranked groups."""
        from ubuntu_reference import lookup_record, reference_profile
        checks = (
            ("smartctl", "--health", ""), ("sensors", "--config-file", "config-file"),
            ("apache2ctl", "graceful-stop", ""), ("make", "--always-make", ""),
            ("sshfs", "-p", "PORT"), ("nginx", "-s", "signal"),
            ("redis-cli", "-h", "HOSTNAME"), ("wg", "show", ""),
            ("zpool", "status", ""), ("tree", "-L", "level"), ("cmake", "-S", "path-to-source"),
            ("npx", "--package", "PACKAGE"), ("gh", "issue", ""), ("fish", "--command", "COMMAND"),
            ("gofmt", "-r", "RULE"), ("go", "build", ""), ("mysql", "--host", "host_name"),
            ("starship", "completions", ""), ("photorec", "/log", ""), ("testdisk", "/list", ""),
            ("buildah", "--version", ""),
        )
        for name, spelling, arg in checks:
            with self.subTest(name=name):
                target = "/usr/lib/go-1.26/bin/go" if name == "go" else "/usr/bin/" + name
                record = lookup_record(name, "resolute", "/usr/bin", target)
                profile = reference_profile(record, build_profile, validate_profile)
                self.assertEqual(rows(profile)[spelling].get("argument", ""), arg)
        for name, flag, arg in (("grub-mkconfig", "--output", "FILE"), ("bc", "--interactive", ""),
                                ("cmp", "--verbose", ""), ("iw", "--debug", ""), ("snap", "install", "")):
            path = "/usr/sbin/" if name == "grub-mkconfig" else "/usr/bin/"
            if name == "iw":
                path = "/usr/sbin/"
            record = lookup_record(name, "resolute", path.rstrip("/"), path + name)
            self.assertEqual(rows(reference_profile(record, build_profile, validate_profile))[flag].get("argument", ""), arg)
        directory = "/usr/lib/linux-tools-7.0.0-30"
        for name, spelling, arg in (("acpidbg", "-f", "FILE"), ("rtla", "timerlat", ""),
                                    ("turbostat", "--interval", "SECONDS"),
                                    ("x86_energy_perf_policy", "--cpu", "CPU-LIST")):
            with self.subTest(name=name):
                record = lookup_record(name, "resolute", directory, directory + "/" + name)
                self.assertEqual(rows(reference_profile(record, build_profile, validate_profile))[spelling].get("argument", ""), arg)

    def test_default_discovery_fallback_and_guards(self):
        from ubuntu_reference import reference_record
        with patch("ubuntu_reference.ubuntu_edition", return_value="resolute"):
            with patch("discovery.shutil.which", side_effect=lambda name: "/usr/bin/sensors" if name == "sensors" else None), \
                    patch("discovery.installed_reference"), patch("discovery.executable_identity", return_value={}), \
                    patch("discovery.run_probe", side_effect=AssertionError("unexpected probe")):
                ctx = find_context("sensors ", 8, [], lambda cmd: discover(cmd, Settings()))
                self.assertIn("--fahrenheit", rows(ctx.profile))
                self.assertIn("reference_sha256", ctx.profile["discovery"])
                with self.assertRaisesRegex(HelpError, "disabled"):
                    discover("sensors", Settings(mode="off"))
                with self.assertRaisesRegex(HelpError, "not found"):
                    discover("smartctl", Settings())
            self.assertIsNone(reference_record("sensors", "/tmp/sensors"))
            self.assertIsNone(reference_record("intel-speed-select", "/usr/lib/linux-tools-0.0.0-1/intel-speed-select"))
            kernel = reference_record("intel-speed-select", "/usr/lib/linux-tools-7.0.0-30/intel-speed-select")
            self.assertEqual(kernel["version"], "7.0.0-30.30")
            for target, package in (("/usr/bin/mawk", "mawk"), ("/usr/bin/gawk", "gawk")):
                with patch("ubuntu_reference.os.path.realpath", return_value=target):
                    # Patch only the provider lookup. The executable directory remains canonical.
                    with patch.object(Path, "resolve", return_value=Path("/usr/bin")):
                        self.assertEqual(reference_record("awk", "/usr/bin/awk")["package"], package)

    def test_supported_installed_packaging_and_shell_sources(self):
        """Match the full fixed replies when this target has the captured upstream edition."""
        import subprocess
        from ubuntu_reference import ubuntu_edition
        edition = ubuntu_edition()
        if not edition or not Path("/usr/bin/apt").is_file():
            self.skipTest("Fixed Ubuntu package and shell sources require a matching Ubuntu target")
        expected = {kind: json.loads((FIXTURES / f"{edition}-{kind}.json").read_text())
                    for kind in ("bash", "help")}
        actual = json.loads(subprocess.check_output([sys.executable, FIXTURES / "capture-shell-packaging.py"]))
        if actual["help"]["apt"].splitlines()[0] != expected["help"]["apt"].splitlines()[0]:
            self.skipTest("Installed APT edition differs from the recorded Ubuntu package")
        for kind, captures in expected.items():
            self.assertEqual(actual[kind], captures)
