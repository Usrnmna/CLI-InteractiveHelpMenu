"""Print fixed package-manager and Bash documentation as JSON in a prepared Ubuntu target."""

import json
import os
import subprocess


def capture(*argv):
    """Read successful documentation with a clean locale, fixed PATH and no shell startup files."""
    return subprocess.check_output(argv, text=True, timeout=10, stdin=subprocess.DEVNULL,
                                   env={"PATH": os.defpath, "LC_ALL": "C", "HOME": "/tmp",
                                        "MANWIDTH": "100", "PAGER": "cat"}).rstrip()


def main():
    """Preserve source editions and each builtin's complete help, including literal punctuation."""
    shell = ["/bin/bash", "--noprofile", "--norc", "-c"]
    builtins = capture(*shell, "compgen -b").splitlines()
    commands = "apt apt-cache apt-get apt-mark apt-config dpkg dpkg-query dpkg-deb".split()
    evidence = {
        "versions": [capture("/usr/bin/apt", "--version"), capture("/usr/bin/dpkg", "--version").splitlines()[0],
                     capture(*shell, 'printf "%s" "$BASH_VERSION"')],
        "bash": {name: capture(*shell, 'builtin help -- "$1"', "capture", name) for name in builtins},
        "help": {name: capture("/usr/bin/" + name, "--help") for name in commands},
    }
    print(json.dumps(evidence, sort_keys=True, ensure_ascii=True))


if __name__ == "__main__":
    main()
