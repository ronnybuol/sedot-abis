import os
import sys
import threading
import unittest
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sedot_core import Options, ProcessRunner, build_command, parse_urls, seconds


class CommandTests(unittest.TestCase):
    def setUp(self):
        self.opt = Options(output=str(Path.home() / "Hasil dengan spasi"))
        self.url = "https://example.org/video?id=1&list=2"

    def command(self, **kwargs):
        return build_command(self.url, replace(self.opt, **kwargs))

    def test_default_single_video_and_destination(self):
        cmd = self.command()
        self.assertIn("--no-playlist", cmd)
        self.assertIn("--ignore-config", cmd)
        self.assertIn("--no-overwrites", cmd)
        self.assertEqual(cmd[cmd.index("-P") + 1], self.opt.output)
        self.assertEqual(cmd[cmd.index("-f") + 1], "bv*[height<=720]+ba/b[height<=720]")
        self.assertEqual(cmd[-2:], ["--", self.url])

    def test_modes(self):
        audio = self.command(mode="Audio MP3")
        self.assertEqual(audio[audio.index("--audio-format") + 1], "mp3")
        self.assertNotIn("-f", audio)
        subs = self.command(mode="Subtitle saja")
        self.assertIn("--skip-download", subs)
        self.assertIn("--write-auto-subs", subs)
        self.assertNotIn("-f", subs)
        archive = self.command(mode="Paket arsip")
        for arg in ("--write-info-json", "--write-description", "--write-thumbnail"):
            self.assertIn(arg, archive)

    def test_best_and_languages(self):
        cmd = self.command(quality="Terbaik", subs=True, languages="all", auto_subs=False)
        self.assertEqual(cmd[cmd.index("-f") + 1], "bv*+ba/b")
        self.assertEqual(cmd[cmd.index("--sub-langs") + 1], "all")
        self.assertNotIn("--write-auto-subs", cmd)

    def test_cut_and_separate_filenames(self):
        cmd = self.command(start="00:05:00", end="00:08:30")
        self.assertEqual(cmd[cmd.index("--download-sections") + 1], "*00:05:00-00:08:30")
        self.assertIn("00-05-00_00-08-30", cmd[cmd.index("-o") + 1])
        self.assertNotEqual(self.command(quality="720p")[self.command().index("-o") + 1],
                            self.command(quality="1080p")[self.command().index("-o") + 1])

    def test_playlist_rate_and_archive(self):
        cmd = self.command(playlist=True, playlist_items="1-5,8", rate="2M", archive=True)
        self.assertIn("--yes-playlist", cmd)
        self.assertEqual(cmd[cmd.index("--playlist-items") + 1], "1:5,8")
        self.assertEqual(cmd[cmd.index("--limit-rate") + 1], "2M")
        media_archive = cmd[cmd.index("--download-archive") + 1]
        audio = self.command(mode="Audio MP3", archive=True)
        self.assertNotEqual(media_archive, audio[audio.index("--download-archive") + 1])

    def test_invalid_fields(self):
        for values in ({"start": "00:10:00", "end": "00:05:00"}, {"start": "00:05:00"},
                       {"start": "00:65:00", "end": "00:70:00"}, {"rate": "2M --exec x"},
                       {"playlist_items": "1-5"}, {"playlist": True, "playlist_items": "1;2"},
                       {"mode": "Subtitle saja", "archive": True}, {"subs": True, "languages": ""},
                       {"output": ""}, {"archive": True, "start": "00:01:00", "end": "00:02:00"}):
            with self.subTest(values=values), self.assertRaises(ValueError):
                self.command(**values)

    def test_urls(self):
        self.assertEqual(parse_urls("\n" + self.url + "\n" + self.url), [self.url])
        for url in ("", "file:///tmp/video", "--exec calc", "https://", "https://user:secret@example.org"):
            with self.subTest(url=url), self.assertRaises(ValueError):
                parse_urls(url)
        self.assertEqual(seconds("02:01:30"), 7290)


class ProcessTests(unittest.TestCase):
    def test_exit_code_utf8_and_literal_argument(self):
        runner = ProcessRunner()
        lines = []
        argument = "x & echo injected $(echo bad)"
        code = runner.run([sys.executable, "-c", "import sys; print('bahasa: Indonesia'); print(sys.argv[1]); sys.exit(7)", argument], lines.append)
        self.assertEqual(code, 7)
        self.assertIn(argument, lines)
        self.assertIsNone(runner.process)

    def test_cancel_active_and_no_restart(self):
        runner = ProcessRunner()
        ready = threading.Event()
        codes = []
        def line(value):
            if value == "ready":
                ready.set()
        def run():
            codes.append(runner.run([sys.executable, "-u", "-c", "import time; print('ready', flush=True); time.sleep(60)"], line))
        thread = threading.Thread(target=run)
        thread.start()
        self.assertTrue(ready.wait(5))
        runner.cancel()
        thread.join(10)
        self.assertFalse(thread.is_alive())
        self.assertNotEqual(codes[0], 0)
        self.assertEqual(runner.run([sys.executable, "-c", "raise SystemExit(0)"], line), -1)

    def test_cancel_before_start(self):
        runner = ProcessRunner()
        runner.cancel()
        self.assertEqual(runner.run(["executable-that-does-not-exist"], lambda _: None), -1)


if __name__ == "__main__":
    unittest.main()
