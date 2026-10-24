"""Independent route, arity, privacy, and literal-edit contracts for ordinary workflows."""

import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'cli_help'))
from command_paths import help_route, load_driver_registry, resolve_path
from core import HelpError, find_context, insert_option, validate_profile
from diagnostics import doctor, explain
from discovery import Settings, build_profile, discover, parse_help
from drivers import parse_driver

FIXTURES = ROOT / 'tests/fixtures/help'
CASES = json.loads((FIXTURES / 'workflow-baseline.json').read_text())
CAPTURES = json.loads((FIXTURES / 'workflow-baseline-captured.json').read_text())
REGISTRY = load_driver_registry(ROOT / 'config/drivers.example')


def profile_for(command):
    """Parse the recorded help, independently of installed programs and static profiles."""
    case = next(case for case in CASES if case['command'] == command)
    return build_profile(command.split(), [('capture', (FIXTURES / case['fixture']).read_text())])


def options_for(profile):
    return {option['flag']: option for category in profile['categories'] for option in category['options']}


def expected_help_route(words):
    """Specify reviewed requests independently of driver loading and discovery."""
    if words[0] == 'git':
        return (), '-'.join(words)
    if words[0] == 'docker':
        return (*words[1:], '--help'), None
    if words[0] in ('gh', 'kubectl'):
        return ('help', *words[1:]), None
    return ('--help',), words[0]


class WorkflowCorpusTests(unittest.TestCase):
    def test_inventory_provenance_and_matrix_are_complete(self):
        expected = {'git ' + leaf for leaf in ('status', 'show', 'fetch', 'switch')}
        expected.update('docker compose ' + leaf for leaf in ('ps', 'config', 'build', 'pull', 'down', 'run'))
        expected.update('kubectl ' + leaf for leaf in ('apply', 'delete', 'exec', 'port-forward'))
        expected.update('gh ' + parent + ' ' + leaf for parent in ('issue', 'run', 'workflow') for leaf in ('list', 'view'))
        expected.update('cp mv rm sort head tail du df sed gzip xz'.split())
        self.assertEqual({case['command'] for case in CASES}, expected)
        self.assertEqual(set(CAPTURES), expected)
        matrix = json.loads((FIXTURES / 'matrix.json').read_text())
        self.assertEqual(len(matrix), len({case['command'] for case in matrix}))
        self.assertEqual({case['command'] for case in matrix if case.get('expansion') == 'workflow-baseline'}, expected)
        for case in CASES:
            with self.subTest(command=case['command']):
                evidence = CAPTURES[case['command']]
                self.assertEqual(evidence['kind'], 'installed-capture')
                self.assertTrue(evidence['source_url'].startswith('https://'))
                self.assertTrue(evidence['version'])
                self.assertEqual(evidence['fixture'], case['fixture'])
                self.assertEqual(resolve_path(case['command'].split(), [], REGISTRY).words, tuple(case['command'].split()))

    def test_captures_match_independent_flags_arity_and_exclusions(self):
        for case in CASES:
            with self.subTest(command=case['command']):
                profile = profile_for(case['command'])
                validate_profile(profile, Path('capture'))
                options = options_for(profile)
                for flag, argument in case['flags'].items():
                    self.assertIn(flag, options)
                    self.assertEqual(options[flag]['argument'], argument, flag)
                    self.assertEqual(options[flag].get('argument_count', 1), 1, flag)
                    self.assertEqual(options[flag].get('argument_optional', False), flag in case['optional'], flag)
                self.assertFalse(set(case['excluded']) & set(options))

    def test_required_values_and_each_literal_insertion(self):
        for case in CASES:
            profile = profile_for(case['command'])
            for flag, argument in case['flags'].items():
                with self.subTest(command=case['command'], flag=flag):
                    prefix = case['command'] + '  '
                    line = prefix + '--' + "\t'café file'  suffix"
                    context = find_context(line, len(prefix) + 2, [profile], driver_registry=REGISTRY)
                    expected = prefix + flag + "\t'café file'  suffix"
                    point = len(prefix + flag) + int(not flag.endswith('='))
                    self.assertEqual(insert_option(context, options_for(profile)[flag]), (expected, point))
                    if argument and flag not in case['optional']:
                        pending = case['command'] + ' ' + flag.rstrip('=') + ' '
                        with self.assertRaises(HelpError) as raised:
                            find_context(pending, len(pending), [profile], driver_registry=REGISTRY)
                        self.assertEqual(raised.exception.code, 'option_value_required')

    def test_fixed_routes_are_independent_of_pending_operands(self):
        for case in CASES:
            words = case['command'].split()
            with self.subTest(command=words):
                route = help_route(words[0], tuple(words[1:]), REGISTRY)
                expected_help, expected_manual = expected_help_route(words)
                self.assertEqual(route.arguments, expected_help)
                self.assertEqual(route.manual, expected_manual)
                calls = []
                def probe(argv, timeout, **kwargs):
                    calls.append(argv)
                    return (FIXTURES / case['fixture']).read_text()
                def executable(name):
                    return '/fixed/man' if name == 'man' and words[0] == 'git' else None if name == 'man' else '/fixed/' + name
                with patch('discovery.shutil.which', side_effect=executable), patch('discovery.run_probe', side_effect=probe), \
                     patch('discovery.executable_identity', return_value={'fixture': True}):
                    profile = discover(words[0], Settings(cache_ttl=0), subcommands=tuple(words[1:]), driver_registry=REGISTRY)
                if words[0] == 'git':
                    expected_argv = ['/fixed/man', '-P', '/bin/cat', '--no-hyphenation', '--no-justification',
                                     '-s', '1:8', '--', expected_manual]
                else:
                    expected_argv = ['/fixed/' + words[0], *expected_help]
                self.assertEqual(calls, [expected_argv])
                lookup = Mock(return_value=profile)
                line = case['command'] + ' --'
                find_context(line, len(line), [], discover=lookup, driver_registry=REGISTRY)
                expected_kwargs = {'subcommands': tuple(words[1:])} if len(words) > 1 else {}
                lookup.assert_called_once_with(words[0], **expected_kwargs)

    def test_literal_workflows_preserve_independent_prefix_suffix_and_cursor(self):
        # @ denotes the character cursor, not shell syntax.
        cases = [
            ('git status', "git -C 'café dir' status --sh@  -- 'private file'", '--short', "git -C 'café dir' status --short @ -- 'private file'"),
            ('git fetch', "git -c key=value fetch --depth=2 --pr@ origin", '--prune', "git -c key=value fetch --depth=2 --prune @origin"),
            ('docker compose build', "docker --context local compose -f a.yml -f='café.yml' --profile debug build --build-arg A=one --build-arg=B=two --no-c@ web", '--no-cache', "docker --context local compose -f a.yml -f='café.yml' --profile debug build --build-arg A=one --build-arg=B=two --no-cache @web"),
            ('docker compose run', "docker compose run --env A=one --env=B=two --r@ web sh -c 'printf test'", '--rm', "docker compose run --env A=one --env=B=two --rm @web sh -c 'printf test'"),
            ('kubectl apply', "kubectl -n demo apply --filename=a.yml -f 'café.yml' --server-s@", '--server-side', "kubectl -n demo apply --filename=a.yml -f 'café.yml' --server-side @"),
            ('kubectl delete', 'kubectl delete --grace-period -1 --wa@', '--wait', 'kubectl delete --grace-period -1 --wait @'),
            ('kubectl exec', 'kubectl exec pod --namespace demo -c app --tt@ -- sh -c echo', '--tty', 'kubectl exec pod --namespace demo -c app --tty @-- sh -c echo'),
            ('gh issue list', "gh issue -R owner/repo list --label bug --label='help wanted' --json number,title --li@", '--limit', "gh issue -R owner/repo list --label bug --label='help wanted' --json number,title --limit @"),
            ('gh run view', 'gh run view 42 --attempt=2 --log-f@', '--log-failed', 'gh run view 42 --attempt=2 --log-failed @'),
            ('cp', "cp -t 'café dir' --back@ 'source file'", '--backup', "cp -t 'café dir' --backup @'source file'"),
            ('cp', "cp 'first file' 'second file' --arch@ 'target dir'", '--archive', "cp 'first file' 'second file' --archive @'target dir'"),
            ('mv', 'mv -t out --back@ a b', '--backup', 'mv -t out --backup @a b'),
            ('rm', "rm --interactive=once --recur@ 'café dir'", '--recursive', "rm --interactive=once --recursive @'café dir'"),
            ('sort', "sort --key=2,2 --key=1,1 --field-separator=, --num@ 'café.csv'", '--numeric-sort', "sort --key=2,2 --key=1,1 --field-separator=, --numeric-sort @'café.csv'"),
            ('head', "head -n -5 --qu@ 'café.txt'", '--quiet', "head -n -5 --quiet @'café.txt'"),
            ('tail', 'tail --lines=+5 --follow=name --pi@', '--pid=', 'tail --lines=+5 --follow=name --pid=@'),
            ('du', "du --max-depth=2 --human-r@ 'café dir'", '--human-readable', "du --max-depth=2 --human-readable @'café dir'"),
            ('df', 'df --output=source,target --ty@', '--type=', 'df --output=source,target --type=@'),
            ('sed', "sed -e 's/a b/café/g' --expression='s/x/y/g' --qu@  'source file'", '--quiet', "sed -e 's/a b/café/g' --expression='s/x/y/g' --quiet @ 'source file'"),
            ('gzip', 'gzip --keep --suf@', '--suffix=', 'gzip --keep --suffix=@'),
            ('xz', "xz --threads=2 --ke@ 'café.xz'", '--keep', "xz --threads=2 --keep @'café.xz'"),
        ]
        for command, marked, flag, expected in cases:
            with self.subTest(command=command):
                point = marked.index('@')
                line = marked.replace('@', '')
                profile = profile_for(command)
                context = find_context(line, point, [profile], driver_registry=REGISTRY)
                self.assertEqual(insert_option(context, options_for(profile)[flag]), (expected.replace('@', ''), expected.index('@')))

    def test_values_expressions_and_end_markers_reject_edits(self):
        cases = [('head', 'head -n ', 'option_value_required'), ('head', 'head --lines=-5@', 'cursor_in_value'),
                 ('sed', "sed -e 's/a/--quiet/g'@", 'cursor_in_operand'),
                 ('sed', 'sed -i.bak@ file', 'cursor_in_value'),
                 ('cp', 'cp -- -private --@', 'end_of_options'),
                 ('sort', 'sort -- file --@', 'end_of_options'),
                 ('kubectl exec', 'kubectl exec pod -- sh --@', 'end_of_options'),
                 ('kubectl exec', 'kubectl exec pod --namespace @', 'option_value_required'),
                 ('docker compose run', 'docker compose run web sh --@', 'child_argument_boundary'),
                 ('docker compose run', 'docker compose run --mystery value --@', 'unsupported_option')]
        cases.extend((name, name + " -- '-private file' --@", 'end_of_options')
                     for name in 'cp mv rm sort head tail du df sed gzip xz'.split())
        for command, marked, reason in cases:
            point = marked.index('@') if '@' in marked else len(marked)
            line = marked.replace('@', '')
            with self.subTest(line=line), self.assertRaises(HelpError) as raised:
                find_context(line, point, [profile_for(command)], driver_registry=REGISTRY)
            self.assertEqual(raised.exception.code, reason)

    def test_route_cursor_boundaries_and_inherited_values(self):
        profile = profile_for('gh issue list')
        line = 'gh issue -R owner/repo list --li'
        for point in (line.index('list') + 1, line.index('owner') + 2):
            with self.subTest(point=point), self.assertRaises(HelpError):
                find_context(line, point, [profile], driver_registry=REGISTRY)
        self.assertEqual(find_context(line, len(line), [profile], driver_registry=REGISTRY).profile, profile)
        for command in ('kubectl apply', 'kubectl delete', 'kubectl exec', 'kubectl port-forward'):
            profile = profile_for(command)
            for suffix in (' --namespace demo --', ' --namespace=demo --', ' -ndemo --'):
                pending = command + suffix
                self.assertEqual(find_context(pending, len(pending), [profile], driver_registry=REGISTRY).query, '--')
            for suffix in (' --namespace ', ' --context '):
                pending = command + suffix
                with self.assertRaises(HelpError) as raised:
                    find_context(pending, len(pending), [profile], driver_registry=REGISTRY)
                self.assertEqual(raised.exception.code, 'option_value_required')

    def test_partial_placeholders_and_numeric_ranges_are_not_truncated(self):
        for declaration in ('-0 ... -9  Compression range', '-0 … -9  Compression range'):
            self.assertEqual(parse_help('Options:\n  ' + declaration, 'fixture'), [])
        options = options_for(build_profile('tool', [('fixture', 'Options:\n  -R, --repo [HOST/]OWNER/REPO  Select repository\n  -1, --fast  Fast compression\n')]))
        self.assertEqual(options['--repo']['argument'], '[HOST/]OWNER/REPO')
        self.assertFalse(options['--repo']['argument_optional'])
        self.assertIn('-1', options)

    def test_manual_examples_and_numeric_tables_do_not_override_declarations(self):
        evidence = json.loads((FIXTURES / 'workflow-manual-edge-cases.json').read_text())
        pretty = options_for(build_profile(['git', 'show'], [('man', evidence['git-show']['text'])]))
        self.assertEqual(pretty['--pretty']['argument'], '[=<format>]')
        self.assertTrue(pretty['--pretty']['argument_optional'])
        self.assertNotIn('--pretty=', pretty)
        xz = options_for(build_profile('xz', [('man', evidence['xz']['text'])]))
        self.assertEqual(set(xz), {'--best'})
        self.assertEqual(xz['--best']['argument'], '')
        self.assertEqual(parse_help("Options:\n  --format='incomplete example  prose\n", 'fixture'), [])
        aliases = options_for(build_profile('tool', [('fixture', 'Options:\n  --fast or --quick  Select speed\n')]))
        self.assertEqual(set(aliases), {'--fast', '--quick'})


class DriverActivationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.folder = Path(self.temporary.name)
        self.environment = patch.dict(os.environ, {
            'CLI_HELP_DRIVERS': '', 'CLI_HELP_PROFILES': '', 'CLI_HELP_CONFIG': '',
            'CLI_HELP_DISCOVERY': 'off', 'CLI_HELP_CACHE_DIR': str(self.folder / 'absent'),
        })
        self.environment.start()
        self.addCleanup(self.environment.stop)

    def test_default_and_explicit_selection_preserve_precedence(self):
        report = doctor(ROOT)
        selection = report['configuration']['driver_selection']
        self.assertEqual(selection['source'], 'built_in')
        self.assertFalse(selection['supplied_selected'])
        self.assertIsNone(selection['directory'])
        with patch.dict(os.environ, {'CLI_HELP_DRIVERS': str(ROOT / 'config/drivers.example')}):
            self.assertTrue(doctor(ROOT)['configuration']['driver_selection']['supplied_selected'])
            line = 'docker compose ps --'
            explanation = explain(ROOT, line, len(line))
            self.assertEqual(explanation['route']['kind'], 'configured')
            self.assertEqual(explanation['route']['file'], str(ROOT / 'config/drivers.example/docker.json'))
            self.assertEqual(explanation['route']['help_arguments'], ['compose', 'ps', '--help'])
            line = 'git status --'
            self.assertEqual(explain(ROOT, line, len(line))['route']['kind'], 'built_in')

    def test_manual_combination_and_same_executable_overlay_are_explicit(self):
        supplied = json.loads((ROOT / 'config/drivers.example/docker.json').read_text())
        supplied['paths'].append({'command':['custom'], 'help':['help','custom'], 'man':None})
        (self.folder / 'docker.json').write_text(json.dumps(supplied))
        (self.folder / 'tool.json').write_text(json.dumps({'command':'local-tool','paths':[{'command':[], 'help':['--help']}]}))
        registry = load_driver_registry(self.folder)
        self.assertEqual(help_route('docker', ('compose','ps'), registry).arguments, ('compose','ps','--help'))
        self.assertEqual(help_route('docker', ('custom',), registry).source, str(self.folder / 'docker.json'))
        self.assertEqual(help_route('docker', ('image','ls'), registry).source, None)
        self.assertIn('--context', registry['docker'].global_values)
        with patch.dict(os.environ, {'CLI_HELP_DRIVERS': str(self.folder)}):
            self.assertFalse(doctor(ROOT)['configuration']['driver_selection']['supplied_selected'])
            self.assertEqual(doctor(ROOT)['configuration']['driver_selection']['directory'], str(self.folder))

    def test_duplicate_executables_routes_and_global_arity_conflicts_fail(self):
        document = {'command':'git','paths':[{'command':['status'],'help':['help','status']}]}
        for filename in ('one.json','two.json'):
            (self.folder / filename).write_text(json.dumps(document))
        with self.assertRaises(HelpError):
            load_driver_registry(self.folder)
        (self.folder / 'two.json').unlink()
        document['global_flags'] = ['-C']
        (self.folder / 'one.json').write_text(json.dumps(document))
        with self.assertRaises(HelpError):
            load_driver_registry(self.folder)
        document.pop('global_flags')
        document['paths'] *= 2
        with self.assertRaises(ValueError):
            parse_driver(document)
        document['paths'] = document['paths'][:1]
        document['paths'][0]['source'] = 'untrusted'
        with self.assertRaises(ValueError):
            parse_driver(document)
        with patch.dict(os.environ, {'CLI_HELP_DRIVERS': str(self.folder)}):
            self.assertEqual(doctor(ROOT)['configuration']['status'], 'invalid')

    def test_passive_reporting_omits_secrets_and_performs_no_processes_or_writes(self):
        original_open = io.open
        def read_only(file, mode='r', *args, **kwargs):
            self.assertFalse(any(character in mode for character in 'wax+'))
            return original_open(file, mode, *args, **kwargs)
        with patch.dict(os.environ, {'CLI_HELP_DRIVERS': str(ROOT / 'config/drivers.example')}), \
             patch('subprocess.Popen', side_effect=AssertionError('target process')), \
             patch('os.mkdir', side_effect=AssertionError('write')), patch('os.replace', side_effect=AssertionError('write')), \
             patch('discovery.write_cache', side_effect=AssertionError('write')), patch('io.open', side_effect=read_only):
            reports = [doctor(ROOT)]
            for line in ('gh issue -R PRIVATE_SENTINEL list --', 'kubectl exec pod --namespace PRIVATE_SENTINEL --', 'docker compose -f PRIVATE_SENTINEL run --', 'kubectl --token=PRIVATE_SENTINEL exec --'):
                reports.append(explain(ROOT, line, len(line)))
        self.assertNotIn('PRIVATE_SENTINEL', json.dumps(reports))
        self.assertFalse((self.folder / 'absent').exists())


if __name__ == '__main__':
    unittest.main()
