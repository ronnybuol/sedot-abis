"""Membuat paket rilis deterministik tanpa .venv, binary alat, atau data pengguna."""
from pathlib import Path
import hashlib
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]
FILES = (
    "sedot_abis.py", "sedot_core.py", "requirements.txt",
    "INSTALL.bat", "MULAI.bat", "PASANG_ALAT.bat",
    "PANDUAN.txt", "PANDUAN.html", "README.md",
    "CHANGELOG.md", "RELEASE_NOTES.md", "THIRD_PARTY.md",
    "tools/bin/LETAKKAN-ALAT-DI-SINI.txt",
    "tests/test_core.py", "tests/test_gui.py", "scripts/build_release.py",
)


def build():
    source = (ROOT / "sedot_abis.py").read_text(encoding="utf-8")
    match = re.search(r'^VERSION = "(\d+\.\d+\.\d+)"$', source, re.M)
    if not match:
        raise ValueError("VERSION aplikasi tidak ditemukan.")
    version = match.group(1)
    output = ROOT / "dist"
    output.mkdir(exist_ok=True)
    archive = output / f"Sedot-Abis-v{version}.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for name in sorted(FILES):
            file = ROOT / name
            data = file.read_bytes().replace(b"\r\n", b"\n")
            if file.suffix == ".bat":
                data = data.replace(b"\n", b"\r\n")
            info = zipfile.ZipInfo("Sedot-Abis/" + name, date_time=(2026, 10, 3, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    with zipfile.ZipFile(archive) as z:
        if z.testzip() is not None:
            raise ValueError("Paket rilis rusak.")
    checksum = hashlib.sha256(archive.read_bytes()).hexdigest()
    (output / "SHA256SUMS.txt").write_text(f"{checksum}  {archive.name}\n", encoding="utf-8")
    print(f"v{version}: {archive.name} ({archive.stat().st_size} bytes)")
    print("SHA256:", checksum)
    return archive


if __name__ == "__main__":
    build()
