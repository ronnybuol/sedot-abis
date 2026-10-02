# Sedot Abis v1.0.2

Rilis lengkap aplikasi desktop internal Zonautara untuk mengunduh video, audio MP3, subtitle, dan arsip sumber melalui yt-dlp.

## Isi rilis

- `Sedot-Abis-v1.0.2.zip`: aplikasi Python, installer, peluncur, bantuan Indonesia, dan pengujian.
- `SHA256SUMS.txt`: checksum paket ZIP.

Python, FFmpeg, ffprobe, dan Deno tidak dibundel. Panduan menjelaskan pemasangannya. Paket ini belum berupa aplikasi `.exe` mandiri.

## Perbaikan

- Tombol bawah tampil utuh; Ctrl + Enter dapat memulai unduhan.
- Pemeriksaan tautan diperbaiki agar tombol mulai dapat menjalankan antrean.
- Installer dan pembaruan yt-dlp menyertakan `curl-cffi`.
- Bantuan menjelaskan `.venv`, impersonation, serta penanganan peringatan dan kesalahan.

## Pengguna baru

Ekstrak ZIP, pasang Python 3.10+, jalankan `INSTALL.bat`, lengkapi FFmpeg/Deno melalui `PASANG_ALAT.bat` atau panduan manual, kemudian buka `MULAI.bat`.

## Pengguna versi 1.0.0 / 1.0.1

Tutup aplikasi. Salin `sedot_abis.py`, `sedot_core.py`, `requirements.txt`, `PANDUAN.txt`, dan `PANDUAN.html` dari ZIP ke folder aplikasi lama. Pertahankan `.venv` dan `tools`. Buka `MULAI.bat`; gunakan **Perbarui yt-dlp** bila `curl_cffi` belum terpasang pada `.venv`.

## Validasi dan batas

Pengujian mencakup pembentukan perintah, validasi isian, pembatalan subprocess, tata letak, dan alur klik dengan mesin unduhan simulasi. Pengujian tersebut tidak membuktikan semua situs dapat diunduh. Dukungan platform mengikuti yt-dlp, akses sumber, dan perubahan situs. Login/cookies, pengumpulan komentar, dan kontrol livestream belum tersedia pada UI.
