"""Record target selection, lifecycle and argv in a disposable package using supplied Bun binaries."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile


def probe(binary):
    """Run each local target through Bun, checking its identity and complete argument vector."""
    binary = Path(binary).resolve()
    with tempfile.TemporaryDirectory() as scratch:
        root = Path(scratch)
        env = {"HOME": scratch, "PATH": "/usr/bin:/bin", "BUN_INSTALL_CACHE_DIR": str(root / "cache")}
        bindir = root / "node_modules/.bin"
        bindir.mkdir(parents=True)
        (root / "record.py").write_text("import json, sys\nprint(json.dumps(sys.argv[1:]))\n")
        (root / "task.js").write_text('console.log(JSON.stringify(["file", ...process.argv.slice(2)]))')
        exe = bindir / "task.js"
        exe.write_text('#!/bin/sh\nexec python3 record.py executable "$@"\n')
        exe.chmod(0o700)
        manifest = root / "package.json"
        manifest.write_text(json.dumps({"scripts": {"pretask.js": "python3 record.py pre",
            "task.js": "python3 record.py script", "posttask.js": "python3 record.py post"}}))
        version = subprocess.check_output([binary, "--version"], cwd=root, env=env, text=True).strip()
        def run(*args):
            """Read the child markers, using a private working directory and fixed local PATH."""
            result = subprocess.run([binary, "run", *args], cwd=root, env=env, text=True, capture_output=True)
            print(version, list(args), result.returncode, result.stdout.strip(), result.stderr.strip(), flush=True)
            return result.returncode, [json.loads(line) for line in result.stdout.splitlines()]
        tail = ["two words", "--watch"]
        assert run("--silent", "task.js", *tail) == (0, [["pre"], ["script", *tail], ["post"]])
        expected_script = (0, [["pre"], ["script", *tail], ["post"]])
        assert run("--silent", "--", "task.js", *tail) == expected_script
        assert run("--silent", "task.js", "--", *tail) == expected_script
        assert run("./task.js", "--", *tail) == (0, [["file", *tail]])
        assert run("./task.js", *tail) == (0, [["file", *tail]])
        manifest.write_text("{}")
        assert run("task.js", *tail) == (0, [["file", *tail]])
        (root / "task.js").unlink()
        assert run("task.js", *tail) == (0, [["executable", *tail]])


if __name__ == "__main__":
    for path in sys.argv[1:]:
        probe(path)
