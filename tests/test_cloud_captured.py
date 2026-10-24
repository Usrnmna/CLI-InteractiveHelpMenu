"""Check all curated cloud options against versioned leaf documentation."""
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
CAPTURE = json.loads((ROOT / 'tests/fixtures/help/followup-cloud-captured.json').read_text(encoding='utf-8'))

# Independently reviewed value-taking options; all other curated entries are switches.
VALUE_FLAGS = {
    'az account show': {'-s', '--subscription', '-o', '--output', '--query'},
    'az vm list': {'-g', '--resource-group', '-o', '--output', '--query', '--subscription'},
    'az storage blob list': {'-c', '--container-name', '--account-name', '--auth-mode', '--prefix',
                             '--num-results', '--marker', '--include', '--delimiter', '-o', '--output',
                             '--query', '--subscription'},
    'gcloud config list': {'--format', '--project', '--configuration', '--account', '--verbosity'},
    'gcloud compute instances list': {'--filter', '--limit', '--sort-by', '--zones', '--page-size',
                                      '--format', '--project', '--configuration', '--account', '--verbosity'},
    'gcloud storage ls': {'--format', '--project', '--configuration', '--account', '--verbosity'},
}


class CloudCaptureTests(unittest.TestCase):
    def test_every_curated_flag_has_leaf_or_explicit_global_documentation(self):
        """Reject options that only appear inside examples or unrelated prose."""
        self.assertEqual({' '.join(case['command']) for case in CAPTURE['cases']}, set(VALUE_FLAGS))
        for case in CAPTURE['cases']:
            profile = json.loads((ROOT / 'profiles' / ('-'.join(case['command']) + '.json')).read_text())
            text = case['text']
            if case['command'][0] == 'gcloud':
                text += '\n' + CAPTURE['gcloud_global_help']['text']
            declarations = '\n'.join(line for line in text.splitlines() if re.match(r'^\s+--[a-z]', line))
            for category in profile['categories']:
                for option in category['options']:
                    with self.subTest(command=case['command'], flag=option['flag']):
                        self.assertRegex(declarations, r'(?<![\w-])' + re.escape(option['flag']) + r'(?![\w-])')

    def test_curated_arity_matches_independently_reviewed_cloud_syntax(self):
        """Keep expression values and comma-separated lists as single arguments."""
        for command, valued in VALUE_FLAGS.items():
            profile = json.loads((ROOT / 'profiles' / (command.replace(' ', '-') + '.json')).read_text())
            options = {option['flag']: option for category in profile['categories'] for option in category['options']}
            self.assertEqual({flag for flag, option in options.items() if option.get('argument')}, valued)
            for flag, option in options.items():
                with self.subTest(command=command, flag=flag):
                    self.assertFalse(option.get('argument_optional', False))
                    if flag in valued:
                        self.assertEqual(option.get('argument_count', 1), 1)


if __name__ == '__main__':
    unittest.main()
