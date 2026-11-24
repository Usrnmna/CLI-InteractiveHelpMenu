"""Check the six cloud leaf menus against their manuals and historical CLI output."""
import json
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'cli_help'))
from command_paths import load_driver_registry, resolve_path

CAPTURE = json.loads((ROOT / 'tests/fixtures/help/followup-cloud-captured.json').read_text(encoding='utf-8'))
INVENTORY = json.loads((ROOT / 'tests/fixtures/cloud-manual/inventory.json').read_text(encoding='utf-8'))


def option_rows(command):
    """Read every selectable profile row in file order for an exact command."""
    profile = json.loads((ROOT / 'profiles' / (command.replace(' ', '-') + '.json')).read_text(encoding='utf-8'))
    return [row for category in profile['categories'] for row in category['options']]


class CloudCaptureTests(unittest.TestCase):
    def test_every_curated_flag_has_leaf_or_explicit_global_documentation(self):
        """Require a documented spelling in captured leaf or inherited help."""
        self.assertEqual({' '.join(case['command']) for case in CAPTURE['cases']}, set(INVENTORY['commands']))
        for case in CAPTURE['cases']:
            command = ' '.join(case['command'])
            text = case['text']
            if case['command'][0] == 'gcloud':
                text += '\n' + CAPTURE['gcloud_global_help']['text']
            declarations = '\n'.join(line for line in text.splitlines() if re.match(r'^\s+-[A-Za-z-]', line))
            for option in option_rows(command):
                flag = option['flag']
                with self.subTest(command=command, flag=flag):
                    if flag == '--no-user-output-enabled':
                        # Google documents this spelling in the positive flag's body.
                        self.assertIn('Use --no-user-output-enabled to disable.', text)
                    else:
                        self.assertRegex(declarations, r'(?<![\w-])' + re.escape(flag) + r'(?![\w-])')

    def test_curated_arity_matches_independently_reviewed_cloud_syntax(self):
        """Require every documented spelling and exactly one operand for valued flags."""
        for command, groups in INVENTORY['commands'].items():
            expected = {}
            for group in INVENTORY[command.split()[0]] + groups:
                for flag in group.rstrip('=').split():
                    self.assertNotIn(flag, expected)
                    expected[flag] = int(group.endswith('='))
            options = option_rows(command)
            with self.subTest(command=command):
                self.assertCountEqual([row['flag'] for row in options], expected.keys())
            for row in options:
                with self.subTest(command=command, flag=row['flag']):
                    self.assertFalse(row.get('argument_optional', False))
                    arity = row.get('argument_count', 1) if row.get('argument') else 0
                    self.assertEqual(arity, expected[row['flag']])
                    self.assertTrue(row.get('detail'))

    def test_storage_options_retain_command_specific_meanings(self):
        """Distinguish leaf formatting, server-side filters and SDK validator behavior."""
        google = {row['flag']: row for row in option_rows('gcloud storage ls')}
        self.assertIn('--json', google['--format']['detail'])
        self.assertIn('Buckets and folders still appear.', google['--metadata-filter']['detail'])
        azure = {row['flag']: row for row in option_rows('az storage blob list')}
        self.assertIn('does not forward', azure['--include']['detail'])
        self.assertIn('Pagination can take longer.', azure['--timeout']['detail'])

    def test_gcloud_accepts_nonterminal_globals_before_the_leaf(self):
        """Treat global operands as data even when their text resembles a command."""
        registry = load_driver_registry(ROOT / 'config/drivers.example')
        for flag in ('--access-token-file', '--billing-project', '--flags-file', '--flatten', '--trace-token'):
            with self.subTest(flag=flag):
                path = resolve_path(['gcloud', flag, 'storage', 'config', 'list'], [], registry)
                self.assertEqual(path.words, ('gcloud', 'config', 'list'))
        for flag in ('--no-user-output-enabled', '--user-output-enabled', '--log-http'):
            with self.subTest(flag=flag):
                path = resolve_path(['gcloud', flag, 'storage', 'ls'], [], registry)
                self.assertEqual(path.words, ('gcloud', 'storage', 'ls'))


if __name__ == '__main__':
    unittest.main()
