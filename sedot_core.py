"""Pembentuk perintah dan pengelola proses Sedot Abis. Tanpa dependensi GUI."""
from __future__ import annotations

import os
import re
import shutil
import signal
import subprocess
import sys
import threading
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent
MODES = ("Video", "Audio MP3", "Subtitle saja", "Paket arsip")
QUALITIES = ("Terbaik", "1080p", "720p", "480p", "360p")


def find_tool(name: str) -> str | None:
    filename = name + (".exe" if os.name == "nt" else "")
    local = ROOT / "tools" / "bin" / filename
    return str(local) if local.is_file() else shutil.which(name)


def parse_urls(text: str) -> list[str]:
    urls = []
    for line in text.splitlines():
        url = line.strip()
        if not url:
            continue
        parsed = urlsplit(url)
        if parsed.scheme not in ("https", "http") or not parsed.hostname:
            raise ValueError("Setiap baris harus berisi satu tautan http:// atau https:// yang lengkap.")
        if parsed.username or parsed.password:
            raise ValueError("Tautan tidak boleh berisi nama pengguna atau kata sandi.")
        if url not in urls:
            urls.append(url)
    if not urls:
        raise ValueError("Tempel setidaknya satu tautan video atau playlist.")
    return urls


def seconds(value: str) -> int:
    if not re.fullmatch(r"\d{1,3}:[0-5]\d:[0-5]\d", value):
        raise ValueError("Waktu harus memakai format JJ:MM:DD, misalnya 00:05:00.")
    h, m, s = map(int, value.split(":"))
    return h * 3600 + m * 60 + s


@dataclass(frozen=True)
class Options:
    output: str
    mode: str = "Video"
    quality: str = "720p"
    playlist: bool = False
    subs: bool = False
    auto_subs: bool = True
    languages: str = "id,en"
    archive: bool = False
    metadata: bool = False
    start: str = ""
    end: str = ""
    rate: str = ""
    playlist_items: str = ""


def build_command(url: str, opt: Options) -> list[str]:
    parse_urls(url)
    if opt.mode not in MODES or opt.quality not in QUALITIES:
        raise ValueError("Pilihan jenis atau kualitas unduhan tidak dikenal.")
    if not opt.output.strip():
        raise ValueError("Pilih folder tujuan terlebih dahulu.")
    if opt.mode == "Subtitle saja" and (opt.start or opt.end):
        raise ValueError("Potong durasi tidak berlaku untuk unduhan subtitle saja.")
    if (opt.start or opt.end):
        if not opt.start or not opt.end or seconds(opt.end) <= seconds(opt.start):
            raise ValueError("Isi waktu mulai dan selesai; waktu selesai harus lebih besar.")
    if opt.rate and not re.fullmatch(r"[1-9]\d*(?:\.\d+)?[KM]?", opt.rate, re.I):
        raise ValueError("Batas kecepatan: gunakan angka seperti 500K atau 2M.")
    if opt.playlist_items and not re.fullmatch(r"\d+(?:-\d+)?(?:,\d+(?:-\d+)?)*", opt.playlist_items):
        raise ValueError("Nomor playlist: gunakan 1-5 atau 1,3,5 tanpa spasi.")
    if opt.playlist_items and not opt.playlist:
        raise ValueError("Aktifkan unduh playlist untuk memilih nomor video.")
    wants_subs = opt.subs or opt.mode == "Subtitle saja"
    if wants_subs and not re.fullmatch(r"[A-Za-z0-9_-]+(?:,[A-Za-z0-9_-]+)*", opt.languages):
        raise ValueError("Bahasa subtitle: gunakan id,en atau all, tanpa spasi.")
    if opt.mode == "Subtitle saja" and opt.archive:
        raise ValueError("Catatan unduhan tidak digunakan pada mode subtitle saja.")
    if opt.archive and opt.start:
        raise ValueError("Matikan catatan unduhan saat mengambil potongan, agar potongan berikutnya tidak dilewati.")
    label = "mp3" if opt.mode == "Audio MP3" else opt.quality
    suffix = " - " + label if opt.mode != "Subtitle saja" else ""
    if opt.start:
        suffix += " - " + opt.start.replace(":", "-") + "_" + opt.end.replace(":", "-")
    cmd = [sys.executable, "-m", "yt_dlp", "--ignore-config", "--newline", "--no-color",
           "--windows-filenames", "--no-overwrites", "--socket-timeout", "30",
           "--retries", "5", "--fragment-retries", "5", "-P", str(Path(opt.output).expanduser()),
           "-o", "%(title).150B [%(id)s]" + suffix + ".%(ext)s",
           "--progress-template", "download:SA_PROGRESS|%(progress._percent_str)s|%(progress._speed_str)s|%(progress._eta_str)s",
           "--yes-playlist" if opt.playlist else "--no-playlist"]
    ffmpeg = find_tool("ffmpeg")
    if ffmpeg:
        cmd += ["--ffmpeg-location", str(Path(ffmpeg).parent)]
    deno = find_tool("deno")
    if deno:
        cmd += ["--js-runtimes", "deno:" + deno]
    if opt.mode == "Audio MP3":
        cmd += ["-x", "--audio-format", "mp3", "--audio-quality", "0"]
    elif opt.mode == "Subtitle saja":
        cmd += ["--skip-download"]
    else:
        fmt = "bv*+ba/b" if opt.quality == "Terbaik" else (
            "bv*[height<=" + opt.quality[:-1] + "]+ba/b[height<=" + opt.quality[:-1] + "]")
        cmd += ["-f", fmt]
    if wants_subs:
        cmd += ["--write-subs", "--sub-langs", opt.languages, "--sub-format", "vtt/best"]
        if opt.auto_subs:
            cmd += ["--write-auto-subs"]
    if opt.mode == "Paket arsip" or opt.metadata:
        cmd += ["--write-info-json", "--write-description", "--write-thumbnail", "--no-write-playlist-metafiles"]
    if opt.archive:
        # Pisahkan catatan video, MP3, dan kualitas agar satu kebutuhan tidak memblokir yang lain.
        kind = ("mp3" if opt.mode == "Audio MP3" else opt.mode.lower().replace(" ", "-"))
        cmd += ["--download-archive", str(Path(opt.output) / (".sedot-arsip-" + kind + "-" + opt.quality + ".txt"))]
    if opt.start:
        cmd += ["--download-sections", "*" + opt.start + "-" + opt.end]
    if opt.rate:
        cmd += ["--limit-rate", opt.rate]
    if opt.playlist_items:
        # UI memakai 1-5; yt-dlp memakai slice 1:5 (ujung inklusif).
        cmd += ["--playlist-items", opt.playlist_items.replace("-", ":")]
    cmd += ["--", url]
    return cmd


class ProcessRunner:
    """Satu pekerjaan per instance; keluaran dikirim melalui callback thread worker."""
    def __init__(self):
        self.cancelled = threading.Event()
        self.lock = threading.Lock()
        self.process = None

    def run(self, cmd: list[str], on_line) -> int:
        with self.lock:
            if self.cancelled.is_set():
                return -1
            kwargs = {"creationflags": subprocess.CREATE_NO_WINDOW} if os.name == "nt" else {"start_new_session": True}
            self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                            text=True, encoding="utf-8", errors="replace", bufsize=1,
                                            cwd=ROOT, env={**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"}, **kwargs)
            process = self.process
        try:
            for line in process.stdout:
                on_line(line.rstrip())
            return process.wait()
        finally:
            process.stdout.close()
            with self.lock:
                self.process = None

    def cancel(self):
        self.cancelled.set()
        with self.lock:
            process = self.process
            if process is None or process.poll() is not None:
                return
            try:
                if os.name == "nt":
                    subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"],
                                   capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW, timeout=10)
                else:
                    os.killpg(process.pid, signal.SIGTERM)
            except (OSError, subprocess.TimeoutExpired):
                try:
                    process.kill()
                except OSError:
                    pass
