"""Probe read-only listing syntax in a project sandbox with private loopback."""

import json
import socket
import subprocess
import sys
import tempfile
from pathlib import Path


def run(tool, *arguments):
    """Capture the packaged client's status and output without shell expansion."""
    return subprocess.run([tool, *arguments], capture_output=True, check=False)


def main():
    """Use sandbox-local client paths; create one disposable TCP listener for ss."""
    ip, ss = sys.argv[1:]
    version = run(ip, '-Version').stdout.decode().strip()
    noble = '6.1.0' in version
    assert noble or '6.19.0' in version, version
    assert version.split('iproute2-')[1].split(',')[0] in run(ss, '-V').stdout.decode()
    print(version)
    for obj in ('address', 'link', 'route'):
        for alias in ('list', 'lst'):
            assert run(ip, obj, alias).stdout == run(ip, obj, 'show').stdout
    for obj in ('address', 'link'):
        for word in ('down', 'novf'):
            result = run(ip, obj, 'show', word)
            assert (result.returncode == 0) == (not noble), (obj, word, result)
            if noble:
                assert b'does not exist' in result.stderr
    assert (run(ip, 'address', 'show', 'proto', '0').returncode == 0) == (not noble)
    assert run(ip, 'address', 'show', 'proto', 'kernel_lo').returncode
    flags = 'secondary temporary nodad optimistic dadfailed home deprecated tentative permanent mngtmpaddr noprefixroute autojoin stable-privacy dynamic primary'
    for flag in flags.split():
        for selector in (flag, '-' + flag):
            assert run(ip, 'address', 'show', selector).returncode == 0, selector
    for keyword, operand in [('tos','10'), ('dsfield','ff'), ('realms','1/'), ('realm','1'), ('realm','1/2'), ('realm','1/'), ('realm','0x10002'), ('mark','0'), ('metric','0'), ('priority','0'), ('preference','0'), ('iif','lo'), ('oif','lo')]:
        assert run(ip, 'route', 'show', keyword, operand).returncode == 0, (keyword, operand)
        assert run(ip, 'route', 'show', keyword).returncode != 0
    assert run(ip, 'route', 'show', 'tos', '100').returncode != 0
    assert run(ip, 'route', 'show', 'preference', 'low').returncode != 0
    expected = run(ip, '-4', 'route', 'show', 'table', 'local', 'to', 'root', '127.0.0.0/8')
    assert expected.returncode == 0 and b'lo' in expected.stdout
    assert run(ip, '-4', 'route', 'list', 'table', 'local', 'root', '127.0.0.0/8').stdout == expected.stdout
    print('Listing aliases, address flags and their inverses, release-specific filters and numeric route selectors passed.')
    for opt in ('--no-queues','--bound-inactive','--bpf-maps'):
        result = run(ss, opt, '--version')
        assert (result.returncode == 0) == (not noble), (opt, result)
    invalid_id = run(ss, '--bpf-map-id=0')
    expected_error = b'unrecognized option' if noble else b'invalid BPF map ID'
    assert invalid_id.returncode and expected_error in invalid_id.stderr
    assert run(ss, '-v').stdout == run(ss, '--version').stdout
    assert run(ss, '-d', '--version').returncode == 0
    for family in ['inet','inet6','link','unix','netlink','vsock','tipc','xdp']:
        assert run(ss, '--family=' + family, '-V').returncode == 0
    for table in ['all','inet','unix','packet','vsock','p_raw','u_seq','v_dgr','dccp','tipc']:
        assert run(ss, '--query=' + table, '-V').returncode == 0
    with socket.socket() as listener, tempfile.TemporaryDirectory() as folder:
        listener.bind(('127.0.0.1', 0))
        listener.listen()
        port = listener.getsockname()[1]
        result = run(ss, '-Hln', '--socket=tcp', 'sport', '=', ':' + str(port))
        assert result.returncode == 0 and str(port).encode() in result.stdout
        assert b'python' in run(ss, '-HlnpT', '-t', 'sport', '=', ':' + str(port)).stdout
        # The raw-dump branch precedes expression parsing in all three tags.
        dest = Path(folder, 'tcp.dump')
        result = run(ss, '-ltn', '--diag=' + str(dest), 'this-is-not-an-expression')
        assert result.returncode == 0 and dest.stat().st_size > 0, result
        assert run(ss, '-ltn', 'this-is-not-an-expression').returncode != 0
        threads_alone = run(ss, '-HlnT', '-t', 'sport', '=', ':' + str(port))
        assert (b'python' in threads_alone.stdout) == noble, threads_alone
        print('Threads with -T alone include process name:', noble)
    print('Socket table aliases, family names, BPF parser availability, owned TCP selection and raw dump behavior passed.')
    for obj in ('address','link','route','ss'):
        result = run(ss, '--help') if obj == 'ss' else run(ip, obj, 'help')
        print(json.dumps({'object':obj, 'version':version, 'help':(result.stdout + result.stderr).decode()}))


if __name__ == '__main__':
    main()
