"""Ansible's fixed UTF-8 probes preserve pending-workload isolation."""

import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from test_discovery import write_executable
from discovery import run_probe


@unittest.skipUnless(os.name == "posix", "Linux executable fixtures")
class AnsibleProbeLocaleTests(unittest.TestCase):
    def test_help_and_version_receive_fixed_locale_without_pending_operands(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            executable = folder / "ansible-playbook"
            marker = folder / "workload-executed"
            write_executable(executable,
                "import json, os, pathlib, sys\n"
                "if sys.argv[1:] not in [['--help'], ['--version']]:\n"
                f"    pathlib.Path({str(marker)!r}).write_text('unsafe request')\n"
                "print(json.dumps({'argv': sys.argv[1:], 'env': dict(os.environ)}))\n")
            for request in ("--help", "--version"):
                with patch.dict(os.environ, {"LC_ALL": "bad-locale", "LANG": "bad-locale",
                                             "CLI_HELP_LINE": "ansible-playbook private.yml --check",
                                             "ANSIBLE_CONFIG": "private.cfg"}):
                    record = json.loads(run_probe([str(executable), request], 2))
                self.assertEqual(record["argv"], [request])
                self.assertEqual(record["env"]["LC_ALL"], "C.UTF-8")
                self.assertEqual(record["env"]["LANG"], "C.UTF-8")
                self.assertNotIn("CLI_HELP_LINE", record["env"])
                self.assertNotIn("ANSIBLE_CONFIG", record["env"])
                self.assertFalse(marker.exists())
            other = folder / "other-tool"
            write_executable(other, "import os; print(os.environ['LC_ALL'])\n")
            self.assertEqual(run_probe([str(other), "--help"], 2).strip(), "C")


if __name__ == "__main__":
    unittest.main()
