# Komponen pihak ketiga

Sedot Abis memakai alat dan paket berikut. Binary Python, FFmpeg, dan Deno tidak disertakan dalam paket rilis; pemasangan dilakukan dari sumbernya. Paket Python tambahan diambil melalui pip dari PyPI.

| Komponen | Fungsi | Sumber dan lisensi |
|---|---|---|
| Python / Tkinter | Runtime dan antarmuka desktop | [Python](https://www.python.org/), [lisensi](https://docs.python.org/3/license.html); Tcl/Tk memiliki ketentuan tersendiri |
| yt-dlp | Ekstraksi dan unduhan media | [yt-dlp](https://github.com/yt-dlp/yt-dlp), [lisensi](https://github.com/yt-dlp/yt-dlp/blob/master/LICENSE) |
| yt-dlp-ejs | Komponen JavaScript untuk dukungan YouTube | [EJS](https://github.com/yt-dlp/ejs), lisensi komponennya tersedia pada upstream |
| FFmpeg / ffprobe | Pemrosesan media | [FFmpeg](https://ffmpeg.org/), [ketentuan lisensi menurut build](https://ffmpeg.org/legal.html) |
| Deno | Runtime JavaScript | [Deno](https://github.com/denoland/deno), [lisensi](https://github.com/denoland/deno/blob/main/LICENSE.md) |
| curl_cffi | Impersonation permintaan browser | [curl_cffi](https://github.com/lexiforest/curl_cffi), lisensi tersedia pada upstream |

Dependensi transitif seperti requests, certifi, brotli, mutagen, pycryptodomex, dan websockets memakai lisensi masing-masing. Daftar dependensi dapat berubah mengikuti versi yt-dlp. Baca dokumentasi dan berkas lisensi sumber ketika mendistribusikan binary atau paket tambahan.
