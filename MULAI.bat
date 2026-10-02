@echo off
setlocal
cd /d "%~dp0"
title Sedot Abis
if exist ".venv\Scripts\python.exe" goto run
echo Instalasi belum dilakukan. Jalankan INSTALL.bat terlebih dahulu.
pause
exit /b 1
:run
".venv\Scripts\python.exe" "sedot_abis.py"
if errorlevel 1 (
  echo.
  echo Aplikasi berhenti dengan kesalahan. Periksa pesan di atas.
  echo Buka PANDUAN.html untuk bantuan.
  pause
)
