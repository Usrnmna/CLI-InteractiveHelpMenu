"""Build deterministic Linux release archives, a native launcher, and SHA-256 files."""

import argparse
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import tarfile
import tempfile


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIRECTORIES = ("bash", "cli_help", "config", "docs", "native", "profiles", "scripts", "tests", "tools", ".github")
SOURCE_FILES = ("VERSION", "README.md", "CHANGELOG.md", "install.sh", "uninstall.sh", "update.sh",
                "review-update.sh", "update-from-github.sh", ".gitignore", ".gitattributes", ".editorconfig", "lychee.toml")


def source_files(root):
    """Select maintained source, documentation, and fixtures without local reports or caches."""
    files = [root / name for name in SOURCE_FILES]
    for directory in SOURCE_DIRECTORIES:
        files.extend(path for path in (root / directory).rglob("*")
                     if path.is_file() and not any(part in {"__pycache__", "reports"} for part in path.relative_to(root).parts)
                     and path.suffix not in {".pyc", ".pyo"})
    for path in files:
        if not path.is_file() or path.is_symlink():
            raise ValueError(f"Missing or symlinked release input: {path}")
        if any(parent.is_symlink() for parent in path.parents if root in parent.parents):
            raise ValueError(f"Symlinked release input directory: {path}")
    return sorted(files)


def archive(files, top):
    """Create a reproducible gzip/tar payload with normalized modes and timestamps."""
    result = io.BytesIO()
    with gzip.GzipFile(fileobj=result, mode="wb", mtime=0, filename="") as compressed:
        with tarfile.open(fileobj=compressed, mode="w") as bundle:
            for name, data in sorted(files.items()):
                member = tarfile.TarInfo(top + "/" + name)
                member.size = len(data)
                member.mode = 0o755 if name.endswith(".sh") or name == "cli-help" else 0o644
                member.mtime = 0
                bundle.addfile(member, io.BytesIO(data))
    return result.getvalue()


def installer(payload, top):
    """Wrap a verified runtime archive with an installer that forwards literal arguments."""
    checksum = hashlib.sha256(payload).hexdigest()
    header = f'''#!/usr/bin/env bash
# Self-extracting Linux installation package; inspect the source archive for implementation.
set -euo pipefail
if [[ ${{1:-}} == --help ]]; then
    printf '%s\\n' 'Usage: bash installer.run [install|update] [--prefix PATH] [installer options]' 'Use --verify to check the embedded archive without installing.'
    exit 0
fi
action=install
case "${{1:-}}" in
    install|update) action=$1; shift ;;
    --verify) action=verify; shift ;;
esac
stage=$(mktemp -d "${{TMPDIR:-/tmp}}/cli-help-installer.XXXXXXXX")
trap 'rm -rf -- "$stage"' EXIT
archive="$stage/runtime.tar.gz"
tail -n +PAYLOAD_LINE -- "$0" > "$archive"
printf '%s  %s\\n' '{checksum}' "$archive" | sha256sum -c - >/dev/null
if [[ $action == verify ]]; then
    printf '%s\\n' 'Embedded archive checksum verified.'
    exit 0
fi
tar --no-same-owner -xzf "$archive" -C "$stage"
status=0
bash "$stage/{top}/$action.sh" "$@" || status=$?
if [[ $status == 2 && $action == update ]]; then
    trap - EXIT
    printf 'Source retained for conflict review: %s\\n' "$stage/{top}"
fi
exit "$status"
'''
    header = header.replace("PAYLOAD_LINE", str(header.count("\n") + 1))
    return header.encode() + payload


def build(root, destination):
    """Compile the native convenience launcher and write complete versioned deliverables."""
    version = (root / "VERSION").read_text().strip()
    if not re.fullmatch(r"\d+\.\d+\.\d+(?:-[a-z0-9.]+)?", version):
        raise ValueError("VERSION must contain a simple semantic version.")
    if platform.system() != "Linux" or platform.machine() != "x86_64":
        raise ValueError("This release builder currently targets Linux x86_64.")
    if destination.exists():
        raise ValueError("The output directory already exists; select a new directory to preserve previous builds.")
    selected = source_files(root)
    contents = {path.relative_to(root).as_posix(): path.read_bytes() for path in selected}
    compiler = shutil.which(os.environ.get("CC", "gcc"))
    if not compiler:
        raise ValueError("A C compiler is required; install GCC or set CC to its executable.")
    with tempfile.TemporaryDirectory(prefix="cli-help-build-") as temporary:
        executable = Path(temporary) / "cli-help"
        subprocess.run([compiler, "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-Wl,--build-id=none", "-s",
                        f'-DCLI_HELP_VERSION="{version}"', str(root / "native/cli_help.c"), "-o", str(executable)], check=True)
        binary = executable.read_bytes()
        subprocess.run([str(executable), "--version"], check=True)
    base = f"cli-interactive-help-v{version}"
    top = base
    binary_name = f"cli-help-v{version}-linux-x86_64"
    runtime = archive({**contents, "cli-help": binary}, top)
    manifest = {name: hashlib.sha256(data).hexdigest() for name, data in contents.items()}
    info = {"version": version, "platform": "linux-x86_64", "python_required": "3.10+", "bash_required": "4.4+",
            "compiler": subprocess.check_output([compiler, "--version"], text=True).splitlines()[0],
            "build_platform": platform.platform(), "source_files": manifest}
    artifacts = {f"{base}-source.tar.gz": archive(contents, top),
                 f"{base}-linux-x86_64.tar.gz": runtime,
                 f"{base}-linux-x86_64.run": installer(runtime, top),
                 binary_name: binary,
                 "BUILD-INFO.json": (json.dumps(info, indent=2, sort_keys=True) + "\n").encode()}
    destination.mkdir(parents=True)
    checksums = []
    for name, data in artifacts.items():
        path = destination / name
        path.write_bytes(data)
        if name.endswith(".run") or name == binary_name:
            path.chmod(0o755)
        line = f"{hashlib.sha256(data).hexdigest()}  {name}\n"
        (destination / (name + ".checksum")).write_text(line, encoding="utf-8")
        checksums.append(line)
    (destination / "SHA256SUMS.checksum").write_text("".join(checksums), encoding="utf-8")
    return destination


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="New directory for release artifacts")
    args = parser.parse_args()
    try:
        print("Built release: " + str(build(ROOT, args.output.absolute())))
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"Build failed: {error}\n")


if __name__ == "__main__":
    main()
