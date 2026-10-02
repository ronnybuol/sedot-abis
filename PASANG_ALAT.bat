@echo off
setlocal
cd /d "%~dp0"
title Komponen tambahan Sedot Abis
echo SEDOT ABIS - FFMPEG DAN DENO
echo Skrip ini memasang FFmpeg dan Deno melalui Windows Package Manager.
echo Ikuti persetujuan paket dan izin Windows yang muncul.
echo Jika sudah terpasang, Anda dapat memakai cara manual di PANDUAN.html.
echo.
where winget >nul 2>&1
if errorlevel 1 goto nowinget
winget install --id Gyan.FFmpeg --exact
if errorlevel 1 echo FFmpeg belum berhasil dipasang atau sudah tersedia. Periksa keluaran di atas.
winget install --id DenoLand.Deno --exact
if errorlevel 1 echo Deno belum berhasil dipasang atau sudah tersedia. Periksa keluaran di atas.
echo.
echo Tutup Sedot Abis dan jendela Command Prompt, lalu buka MULAI.bat lagi.
echo Pada Status dan log, klik Cek komponen untuk memastikan hasilnya.
pause
exit /b 0
:nowinget
echo winget tidak ditemukan. Buka PANDUAN.html bagian 3 untuk cara manual.
start "" "PANDUAN.html"
pause
exit /b 1
