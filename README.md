# Sedot Abis

**Pengunduh video, audio, subtitle, dan arsip sumber untuk internal Zonautara.**

Sedot Abis adalah aplikasi desktop Windows berbahasa Indonesia. Pengguna menempel tautan, memilih kebutuhan dan folder hasil, lalu mengeklik **Sedot sekarang**. yt-dlp menjalankan unduhan; Tkinter menyediakan antarmuka; FFmpeg/ffprobe memproses media; Deno membantu dukungan YouTube; curl_cffi menyediakan impersonation browser pada situs yang memerlukannya.

Versi saat ini: **1.0.2**. Repository ini privat untuk penggunaan internal.

- [Unduh rilis terbaru](https://github.com/ronnybuol/sedot-abis/releases/latest)
- [Panduan lengkap dalam teks](PANDUAN.txt)
- [Panduan HTML offline](PANDUAN.html) — unduh lalu buka di browser
- [Riwayat perubahan](CHANGELOG.md)
- [Catatan rilis](RELEASE_NOTES.md)

## Fitur

| Fitur | Kegunaan |
|---|---|
| Video | Mengunduh video beserta suara |
| Audio MP3 | Mengambil audio dan mengonversinya menjadi MP3 |
| Subtitle saja | Mengambil subtitle sumber tanpa mengunduh video |
| Paket arsip | Video, deskripsi TXT, thumbnail, dan metadata JSON |
| Kualitas maksimum | Terbaik, 1080p, 720p, 480p, atau 360p |
| Beberapa tautan | Satu tautan per baris, diproses berurutan |
| Playlist | Semua video atau nomor tertentu |
| Potongan waktu | Mengambil rentang video/audio tertentu |
| Subtitle pilihan | Bahasa Indonesia, Inggris, bahasa lain, atau semua yang tersedia |
| Catatan unduhan | Melewati video yang sudah tercatat berhasil |
| Batas kecepatan | Mengatur penggunaan koneksi |
| Progres dan log | Memantau proses, menyimpan log, membuka hasil |
| Hentikan | Menghentikan proses aktif beserta proses anak |
| Bantuan offline | Petunjuk instalasi, seluruh opsi, dan pemecahan masalah |
| Pembaruan yt-dlp | Memperbarui mesin unduhan dan curl_cffi dari aplikasi |

## Persyaratan

- Windows 10/11 64-bit.
- Python 3.10 atau lebih baru, dengan pip dan Tcl/Tk (Tkinter).
- Koneksi internet untuk instalasi dependensi, pembaruan, dan unduhan.
- FFmpeg serta ffprobe untuk Video, MP3, Paket arsip, dan potongan waktu.
- Deno direkomendasikan untuk dukungan YouTube.

Python, FFmpeg, ffprobe, dan Deno **tidak disertakan** dalam ZIP. curl_cffi dan yt-dlp-ejs dipasang otomatis melalui dependensi Python sejak versi 1.0.2. Paket rilis ini belum berupa `.exe` mandiri.

## Instalasi pertama

1. Unduh `Sedot-Abis-v1.0.2.zip` dari halaman Releases dan ekstrak seluruhnya. Jangan menjalankan aplikasi dari dalam ZIP.
2. Jika Python belum ada, ambil installer Windows 64-bit dari [python.org](https://www.python.org/downloads/windows/). Sertakan pip dan Tcl/Tk; aktifkan Add Python to PATH bila pilihan itu tersedia. Buka terminal baru setelah pemasangan. Python 3.10 yang sudah terpasang tetap memenuhi syarat.
3. Buka folder `Sedot-Abis` dan klik **INSTALL.bat**. Tunggu sampai muncul **BERHASIL**.
4. Klik **PASANG_ALAT.bat** untuk memasang FFmpeg dan Deno melalui winget. Ikuti persetujuan paket atau Windows yang muncul.
5. Tutup terminal/aplikasi yang sebelumnya terbuka agar perubahan PATH terbaca. Buka **MULAI.bat**.
6. Di **Status & log**, klik **Cek komponen**. Pastikan yt-dlp, yt-dlp-ejs, curl_cffi, FFmpeg, ffprobe, dan Deno ditemukan.

Cara memasang Python dan komponen secara manual dijelaskan lebih rinci dalam [PANDUAN.txt](PANDUAN.txt).

### Alternatif memasang alat tanpa PATH

Unduh FFmpeg dari penyedia Windows yang ditautkan [ffmpeg.org](https://ffmpeg.org/download.html), serta Deno dari [rilis resminya](https://github.com/denoland/deno/releases). Ekstrak, lalu salin tiga file berikut langsung ke `tools/bin`:

```text
ffmpeg.exe
ffprobe.exe
deno.exe
```

Jangan menaruh ZIP atau folder induknya saja di lokasi tersebut. Sedot Abis mencari alat di `tools/bin` terlebih dahulu, lalu PATH Windows.

## Menggunakan aplikasi

1. Pada tab **Unduh**, tempel satu tautan lengkap per baris.
2. Pilih jenis unduhan, kualitas, dan folder hasil.
3. Atur kebutuhan lain di **Opsi tambahan**.
4. Klik tombol maron **Sedot sekarang** di kiri bawah, atau tekan **Ctrl + Enter**.
5. Aplikasi berpindah ke **Status & log** dan menampilkan pesan **Mulai**. Tunggu hingga unduhan dan penggabungan selesai.
6. Klik **Buka folder hasil** untuk melihat berkas.

| Kontrol bawah | Fungsi |
|---|---|
| Sedot sekarang | Memulai antrean |
| Hentikan | Membatalkan proses aktif dan sisa antrean |
| Buka folder hasil | Membuka folder; tidak memulai unduhan |
| Bilah panjang | Progres file/arus media saat ini |

Bilah progres dapat kembali ke nol ketika berpindah dari video ke audio atau ke tautan berikutnya. Hitungan akhir merujuk jumlah tautan masukan; satu tautan playlist dapat menghasilkan banyak file. Proses yang selesai tanpa kesalahan belum tentu menghasilkan file baru, misalnya jika subtitle tidak tersedia atau media sudah ada.

## Seluruh opsi

| Opsi | Isi / perilaku |
|---|---|
| Jenis unduhan | Video, Audio MP3, Subtitle saja, Paket arsip |
| Kualitas maksimum | Batas resolusi sumber; tidak menaikkan kualitas sumber |
| Folder hasil | Pilih folder yang bisa ditulisi; bawaan `Downloads/Sedot Abis` |
| Unduh playlist | Nonaktif secara bawaan untuk mencegah unduhan seluruh playlist tanpa sengaja |
| Nomor playlist | Kosong = semua; `1-5` atau `1,3,5`, tanpa spasi |
| Sertakan subtitle | File subtitle terpisah, diutamakan VTT |
| Subtitle otomatis | Mengambil teks otomatis yang tersedia di platform, bukan membuat transkrip baru |
| Bahasa subtitle | `id`, `en`, `id,en`, bahasa lain seperti `ja`, atau `all` |
| Metadata tambahan | Deskripsi, thumbnail, dan JSON; otomatis pada Paket arsip |
| Catatan unduhan | Catatan per mode/kualitas di folder hasil; tidak berlaku untuk subtitle saja atau potongan |
| Waktu mulai/selesai | Format `JJ:MM:DD`, misalnya `00:05:00` sampai `00:08:30`; kosongkan keduanya untuk media utuh |
| Batas kecepatan | Kosong = tanpa batas; `500K` atau `2M`, dalam byte/detik |

Nama file menyertakan judul, ID sumber, kualitas atau MP3, dan waktu potongan bila dipakai. Berkas yang sudah ada tidak ditimpa. Untuk menambah subtitle/metadata pada unduhan lama, nonaktifkan catatan unduhan dahulu. Potongan mungkin mengikuti keyframe; periksa hasil bila membutuhkan presisi editing.

## Python utama dan lingkungan .venv

`INSTALL.bat` membuat `.venv` di folder aplikasi. Sedot Abis berjalan menggunakan `.venv/Scripts/python.exe`, sehingga paket pada Python lain tidak otomatis tersedia untuk aplikasi.

Contoh: paket yang ada di `C:\Users\Ronny\AppData\Local\Programs\Python\Python310\Lib\site-packages` tidak otomatis terbaca oleh `.venv` yang memakai Python 3.13. Tidak perlu menghapus Python lama atau menyalin site-packages secara manual.

Untuk memasang/memperbarui dependensi aplikasi, buka Command Prompt di folder yang berisi `MULAI.bat` dan jalankan:

```bat
".venv\Scripts\python.exe" -m pip install -U "yt-dlp[default,curl-cffi]"
```

Periksa kemampuan impersonation:

```bat
".venv\Scripts\python.exe" -m yt_dlp --list-impersonate-targets
```

Periksa lokasi paket jika masih bermasalah:

```bat
".venv\Scripts\python.exe" -m pip show curl-cffi
".venv\Scripts\python.exe" -c "import sys, curl_cffi; print(sys.executable); print(curl_cffi.__file__)"
```

Nama tambahan pip adalah `curl-cffi`; nama modul Python adalah `curl_cffi`. Sejak v1.0.2, **INSTALL.bat** dan **Perbarui yt-dlp** menyertakan dependensi ini.

## Memperbarui aplikasi yang sudah terpasang

Untuk naik dari versi 1.0.0/1.0.1 ke 1.0.2:

1. Tutup Sedot Abis.
2. Ekstrak ZIP rilis terbaru ke folder sementara.
3. Salin `sedot_abis.py`, `sedot_core.py`, `requirements.txt`, `PANDUAN.txt`, dan `PANDUAN.html` ke folder aplikasi lama; pilih **Replace / Ganti**.
4. Pertahankan folder `.venv` dan `tools`, serta folder hasil unduhan.
5. Buka `MULAI.bat`. Pastikan header menampilkan **v1.0.2**.
6. Jika curl_cffi belum tersedia, klik **Perbarui yt-dlp**.

Tidak perlu memasang Python atau FFmpeg/Deno lagi jika sudah berfungsi. Pembaruan yt-dlp tidak memperbarui kode Sedot Abis atau alat FFmpeg/Deno. Bantuan saja dapat diperbarui dengan mengganti kedua file `PANDUAN` dan membuka ulang aplikasi.

## Pemecahan masalah

| Pesan / gejala | Langkah |
|---|---|
| Python tidak ditemukan | Buka terminal baru; pastikan `py -3` atau `python` menjalankan Python 3.10+ |
| No module named tkinter | Tambahkan Tcl/Tk melalui installer Python |
| No module named yt_dlp | Jalankan INSTALL.bat pada folder aplikasi yang dipakai |
| No impersonate target is available | Pasang curl_cffi pada `.venv`, lalu periksa daftar target browser |
| FFmpeg / ffprobe / Deno tidak ditemukan | Buka ulang aplikasi setelah winget, atau gunakan `tools/bin` |
| Hanya folder terbuka | Klik Sedot sekarang di kiri, bukan Buka folder hasil di kanan |
| Tombol bawah tidak terbaca | Gunakan kode versi 1.0.1 atau lebih baru |
| HTTP 403 / 429 | Perbarui yt-dlp, periksa akses sumber, dan tunggu sebelum mencoba ulang |
| Login diperlukan | UI versi ini belum mendukung cookies/login |
| Subtitle tidak muncul | Coba bahasa `all`; periksa ketersediaan subtitle dan log |
| File .part | Unduhan belum selesai; coba kembali tautan, folder, dan pilihan yang sama |
| Permission denied / ruang habis | Pilih folder yang bisa ditulisi dan pastikan ruang cukup |
| File dilewati | Periksa berkas yang sudah ada atau matikan catatan unduhan |

**WARNING** adalah peringatan dan tidak selalu menghentikan proses. **ERROR** menunjukkan masalah proses. Jika masih gagal, simpan log lengkap dari **Mulai** hingga **ERROR** melalui **Simpan log**, lalu periksa isinya sebelum dibagikan.

## Penyimpanan dan batas

- Pengaturan terakhir: `%LOCALAPPDATA%/SedotAbis/settings.json`. Tautan tidak disimpan otomatis.
- Video, audio, subtitle, metadata, dan catatan berada pada folder tujuan pengguna.
- Log dapat diekspor manual; tampilan dibatasi sekitar 5.000 baris.
- Aplikasi berjalan lokal tanpa server Zonautara atau API AI.
- Format video mengikuti sumber (MP4, WebM, atau MKV); belum memaksa MP4.
- UI belum menyediakan login/cookies, kontrol livestream, atau pengumpulan komentar.
- Subtitle otomatis perlu diverifikasi sebelum dipakai sebagai kutipan jurnalistik.
- Metadata adalah informasi dari platform saat pengambilan, bukan jaminan kebenaran atau bukti keaslian.
- Dukungan situs mengikuti yt-dlp, akses sumber, dan perubahan sistem situs.

Gunakan konten sesuai akses dan izin penggunaannya. Metadata JSON dan log dapat memuat informasi sumber atau personal; periksa sebelum membagikan.

## Struktur repository

```text
sedot_abis.py               Antarmuka dan alur pekerjaan
sedot_core.py               Validasi, perintah, dan subprocess
INSTALL.bat                Pemasangan dependensi dalam .venv
MULAI.bat                  Peluncur Windows
PASANG_ALAT.bat             Pemasangan FFmpeg dan Deno
requirements.txt           Dependensi Python
PANDUAN.txt / PANDUAN.html  Bantuan offline
CHANGELOG.md               Riwayat versi
RELEASE_NOTES.md            Catatan rilis
THIRD_PARTY.md              Sumber dan lisensi komponen
scripts/build_release.py   Pembuat ZIP dan checksum
tests/                     Pengujian inti dan regresi GUI
.github/workflows/         Pengujian Windows dan publikasi rilis
dist/                      Paket rilis cadangan
```

## Pengujian dan membuat rilis

Dari folder repository:

```bat
python -m unittest discover -s tests -v
python scripts\build_release.py
```

Pengujian GUI berjalan jika Windows atau Linux mempunyai display yang tersedia. Pengujian menggunakan mesin unduhan simulasi; tidak mengunduh media dari internet. Pengujian inti mencakup opsi unduhan, input, subprocess, dan pembatalan.

Workflow GitHub Actions pada branch `main` menguji Windows, membangun ZIP beserta checksum, lalu membuat Release untuk versi yang belum memiliki rilis. Jika versi sudah diterbitkan, workflow tidak menimpa rilis lama. Untuk rilis berikutnya, naikkan `VERSION` pada kode dan perbarui catatan rilis sebelum mengirim perubahan.

Pengujian otomatis tidak membuktikan semua URL dapat diunduh. Unduhan langsung dari situs tetap perlu diuji sesuai akses dan kebutuhan tim.

## Komponen pihak ketiga

Lihat [THIRD_PARTY.md](THIRD_PARTY.md). Kode aplikasi ini disiapkan untuk penggunaan internal; repository tidak memberikan lisensi terbuka baru untuk seluruh proyek. Lisensi komponen pihak ketiga tetap berlaku masing-masing.
