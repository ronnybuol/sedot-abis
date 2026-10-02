@echo off
setlocal
cd /d "%~dp0"
title Instalasi Sedot Abis
echo SEDOT ABIS - INSTALASI
echo Membuat lingkungan Python khusus di folder .venv.
echo Koneksi internet diperlukan untuk mengambil yt-dlp dari PyPI.
echo.
if exist ".venv\Scripts\python.exe" goto install
py -3 -c "import sys, tkinter; sys.exit(0 if sys.version_info >= (3,10) else 1)" >nul 2>&1
if not errorlevel 1 goto usepy
python -c "import sys, tkinter; sys.exit(0 if sys.version_info >= (3,10) else 1)" >nul 2>&1
if not errorlevel 1 goto usepython
echo Python 3.10 atau lebih baru dengan Tkinter belum ditemukan.
echo Buka PANDUAN.html untuk petunjuk memasang Python.
echo Python Anda sebelumnya versi 3.10 sudah memenuhi syarat.
pause
exit /b 1
:usepy
py -3 -m venv .venv
if errorlevel 1 goto fail
goto install
:usepython
python -m venv .venv
if errorlevel 1 goto fail
:install
".venv\Scripts\python.exe" -c "import sys, tkinter; sys.exit(0 if sys.version_info >= (3,10) else 1)"
if errorlevel 1 goto fail
".venv\Scripts\python.exe" -m pip install -U pip
if errorlevel 1 goto fail
".venv\Scripts\python.exe" -m pip install -U -r requirements.txt
if errorlevel 1 goto fail
echo.
echo BERHASIL. Klik MULAI.bat untuk membuka Sedot Abis.
echo Untuk video dan MP3, pasang FFmpeg. Untuk YouTube, pasang Deno.
echo Klik PASANG_ALAT.bat atau ikuti cara manual di PANDUAN.html.
pause
exit /b 0
:fail
echo.
echo Instalasi gagal. Periksa pesan di atas dan koneksi internet.
echo Lihat bagian Pemecahan masalah dalam PANDUAN.html.
pause
exit /b 1
