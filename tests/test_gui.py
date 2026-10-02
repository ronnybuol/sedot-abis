"""Regresi tombol terpotong dan alur mulai; tidak mengunduh media nyata."""
import os
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import sedot_abis as app_module


class FakeRunner:
    def __init__(self):
        self.cancelled = threading.Event()
        self.calls = []

    def run(self, cmd, output):
        self.calls.append(cmd)
        output("SA_PROGRESS|50.0%|1MiB/s|00:01")
        output("[download] Selesai simulasi")
        return 0

    def cancel(self):
        self.cancelled.set()


@unittest.skipUnless(os.name == "nt" or os.environ.get("DISPLAY"), "GUI membutuhkan Windows atau display Linux")
class GuiTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.state_patch = patch.object(app_module, "STATE", Path(self.tmp.name) / "settings")
        self.state_patch.start()
        self.app = app_module.App()
        self.app.update()

    def tearDown(self):
        for timer in self.app.tk.call("after", "info"):
            self.app.after_cancel(timer)
        self.app.destroy()
        self.state_patch.stop()
        self.tmp.cleanup()

    def test_footer_visible_on_all_tabs_and_sizes(self):
        for size in ("940x820", "810x720", "1200x920"):
            self.app.geometry(size)
            for tab in range(4):
                self.app.tabs.select(tab)
                self.app.update()
                for button in (self.app.start_btn, self.app.stop_btn, self.app.folder_btn):
                    with self.subTest(size=size, tab=tab, button=button.cget("text")):
                        self.assertGreaterEqual(button.winfo_height(), button.winfo_reqheight())
                        bottom = button.winfo_rooty() - self.app.winfo_rooty() + button.winfo_height()
                        self.assertLessEqual(bottom, self.app.winfo_height())

    def test_start_button_processes_two_links(self):
        with patch.object(app_module, "ProcessRunner", FakeRunner), \
             patch.object(app_module.importlib.metadata, "version", return_value="test"), \
             patch.object(app_module, "find_tool", return_value="ffmpeg"):
            self.app.vars["output"].set(self.tmp.name)
            self.app.urls.insert("1.0", "https://example.org/video1\nhttps://example.org/video2")
            self.app.start_btn.invoke()
            self.assertEqual(self.app.tabs.index("current"), 2)
            deadline = time.monotonic() + 5
            while self.app.active and time.monotonic() < deadline:
                self.app.update()
                time.sleep(.01)
            self.assertFalse(self.app.active)
            self.assertEqual(len(self.app.runner.calls), 2)
            self.assertIn("Mulai: Video", self.app.log.get("1.0", "end"))
            self.assertIn("2 tautan tanpa kesalahan proses", self.app.status.get())


if __name__ == "__main__":
    unittest.main()
