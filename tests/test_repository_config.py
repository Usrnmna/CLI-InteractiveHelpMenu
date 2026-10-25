"""Protect private local artifacts while keeping maintained repository inputs visible."""

import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import unittest
import uuid


ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which("git"), "Ignore-policy checks require Git")
class RepositoryIgnoreTests(unittest.TestCase):
    def setUp(self):
        parent = (ROOT / ".cache/repository-config-tests").resolve()
        parent.mkdir(parents=True, exist_ok=True)
        self.folder = parent / uuid.uuid4().hex
        self.folder.mkdir()
        # Verify the absolute cleanup target before registering a recursive delete.
        if self.folder.resolve().parent != parent or self.folder.is_symlink():
            raise RuntimeError("Disposable repository left its intended test directory")
        self.addCleanup(shutil.rmtree, self.folder)
        self.environment = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
        self.environment.update({"HOME": str(self.folder), "XDG_CONFIG_HOME": str(self.folder / ".config"),
                                 "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
                                 "GIT_TERMINAL_PROMPT": "0"})
        shutil.copyfile(ROOT / ".gitignore", self.folder / ".gitignore")
        shutil.copyfile(ROOT / ".gitattributes", self.folder / ".gitattributes")
        subprocess.run(["git", "init", "--quiet", str(self.folder)], env=self.environment,
                       check=True, capture_output=True, timeout=10)

    def assert_policy(self, paths, ignored):
        """Check Git's effective result without consulting or changing the real index."""
        for path in paths:
            with self.subTest(path=path):
                result = subprocess.run(["git", "-C", str(self.folder), "check-ignore", "--quiet", "--no-index", "--", path],
                                        env=self.environment, capture_output=True, text=True, timeout=10)
                self.assertIn(result.returncode, (0, 1), result.stderr)
                self.assertEqual(result.returncode == 0, ignored)

    def test_private_tool_homes_credentials_and_histories_are_ignored(self):
        self.assert_policy([
            ".aws/credentials", ".ssh/id_ed25519", ".gnupg/private-keys-v1.d/key", ".kube/config",
            ".docker/config.json", ".config/gh/hosts.yml", ".config/cli-help/profiles/private.json",
            ".azure/accessTokens.json", ".git-credentials", ".netrc", ".pypirc", ".bash_history",
            ".python_history", ".lesshst", ".wget-hsts", ".env", ".env.local",
            "tools/home/.aws/credentials", "tools/home/.ssh/id_ed25519",
            "tools/home/.config/gh/hosts.yml", "tools/home/.config/gcloud/credentials.db",
            "tools/home/.config/cli-help/profiles/private.json", "tools/home/.config/containers/auth.json",
            "tools/home/.local/share/containers/storage/private", ".local/share/cli-interactive-help/profiles/private.json",
            "tools/home/.local/share/cli-interactive-help/profiles/private.json", "tools/home/.netrc",
            "tools/home/.git-credentials", "tools/home/.bash_history",
        ], True)

    def test_reports_caches_and_owned_temporary_artifacts_are_ignored(self):
        self.assert_policy([
            "tests/reports/review/diagnostics.json", ".cache/tool/archive.tar.gz", ".lycheecache",
            "dist/candidate-v0.1.2-alpha/BUILD-INFO.json", "dist/candidate-v0.1.2-alpha/SHA256SUMS.checksum",
            "dist/candidate-v0.1.2-alpha-review/BUILD-INFO.json", ".cache/recommendation10-review/rendered-screens.json",
            ".cache/recommendation10/rendered-screens.json", "tests/reports/ci/release-candidate.log",
            "generated-help/profiles/generated.json", "cli-help-probe-session/output", "cli-help-review-session/draft.json",
            "cli-help-screen-session/tmux.sock", "cli-help-build-session/cli-help", "cli-help-media-session/raw.cast",
            "cli-help-capture-session/help.txt", "cli-help-functional-review-session/state.json",
            "cli-help-workflow-verification-session/source/cli_help/main.py",
            "cli-help-installer.Ab12Cd34/runtime/README.md", "cli-help-review-config-session/drivers/private.json",
            "tests/reports/recommendations-7-9-review/final/rendered-screens.json",
            ".cli-help-rc-session", ".review-state-session", ".cli-help-install.json", "cli-help",
            "scratch/runtime/cli-help", "tools/bin/cli-help",
            "collection/.scan.lock", "collection/.import.lock", "collection/.review-backups/backup.json",
            "collection/profiles/.cli-help-write-interrupted.tmp", ".cli-help-write-interrupted.tmp",
            "collection/.review-backups/recovery-session/manifest.json",
            "tools/.cache/release/BUILD-INFO.json", "tools/dist/candidate/cli-help",
            "tools/generated-help/profiles/private.json", "scratch/tests/reports/screen.json",
            "scratch/cli-help-build-ci.Ab12Cd34/candidate/BUILD-INFO.json",
            "scratch/cli-help-installer.Ab12Cd34/runtime/README.md",
            "scratch/cli-help-screen-session/tmux.sock", "scratch/.review-state-session",
            "scratch/runtime/.cli-help-install.json", "scratch/.cli-help-rc-session", "scratch/.lycheecache",
            "tests/reports/numerical-inventory/inventory.json", "tests/reports/ci/numerical-inventory-summary.json",
            "cli-help-inventory-session/profiles/private.json", "scratch/cli-help-inventory-session/help.txt",
        ], True)

    def test_source_fixtures_templates_and_public_assets_remain_visible(self):
        self.assert_policy([
            "cli_help/diagnostics.py", "profiles/ssh.json", "config/drivers.example/docker.json",
            "tests/fixtures/help/captured.json", "tests/test_repository_config.py", "docs/diagnostics.md",
            "tests/fixtures/help/workflow-baseline-captured.json", "tests/fixtures/help/workflow-manual-edge-cases.json",
            "tests/test_workflow_review.py", "tests/test_workflow_review_terminal.py",
            "tests/fixtures/help/syntax-7zip-captured.json", "tests/fixtures/help/syntax-7z-x.txt",
            "tests/test_collection.py", "docs/collection-recovery.md", "docs/argument-syntax.md",
            "cli_help/arguments.py", "cli_help/collection.py", "profiles/7z-x.json", "profiles/7zz-x.json",
            "tests/test_release_snapshot.py", "tests/test_release_terminal.py", "docs/release-candidate.md",
            "tests/test_syntax_collection_review.py", "tests/test_syntax_terminal.py", "tests/fixtures/help/syntax-7zz-x.txt",
            "docs/cli-help-installer.md", "docs/assets/cli-help-installer.png",
            "docs/assets/option-insertion.gif", "releases/v0.1.1-alpha/cli-help-v0.1.1-alpha-linux-x86_64",
            ".github/workflows/ci.yml", ".github/ISSUE_TEMPLATE/bug_report.yml", ".github/pull_request_template.md",
            ".github/ISSUE_TEMPLATE/feature_request.yml", ".github/ISSUE_TEMPLATE/config.yml",
            ".github/CONTRIBUTING.md", ".github/dependabot.yml",
            ".env.example", ".env.development.sample", "config/ssh.example", "examples/project/.env.template",
            "config/.ssh.example", "docs/cli-help-build-reference.md",
            "tests/fixtures/help/cli-help-installer-example.txt",
            "releases/v0.1.2-alpha/cli-help-v0.1.2-alpha-linux-x86_64.checksum",
            "scripts/inventory_numerical_descriptions.py", "tests/test_numerical_inventory.py",
            "docs/numerical-inventory/README.md", "docs/numerical-inventory/review.json", "docs/cli-help-inventory.md",
        ], False)

    def test_native_artifacts_are_binary_and_maintained_text_keeps_lf(self):
        """Use Git's actual attribute resolution for extensionless artifacts and sources."""
        binaries = ["cli-help", "scratch/runtime/cli-help", "cli-help-v0.1.2-alpha-linux-x86_64",
                    "dist/candidate/cli-help-v0.1.2-alpha-linux-x86_64",
                    "releases/v0.1.1-alpha/cli-help-v0.1.1-alpha-linux-x86_64",
                    "docs/assets/option-insertion.gif", "candidate.run", "candidate.tar.gz"]
        for name in binaries:
            with self.subTest(path=name):
                output = subprocess.check_output(["git", "-C", str(self.folder), "check-attr", "-z",
                                                  "binary", "text", "diff", "merge", "--", name],
                                                 env=self.environment, timeout=10).decode().split("\0")
                attributes = {output[index + 1]: output[index + 2] for index in range(0, len(output) - 1, 3)}
                self.assertEqual(attributes, {"binary": "set", "text": "unset", "diff": "unset", "merge": "unset"})
        for name in ("cli_help/main.py", "docs/usage.md", "tests/fixtures/help/workflow-sed.txt", "profiles/rsync.json",
                     "recording.cast", "capture.jsonl"):
            with self.subTest(path=name):
                output = subprocess.check_output(["git", "-C", str(self.folder), "check-attr", "-z", "text", "eol", "--", name],
                                                 env=self.environment, timeout=10).decode().split("\0")
                attributes = {output[index + 1]: output[index + 2] for index in range(0, len(output) - 1, 3)}
                self.assertEqual(attributes, {"text": "set", "eol": "lf"})

    def test_curated_inventory_is_not_marked_generated(self):
        """Keep maintained review decisions visible rather than treating them as output."""
        name = "docs/numerical-inventory/review.json"
        output = subprocess.check_output(["git", "-C", str(self.folder), "check-attr", "-z",
                                          "linguist-generated", "text", "eol", "--", name],
                                         env=self.environment, timeout=10).decode().split("\0")
        attributes = {output[index + 1]: output[index + 2] for index in range(0, len(output) - 1, 3)}
        self.assertEqual(attributes, {"linguist-generated": "unset", "text": "set", "eol": "lf"})

    def test_inventory_sessions_are_excluded_from_release_sources(self):
        """Keep release selection aligned with Git without requiring a Linux build."""
        spec = importlib.util.spec_from_file_location("release_source_policy", ROOT / "scripts/build_release.py")
        policy = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(policy)
        for name in ("docs/cli-help-inventory-session/private.json", "tools/cli-help-ignore-session/temporary.txt"):
            with self.subTest(path=name):
                self.assertTrue(policy.excluded_source(Path(name)))
        for name in ("docs/numerical-inventory/review.json", "docs/cli-help-inventory.md",
                     "scripts/inventory_numerical_descriptions.py"):
            with self.subTest(path=name):
                self.assertFalse(policy.excluded_source(Path(name)))


if __name__ == "__main__":
    unittest.main()
