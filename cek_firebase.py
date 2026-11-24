import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

try:
    from src.koneksi import buka_database
except ImportError:
    from koneksi import buka_database

akar = buka_database()
akar.child("tes_koneksi").set({"pesan": "Koneksi berhasil"})
hasil = akar.child("tes_koneksi").get()
print("Hasil baca:", hasil)
print("BERHASIL: Python sudah dapat mengakses Firebase.")
