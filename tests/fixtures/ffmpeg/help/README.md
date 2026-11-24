# FFmpeg executable fixtures

The [capture manifest](manifest.json) gives the exact argument list, build identity, byte count and SHA-256 of each uncompressed result. Each fixed help invocation ran with `LC_ALL=C` and merged standard output and standard error. Use `xz -dc noble-full.txt.xz` to read a complete capture. The version files include the build configuration and library ABI versions.

The Noble and Resolute captures come from the project's offline sandboxes and use the Ubuntu amd64 clients. The upstream capture uses the FFmpeg 9.1 release compiled on amd64 with GCC 15. The upstream build disables external library autodetection and networking. Its help therefore covers a different set of optional components. The release archive's detached signature verified against the FFmpeg release signing key. [FFmpeg release verification instructions](https://ffmpeg.org/download.html#release-verification) · [FFmpeg 9.1 release archive](https://ffmpeg.org/releases/ffmpeg-9.1.tar.xz) · [Build configuration](upstream-version.txt)

## Prepare the Noble client

The [Noble runtime checksums](noble-runtime.sha256) list 191 amd64 and architecture-independent packages resolved against the Noble test image. SHA-256 values were checked against the package indices authenticated by Ubuntu's archive key. Package preparation needs network access. Extraction uses private storage and runs no package installation scripts. Start in the repository root.

```bash
set -e
scratch=$(mktemp -d)
fixture_dir=tests/reports/ffmpeg-revisit
mkdir -p "$scratch/packages" "$scratch/root" "$fixture_dir"
while read -r digest package; do
    archive="$scratch/packages/${package##*/}"
    curl --fail --location --retry 2 \
        "https://archive.ubuntu.com/ubuntu/$package" --output "$archive"
    printf '%s  %s\n' "$digest" "$archive" | sha256sum --check --status
    dpkg-deb -x "$archive" "$scratch/root"
done < tests/fixtures/ffmpeg/help/noble-runtime.sha256
tar -C "$scratch/root" -czf "$fixture_dir/noble-runtime.tar.gz" \
    usr/bin/ffmpeg usr/bin/ffprobe usr/lib/x86_64-linux-gnu
```

An Ubuntu mirror can retire superseded dependency revisions. When a listed URL is unavailable, retrieve that exact pool path from an Ubuntu archive snapshot covering 2026-11-24 UTC and verify the same checksum before extraction. The Ubuntu ffmpeg package revision used here is `7:6.1.1-3ubuntu5`. [Ubuntu snapshots](https://snapshot.ubuntu.com/) · [Noble package record](https://packages.ubuntu.com/noble/ffmpeg)

## Run the generated-media checks

The suite creates one MPEG-4 video and two language-tagged audio streams in a temporary Matroska file. Both tools run in the project's isolated filesystem and network namespace. Choose either `noble310` or `noble312`. A local extracted runtime uses `FFMPEG_TEST_ROOT` and sets the shared library search path only for its own client processes.

```bash
python3 -I tests/run_sandbox.py --target noble312 \
    --include tests/reports/ffmpeg-revisit/noble-runtime.tar.gz -- \
    bash -ec '
        mkdir /tmp/ffmpeg-noble
        tar xzf tests/reports/ffmpeg-revisit/noble-runtime.tar.gz -C /tmp/ffmpeg-noble
        export FFMPEG_TEST_ROOT=/tmp/ffmpeg-noble
        python3 -m unittest discover -s tests -p test_ffmpeg_packaged.py -v
    '
```

The `host` target uses the installed Resolute clients from read-only `/usr`. Add `--include tests/test_ffmpeg_packaged.py` before the command separator when the test module is untracked. [Sandbox runner](../../../run_sandbox.py) · [Executable regressions](../../../test_ffmpeg_packaged.py)

## Optional upstream components

A second build of the same verified 9.1 release enabled libcurl, OpenSSL, libsmbclient, libsrt, libxml2 and libmodplug. The capture manifest lists this build separately. Its help includes native networking, DTLS, WHIP, DASH, SMB, SRT and module-file components absent from the smaller 9.1 build. Offline parser probes used fixed arguments followed by `-version`. They verified option recognition without opening a URL. [Companion build configuration](upstream-optional-version.txt) · [Tagged protocol option ledger](../protocol-options.tsv)
