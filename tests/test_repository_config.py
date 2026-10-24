"""Protect private local artifacts while keeping maintained repository inputs visible."""

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which("git"), "Ignore-policy checks require Git")
class RepositoryIgnoreTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="cli-help-ignore-")
        self.addCleanup(self.temporary.cleanup)
        self.folder = Path(self.temporary.name)
        self.environment = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
        self.environment.update({"HOME": str(self.folder), "XDG_CONFIG_HOME": str(self.folder / ".config"),
                                 "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
                                 "GIT_TERMINAL_PROMPT": "0"})
        shutil.copyfile(ROOT / ".gitignore", self.folder / ".gitignore")
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
        ], True)

    def test_reports_caches_and_owned_temporary_artifacts_are_ignored(self):
        self.assert_policy([
            "tests/reports/review/diagnostics.json", ".cache/tool/archive.tar.gz", ".lycheecache",
            "generated-help/profiles/generated.json", "cli-help-probe-session/output", "cli-help-review-session/draft.json",
            "cli-help-screen-session/tmux.sock", "cli-help-build-session/cli-help", "cli-help-media-session/raw.cast",
            ".cli-help-rc-session", ".review-state-session", ".cli-help-install.json", "cli-help",
            "collection/.scan.lock", "collection/.import.lock", "collection/.review-backups/backup.json",
        ], True)

    def test_source_fixtures_templates_and_public_assets_remain_visible(self):
        self.assert_policy([
            "cli_help/diagnostics.py", "profiles/ssh.json", "config/drivers.example/docker.json",
            "tests/fixtures/help/captured.json", "tests/test_repository_config.py", "docs/diagnostics.md",
            "docs/assets/option-insertion.gif", "releases/v0.1.1-alpha/cli-help-v0.1.1-alpha-linux-x86_64",
            ".github/workflows/ci.yml", ".github/ISSUE_TEMPLATE/bug_report.yml", ".github/pull_request_template.md",
            ".env.example", ".env.development.sample", "config/ssh.example", "examples/project/.env.template",
        ], False)


if __name__ == "__main__":
    unittest.main()
