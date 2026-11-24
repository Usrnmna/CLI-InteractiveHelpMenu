"""Check FFmpeg option placement and parser behavior with disposable local media."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


@unittest.skipUnless(sys.platform.startswith("linux"), "Linux FFmpeg fixtures")
class PackagedFFmpegTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Select matching Ubuntu clients and generate a three-stream reference file."""
        override = os.environ.get("FFMPEG_TEST_ROOT")
        root = Path(override or "/")
        cls.ffmpeg = root / "usr/bin/ffmpeg"
        cls.ffprobe = root / "usr/bin/ffprobe"
        if not override and not all(path.is_file() for path in (cls.ffmpeg, cls.ffprobe)):
            raise unittest.SkipTest("Ubuntu FFmpeg and ffprobe fixture unavailable")
        private = tempfile.TemporaryDirectory(prefix="ffmpeg-media-")
        cls.addClassCleanup(private.cleanup)
        cls.directory = Path(private.name)
        cls.env = {"HOME": private.name, "PATH": "/usr/bin:/bin", "LC_ALL": "C"}
        if override:
            # The private Noble runtime uses these directories for shared libraries
            # that its base test image omits. Other programs retain their own loader.
            libs = root / "usr/lib/x86_64-linux-gnu"
            cls.env["LD_LIBRARY_PATH"] = ":".join(
                str(libs / name) for name in ("", "blas", "lapack", "pulseaudio")
            )
        versions = [
            cls.invoke(binary, "-version").stdout.split()[2] for binary in (cls.ffmpeg, cls.ffprobe)
        ]
        if versions[0] != versions[1]:
            raise ValueError(f"FFmpeg and ffprobe releases differ: {versions}")
        cls.release = versions[0]
        if cls.release not in ("6.1.1-3ubuntu5", "8.0.1-3ubuntu2"):
            if override:
                raise ValueError(f"Unexpected FFmpeg fixture version: {cls.release}")
            raise unittest.SkipTest(f"No release-specific expectations for FFmpeg {cls.release}")
        cls.source = cls.directory / "source.mkv"
        cls.convert("-f", "lavfi", "-i", "testsrc2=size=64x48:rate=10:duration=3",
                    "-f", "lavfi", "-i", "sine=frequency=440:duration=3",
                    "-f", "lavfi", "-i", "sine=frequency=880:duration=3",
                    "-map", "0:v", "-map", "1:a", "-map", "2:a",
                    "-c:v", "mpeg4", "-g", "10", "-bf", "0", "-threads:v", "1",
                    "-c:a", "pcm_s16le", "-metadata:s:a:0", "language=eng",
                    "-metadata:s:a:1", "language=fra", cls.source)

    @classmethod
    def invoke(cls, binary, *args, check=True):
        """Run one fixed tool in the fixture directory and retain its diagnostics."""
        return subprocess.run([binary, *args], capture_output=True, text=True, env=cls.env,
                              cwd=cls.directory, check=check, stdin=subprocess.DEVNULL, timeout=20)

    @classmethod
    def convert(cls, *args, check=True):
        """Make encodes deterministic and small enough for the sandbox process limit."""
        return cls.invoke(cls.ffmpeg, "-hide_banner", "-loglevel", "error", "-nostdin",
                          "-filter_threads", "1", "-filter_complex_threads", "1", *args, check=check)

    def probe(self, filename):
        """Return stream identities, frame counts, timestamps and duration from ffprobe."""
        fields = ("stream=index,codec_name,codec_type,width,nb_read_frames,start_time,bit_rate"
                  ":stream_tags=language:format=duration,start_time")
        result = self.invoke(self.ffprobe, "-v", "error", "-count_frames", "-show_entries",
                             fields, "-of", "json", filename)
        return json.loads(result.stdout)

    def test_mapping_order_identity_and_optional_index(self):
        self.convert("-i", self.source, "-map", "0:a:1", "-map", "0:v", "-map", "0:a:0",
                     "-map", "0:s?", "-c", "copy", "-c:a:0", "pcm_u8", "reordered.mkv")
        streams = self.probe("reordered.mkv")["streams"]
        self.assertEqual([(s["index"], s["codec_name"], s.get("tags", {}).get("language"))
                          for s in streams], [(0, "pcm_u8", "fra"), (1, "mpeg4", None),
                                               (2, "pcm_s16le", "eng")])
        self.convert("-i", self.source, "-map", "0", "-map", "-0:a:0", "-c", "copy", "removed.mkv")
        self.assertEqual([s.get("tags", {}).get("language")
                          for s in self.probe("removed.mkv")["streams"]], [None, "fra"])
        bad = self.convert("-i", self.source, "-map", "1:a?", "-f", "null", "-", check=False)
        self.assertNotEqual(bad.returncode, 0)
        self.assertIn("Invalid input file index", bad.stderr)

    def test_output_options_reset_between_files(self):
        self.convert("-i", self.source, "-map", "0", "-an", "-c", "copy", "picture.mkv",
                     "-map", "0:a", "-c", "copy", "tracks.mkv")
        self.assertEqual([s["codec_type"] for s in self.probe("picture.mkv")["streams"]], ["video"])
        self.assertEqual([s["tags"]["language"] for s in self.probe("tracks.mkv")["streams"]],
                         ["eng", "fra"])

    def test_default_disposition_can_outweigh_channel_count(self):
        """Give the mono track default disposition beside an earlier stereo track."""
        self.convert("-i", self.source, "-map", "0:a:0", "-map", "0:a:1", "-c:a", "pcm_s16le",
                     "-ac:a:0", "2", "-disposition:a:0", "0", "-disposition:a:1", "default",
                     "two-tracks.mka")
        for name, mapping, language in (("automatic", [], "fra"), ("explicit", ["-map", "0:a:0"], "eng")):
            with self.subTest(name=name):
                output = name + "-audio.mka"
                self.convert("-i", "two-tracks.mka", *mapping, "-c", "copy", output)
                stream, = self.probe(output)["streams"]
                self.assertEqual(stream["tags"]["language"], language)

    def test_simple_filter_streamcopy_and_complex_outputs(self):
        bad = self.convert("-i", self.source, "-map", "0:v", "-vf", "scale=32:24", "-c:v",
                           "copy", "-f", "null", "-", check=False)
        self.assertNotEqual(bad.returncode, 0)
        self.assertIn("copy", bad.stderr)
        self.convert("-i", self.source, "-filter_complex", "[0:v]scale=32:24", "-map", "0:a:0",
                     "-vn", "-c:v", "ffv1", "-threads:v", "1", "-c:a", "copy", "unlabeled.mkv")
        self.assertEqual([s.get("width") for s in self.probe("unlabeled.mkv")["streams"]],
                         [32, None])
        bad = self.convert("-i", self.source, "-filter_complex", "[0:v]null[picture]", "-map",
                           "0:a:0", "-f", "null", "-", check=False)
        self.assertNotEqual(bad.returncode, 0)
        self.assertIn("unconnected", bad.stderr.lower())

    def test_seek_end_seek_and_duration_placement(self):
        for name, options, codec, frames in (
            ("copy", ["-ss", "1.4", "-i", self.source], "copy", 20),
            ("transcode", ["-ss", "1.4", "-i", self.source], "ffv1", 16),
            ("output", ["-i", self.source, "-ss", "1.4"], "ffv1", 16),
            ("end", ["-sseof", "-1", "-i", self.source], "ffv1", 10),
        ):
            with self.subTest(name=name):
                output = f"seek-{name}.mkv"
                self.convert(*options, "-an", "-c:v", codec, "-threads:v", "1", output)
                self.assertEqual(int(self.probe(output)["streams"][0]["nb_read_frames"]), frames)
        for name, options, seconds in (
            ("input", ["-t", "200ms", "-i", self.source], 0.2),
            ("input_stop", ["-ss", "0.2", "-to", "0.8", "-i", self.source], 0.6),
            ("output_stop", ["-i", self.source, "-ss", "0.2", "-to", "0.8"], 0.6),
            ("both", ["-i", self.source, "-to", "0.1", "-t", "0.2"], 0.2),
        ):
            with self.subTest(name=name):
                output = f"duration-{name}.wav"
                self.convert(*options, "-map", "0:a:0", "-c:a", "pcm_s16le", output)
                self.assertAlmostEqual(float(self.probe(output)["format"]["duration"]), seconds, places=4)
        bad = self.convert("-sseof", "0", "-i", self.source, "-f", "null", "-", check=False)
        self.assertNotEqual(bad.returncode, 0)
        self.assertIn("must be negative", bad.stderr)

    def test_timestamps_are_preserved_or_shifted(self):
        self.convert("-i", self.source, "-map", "0:v", "-c", "copy", "-output_ts_offset", "5",
                     "offset.mkv")
        for name, options, start in (("normal", [], 0), ("retained", ["-copyts"], 5),
                                     ("shifted", ["-copyts", "-start_at_zero"], 0)):
            with self.subTest(name=name):
                self.convert(*options, "-i", "offset.mkv", "-c", "copy", f"{name}.mkv")
                self.assertEqual(float(self.probe(f"{name}.mkv")["format"]["start_time"]), start)

    def test_overwrite_stops_before_the_later_output(self):
        collision = self.directory / "collision.wav"
        later = self.directory / "later.wav"
        collision.write_bytes(b"preserve this file")
        stop = self.convert("-n", "-i", self.source, "-vn", collision, later, check=False)
        self.assertIn("already exists", stop.stderr)
        self.assertEqual(collision.read_bytes(), b"preserve this file")
        self.assertFalse(later.exists())
        self.assertEqual(stop.returncode, 0)
        self.convert("-y", "-i", self.source, "-map", "0:a:0", collision)
        self.assertEqual(self.probe(collision)["streams"][0]["codec_type"], "audio")

    def test_file_loaded_filter_and_retired_subtitle_alias(self):
        (self.directory / "graph").write_text("scale=32:24")
        load = self.convert("-i", self.source, "-map", "0:v", "-/filter:v", "graph",
                            "-c:v", "ffv1", "-threads:v", "1", "file-graph.mkv", check=False)
        if self.release.startswith("6."):
            self.assertNotEqual(load.returncode, 0)
            self.assertIn("Unrecognized option '/filter:v'", load.stderr)
        else:
            self.assertEqual(load.returncode, 0, load.stderr)
            self.assertEqual(self.probe("file-graph.mkv")["streams"][0]["width"], 32)
        unsupported = self.convert("-sbsf", "null", "-version", check=False)
        self.assertNotEqual(unsupported.returncode, 0)
        self.assertIn("Unrecognized option 'sbsf'", unsupported.stderr)
        self.assertEqual(self.convert("-bsf:s", "null", "-version").returncode, 0)

    def test_base_view_selector_depends_on_release(self):
        result = self.convert("-i", self.source, "-map", "0:v:vidx:0", "-threads:v", "1",
                              "-c:v", "ffv1", "base-view.mkv", check=False)
        if self.release.startswith("6."):
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Invalid stream specifier", result.stderr)
        else:
            self.assertEqual(result.returncode, 0, result.stderr)
            stream, = self.probe("base-view.mkv")["streams"]
            self.assertEqual((stream["codec_name"], stream["nb_read_frames"]), ("ffv1", "30"))
