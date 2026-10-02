"""Sedot Abis 1.0.2 — aplikasi internal pengunduh media berbahasa Indonesia."""
from __future__ import annotations

import importlib.metadata
import json
import os
import queue
import re
import subprocess
import sys
import threading
import tkinter as tk
import webbrowser
from dataclasses import asdict
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext, ttk
from urllib.parse import urlsplit

from sedot_core import ROOT, MODES, QUALITIES, Options, ProcessRunner, build_command, find_tool, parse_urls

VERSION = "1.0.2"
STATE = Path(os.environ.get("LOCALAPPDATA", str(Path.home() / ".config"))) / "SedotAbis"


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sedot Abis · Pengunduh media internal")
        self.geometry("940x820")
        self.minsize(810, 720)
        self.configure(bg="#f5f2ef")
        # Sisakan tinggi natural header/footer. Hanya area tab yang boleh menyusut.
        # pack pada versi 1.0.0 memberi tab prioritas ruang dan memotong tombol footer.
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.events = queue.Queue()
        self.runner = None
        self.active = False
        self.closing = False
        self.job_output = ""
        self.settings = self.load_settings()
        self.vars = {}
        defaults = asdict(Options(output=str(Path.home() / "Downloads" / "Sedot Abis")))
        for key, default in defaults.items():
            value = self.settings.get(key, default)
            if type(value) is not type(default):
                value = default
            self.vars[key] = tk.BooleanVar(value=value) if isinstance(default, bool) else tk.StringVar(value=value)
        if self.vars["mode"].get() not in MODES:
            self.vars["mode"].set("Video")
        if self.vars["quality"].get() not in QUALITIES:
            self.vars["quality"].set("720p")
        self.status = tk.StringVar(value="Siap. Tempel tautan untuk memulai.")
        self.detail = tk.StringVar(value="Progres ditampilkan per file; video dan audio dapat diunduh terpisah.")
        self.configure_styles()
        self.build_ui()
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.bind("<Control-Return>", lambda event: self.start_download())
        self.after(100, self.poll)
        self.after(200, self.check_dependencies)

    def configure_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(".", font=("Segoe UI", 10), background="#f5f2ef", foreground="#29252a")
        style.configure("TNotebook.Tab", padding=(18, 10))
        style.configure("TButton", padding=(12, 8))
        style.configure("Accent.TButton", background="#7e2136", foreground="white", font=("Segoe UI", 11, "bold"))
        style.map("Accent.TButton", background=[("active", "#a0354f"), ("disabled", "#aaa")])
        style.configure("TEntry", fieldbackground="white", padding=6)
        style.configure("TCombobox", padding=6)
        style.configure("Title.TLabel", font=("Segoe UI", 25, "bold"), foreground="#7e2136")
        style.configure("Note.TLabel", foreground="#655d65")
        style.configure("TLabelframe", padding=12)
        style.configure("TLabelframe.Label", font=("Segoe UI", 10, "bold"))
        style.configure("Horizontal.TProgressbar", background="#7e2136")

    def build_ui(self):
        header = ttk.Frame(self, padding=(24, 18))
        header.grid(row=0, column=0, sticky="ew")
        ttk.Label(header, text="Sedot Abis", style="Title.TLabel").pack(anchor="w")
        ttk.Label(header, text="Video, audio, subtitle, dan arsip sumber · Internal Zonautara · v" + VERSION,
                  style="Note.TLabel").pack(anchor="w", pady=(3, 0))
        self.tabs = ttk.Notebook(self)
        self.tabs.grid(row=1, column=0, sticky="nsew", padx=20)
        download = ttk.Frame(self.tabs, padding=16)
        options = ttk.Frame(self.tabs, padding=16)
        logs = ttk.Frame(self.tabs, padding=16)
        help_tab = ttk.Frame(self.tabs, padding=16)
        for tab, name in ((download, "Unduh"), (options, "Opsi tambahan"), (logs, "Status & log"), (help_tab, "Bantuan")):
            self.tabs.add(tab, text=name)
        ttk.Label(download, text="1. Tempel tautan — satu tautan per baris").pack(anchor="w")
        self.urls = scrolledtext.ScrolledText(download, height=6, font=("Segoe UI", 11), wrap="word", relief="flat", padx=10, pady=10)
        self.urls.pack(fill="both", expand=True, pady=(8, 12))
        choices = ttk.Frame(download)
        choices.pack(fill="x")
        for column, (label, key, values) in enumerate((("2. Jenis unduhan", "mode", MODES), ("Kualitas maksimum", "quality", QUALITIES))):
            frame = ttk.Frame(choices)
            frame.grid(row=0, column=column, sticky="ew", padx=(0, 14))
            choices.columnconfigure(column, weight=1)
            ttk.Label(frame, text=label).pack(anchor="w")
            combo = ttk.Combobox(frame, textvariable=self.vars[key], values=values, state="readonly")
            combo.pack(fill="x", pady=(6, 0))
        ttk.Label(download, text="MP3 mengabaikan kualitas video. Subtitle hanya diambil jika tersedia di sumber.",
                  style="Note.TLabel").pack(anchor="w", pady=(8, 14))
        ttk.Label(download, text="3. Folder hasil unduhan").pack(anchor="w")
        dest = ttk.Frame(download)
        dest.pack(fill="x", pady=(6, 10))
        ttk.Entry(dest, textvariable=self.vars["output"]).pack(side="left", fill="x", expand=True)
        ttk.Button(dest, text="Pilih folder…", command=self.select_folder).pack(side="left", padx=(8, 0))
        ttk.Checkbutton(download, text="Unduh seluruh playlist dari tautan (dapat berisi banyak video)", variable=self.vars["playlist"]).pack(anchor="w")
        ttk.Label(download, text="Paket arsip = video + deskripsi + thumbnail + metadata JSON.\nTambahkan subtitle melalui Opsi tambahan. Format video mengikuti sumber (MP4 / WebM / MKV).",
                  style="Note.TLabel", wraplength=760).pack(anchor="w", pady=(10, 0))
        self.build_options(options)
        toolbar = ttk.Frame(logs)
        toolbar.pack(fill="x", pady=(0, 10))
        self.check_btn = ttk.Button(toolbar, text="Cek komponen", command=self.check_dependencies)
        self.check_btn.pack(side="left")
        self.update_btn = ttk.Button(toolbar, text="Perbarui yt-dlp", command=self.update_dependency)
        self.update_btn.pack(side="left", padx=8)
        ttk.Button(toolbar, text="Simpan log…", command=self.save_log).pack(side="left")
        self.log = scrolledtext.ScrolledText(logs, font=("Consolas", 9), state="disabled", wrap="word", relief="flat")
        self.log.pack(fill="both", expand=True)
        ttk.Label(logs, text="Log dapat memuat tautan, judul, dan lokasi file. Periksa isinya sebelum membagikan.", style="Note.TLabel").pack(anchor="w", pady=(8, 0))
        ttk.Button(help_tab, text="Buka panduan lengkap di browser", command=self.open_help).pack(anchor="w", pady=(0, 10))
        help_text = scrolledtext.ScrolledText(help_tab, font=("Segoe UI", 10), wrap="word", relief="flat", padx=12, pady=12)
        try:
            help_text.insert("1.0", (ROOT / "PANDUAN.txt").read_text(encoding="utf-8"))
        except OSError:
            help_text.insert("1.0", "Panduan tidak ditemukan. Pastikan seluruh isi ZIP sudah diekstrak.")
        help_text.configure(state="disabled")
        help_text.pack(fill="both", expand=True)
        footer = ttk.Frame(self, padding=(20, 14))
        footer.grid(row=2, column=0, sticky="ew")
        ttk.Label(footer, textvariable=self.status, wraplength=850).pack(anchor="w")
        self.progress = ttk.Progressbar(footer, mode="determinate", maximum=100)
        self.progress.pack(fill="x", pady=(8, 5))
        ttk.Label(footer, textvariable=self.detail, style="Note.TLabel", wraplength=850).pack(anchor="w")
        ttk.Label(footer, text="Mulai unduhan: klik Sedot sekarang (atau Ctrl + Enter).",
                  style="Note.TLabel").pack(anchor="w", pady=(6, 0))
        buttons = ttk.Frame(footer)
        buttons.pack(fill="x", pady=(12, 0))
        # Tombol aksi memakai ukuran dan warna eksplisit, termasuk state nonaktif.
        self.start_btn = tk.Button(buttons, text="Sedot sekarang", command=self.start_download,
                                   font=("Segoe UI", 11, "bold"), bg="#7e2136", fg="white",
                                   activebackground="#a0354f", activeforeground="white",
                                   disabledforeground="#ddd", relief="flat", borderwidth=1,
                                   padx=18, pady=10, cursor="hand2")
        self.start_btn.pack(side="left")
        self.stop_btn = tk.Button(buttons, text="Hentikan", command=self.stop, state="disabled",
                                  font=("Segoe UI", 10), bg="#e9e3df", fg="#29252a",
                                  disabledforeground="#777", relief="flat", padx=16, pady=11)
        self.stop_btn.pack(side="left", padx=8)
        self.folder_btn = tk.Button(buttons, text="Buka folder hasil", command=self.open_output,
                                    font=("Segoe UI", 10), bg="#e9e3df", fg="#29252a",
                                    relief="flat", padx=16, pady=11, cursor="hand2")
        self.folder_btn.pack(side="right")

    def build_options(self, frame):
        subs = ttk.LabelFrame(frame, text="Subtitle dan arsip")
        subs.pack(fill="x", pady=(0, 12))
        for label, key in (("Sertakan subtitle pada unduhan video / audio", "subs"),
                           ("Ambil juga subtitle otomatis jika tersedia", "auto_subs"),
                           ("Simpan deskripsi, thumbnail, dan metadata untuk Video / MP3", "metadata"),
                           ("Catat unduhan berhasil untuk menghindari unduhan berulang", "archive")):
            ttk.Checkbutton(subs, text=label, variable=self.vars[key]).pack(anchor="w", pady=2)
        lang = ttk.Frame(subs)
        lang.pack(fill="x", pady=(6, 0))
        ttk.Label(lang, text="Bahasa subtitle").pack(side="left")
        ttk.Entry(lang, textvariable=self.vars["languages"], width=20).pack(side="left", padx=10)
        ttk.Label(lang, text="id,en atau all · disimpan sebagai VTT", style="Note.TLabel").pack(side="left")
        cut = ttk.LabelFrame(frame, text="Ambil bagian video / audio (opsional)")
        cut.pack(fill="x", pady=(0, 12))
        for label, key in (("Mulai", "start"), ("Selesai", "end")):
            ttk.Label(cut, text=label).pack(side="left")
            ttk.Entry(cut, textvariable=self.vars[key], width=12).pack(side="left", padx=(8, 16))
        ttk.Label(cut, text="Contoh 00:05:00 → 00:08:30", style="Note.TLabel").pack(side="left")
        net = ttk.LabelFrame(frame, text="Playlist dan koneksi")
        net.pack(fill="x")
        for row, (label, key, hint) in enumerate((("Nomor video playlist", "playlist_items", "Kosong = semua; contoh 1-5 atau 1,3,5"),
                                                 ("Batas kecepatan", "rate", "Kosong = tanpa batas; contoh 500K atau 2M (byte/detik)"))):
            ttk.Label(net, text=label).grid(row=row, column=0, sticky="w", pady=6)
            ttk.Entry(net, textvariable=self.vars[key], width=16).grid(row=row, column=1, padx=12)
            ttk.Label(net, text=hint, style="Note.TLabel", wraplength=410).grid(row=row, column=2, sticky="w")
        ttk.Label(frame, text="Kosongkan kedua waktu untuk mengunduh utuh. Potongan membutuhkan FFmpeg.\nCatatan unduhan tidak berlaku untuk subtitle saja atau potongan.\nFile yang sudah ada tidak ditimpa; kualitas dan waktu potongan dicantumkan di nama file.",
                  style="Note.TLabel", wraplength=750).pack(anchor="w", pady=14)

    def load_settings(self):
        try:
            data = json.loads((STATE / "settings.json").read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else {}
        except (OSError, ValueError):
            return {}

    def save_settings(self):
        try:
            STATE.mkdir(parents=True, exist_ok=True)
            (STATE / "settings.json").write_text(json.dumps({k: v.get() for k, v in self.vars.items()}, indent=2), encoding="utf-8")
        except OSError as exc:
            self.append_log("Pengaturan tidak dapat disimpan: " + str(exc))

    def select_folder(self):
        folder = filedialog.askdirectory(title="Pilih folder hasil")
        if folder:
            self.vars["output"].set(folder)

    def open_help(self):
        webbrowser.open((ROOT / "PANDUAN.html").as_uri())

    def open_output(self):
        path = Path(self.job_output or self.vars["output"].get()).expanduser()
        try:
            if not path.is_dir():
                raise ValueError("Folder belum ada. Jalankan unduhan atau pilih folder yang sudah tersedia.")
            if os.name == "nt":
                os.startfile(str(path))
            else:
                webbrowser.open(path.resolve().as_uri())
        except (OSError, ValueError) as exc:
            messagebox.showerror("Folder hasil", str(exc))

    def append_log(self, text):
        self.log.configure(state="normal")
        self.log.insert("end", text + "\n")
        # Batasi tampilan agar playlist besar tidak menghabiskan memori GUI.
        count = int(self.log.index("end-1c").split(".")[0])
        if count > 5000:
            self.log.delete("1.0", f"{count - 4500}.0")
        self.log.see("end")
        self.log.configure(state="disabled")

    def save_log(self):
        filename = filedialog.asksaveasfilename(defaultextension=".txt", initialfile="Sedot-Abis-log.txt", filetypes=[("Teks", "*.txt")])
        if filename:
            try:
                Path(filename).write_text(self.log.get("1.0", "end-1c"), encoding="utf-8")
            except OSError as exc:
                messagebox.showerror("Simpan log", str(exc))

    def set_busy(self, busy):
        self.active = busy
        self.start_btn.configure(state="disabled" if busy else "normal")
        self.update_btn.configure(state="disabled" if busy else "normal")
        self.check_btn.configure(state="disabled" if busy else "normal")
        self.stop_btn.configure(state="normal" if busy else "disabled")

    def start_download(self):
        if self.active:
            return
        try:
            urls = parse_urls(self.urls.get("1.0", "end"))
            opt = Options(**{k: v.get().strip() if isinstance(v, tk.StringVar) else v.get() for k, v in self.vars.items()})
            commands = [build_command(url, opt) for url in urls]
            importlib.metadata.version("yt-dlp")
            needs_ffmpeg = opt.mode != "Subtitle saja"
            if needs_ffmpeg and not (find_tool("ffmpeg") and find_tool("ffprobe")):
                raise ValueError("Untuk Video, MP3, dan Paket arsip, pasang FFmpeg dan ffprobe dahulu. Buka Bantuan → langkah 3.")
            if any("youtube.com" in urlsplit(u).hostname.lower() or urlsplit(u).hostname.lower() == "youtu.be" for u in urls) and not find_tool("deno"):
                messagebox.showwarning("Deno belum tersedia", "Deno direkomendasikan untuk YouTube. Unduhan akan dicoba, tetapi bisa gagal. Lihat Bantuan → langkah 3.")
            folder = Path(opt.output).expanduser()
            folder.mkdir(parents=True, exist_ok=True)
            # Uji izin tulis tanpa menghapus file pengguna.
            import tempfile
            with tempfile.TemporaryFile(dir=folder):
                pass
        except importlib.metadata.PackageNotFoundError:
            messagebox.showerror("yt-dlp belum tersedia", "Tutup aplikasi lalu klik INSTALL.bat, atau gunakan Perbarui yt-dlp di Status & log.")
            return
        except (ValueError, OSError) as exc:
            messagebox.showerror("Periksa isian", str(exc))
            return
        self.job_output = str(folder)
        self.save_settings()
        self.runner = ProcessRunner()
        runner = self.runner
        self.set_busy(True)
        self.progress["value"] = 0
        self.tabs.select(2)
        self.append_log("\nMulai: " + opt.mode + " · " + str(len(urls)) + " tautan. Hasil: " + str(folder))
        def worker():
            success = failed = 0
            warnings = False
            try:
                for i, cmd in enumerate(commands, 1):
                    if runner.cancelled.is_set():
                        break
                    self.events.put(("status", f"Tautan {i}/{len(commands)} · {opt.mode}"))
                    self.events.put(("reset", None))
                    def output(line):
                        nonlocal warnings
                        if "WARNING:" in line or "ERROR:" in line or "no subtitles" in line.lower():
                            warnings = True
                        self.events.put(("line", line))
                    code = runner.run(cmd, output)
                    if runner.cancelled.is_set():
                        break
                    if code == 0:
                        success += 1
                    else:
                        failed += 1
            except Exception as exc:
                failed += 1
                self.events.put(("line", "Kesalahan: " + str(exc)))
            finally:
                result = "Dihentikan. File parsial dapat dilanjutkan dengan menjalankan tautan yang sama." if runner.cancelled.is_set() else f"Selesai: {success} tautan tanpa kesalahan proses; {failed} gagal."
                if warnings or failed:
                    result += " Periksa peringatan pada log."
                self.events.put(("done", result))
        threading.Thread(target=worker, daemon=True).start()

    def update_dependency(self):
        if self.active:
            return
        self.tabs.select(2)
        self.set_busy(True)
        self.runner = ProcessRunner()
        runner = self.runner
        self.status.set("Memperbarui yt-dlp dari PyPI…")
        self.append_log("\nMemperbarui yt-dlp dan dependensi pada Python aplikasi ini.")
        def worker():
            try:
                code = runner.run([sys.executable, "-m", "pip", "install", "-U", "yt-dlp[default,curl-cffi]"],
                                  lambda line: self.events.put(("line", line)))
                msg = "Pembaruan selesai." if code == 0 else "Pembaruan gagal atau dihentikan. Periksa log."
            except Exception as exc:
                msg = "Pembaruan gagal: " + str(exc)
            self.events.put(("done", msg))
        threading.Thread(target=worker, daemon=True).start()

    def check_dependencies(self):
        if self.active:
            return
        self.append_log("\nPEMERIKSAAN KOMPONEN")
        self.append_log("Python " + sys.version.split()[0] + " · " + sys.executable)
        for package in ("yt-dlp", "yt-dlp-ejs", "curl_cffi"):
            try:
                self.append_log(package + ": " + importlib.metadata.version(package))
            except importlib.metadata.PackageNotFoundError:
                self.append_log(package + ": BELUM TERPASANG — jalankan INSTALL.bat")
        for name in ("ffmpeg", "ffprobe", "deno"):
            path = find_tool(name)
            self.append_log(name + ": " + (path or "BELUM DITEMUKAN — lihat Bantuan langkah 3"))

    def stop(self):
        if self.runner and self.active:
            self.status.set("Menghentikan proses…")
            self.stop_btn.configure(state="disabled")
            threading.Thread(target=self.runner.cancel, daemon=True).start()

    def poll(self):
        for _ in range(250):
            try:
                kind, data = self.events.get_nowait()
            except queue.Empty:
                break
            if kind == "line":
                if data.startswith("SA_PROGRESS|"):
                    parts = data.split("|")
                    match = re.search(r"(\d+(?:\.\d+)?)%", parts[1])
                    if match:
                        self.progress["value"] = float(match.group(1))
                    if len(parts) >= 4:
                        self.detail.set(f"File saat ini: {parts[1].strip()} · {parts[2].strip()} · Sisa {parts[3].strip()}")
                else:
                    self.append_log(data)
                    if "[Merger]" in data or "[ExtractAudio]" in data:
                        self.detail.set("Memproses / menggabungkan media. Tunggu sampai selesai.")
            elif kind == "status":
                self.status.set(data)
            elif kind == "reset":
                self.progress["value"] = 0
            elif kind == "done":
                self.set_busy(False)
                self.status.set(data)
                self.detail.set("Lihat log untuk hasil tiap video. Video yang sudah ada / tercatat dapat dilewati.")
                self.append_log(data)
                if self.closing:
                    self.destroy()
                    return
        self.after(100, self.poll)

    def close(self):
        if self.active:
            if messagebox.askyesno("Tutup Sedot Abis?", "Proses masih berjalan. Hentikan proses dan tutup aplikasi?"):
                self.closing = True
                self.stop()
        else:
            self.save_settings()
            self.destroy()


if __name__ == "__main__":
    if sys.version_info < (3, 10):
        raise SystemExit("Sedot Abis membutuhkan Python 3.10 atau lebih baru.")
    App().mainloop()
