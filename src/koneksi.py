import json
from pathlib import Path
import firebase_admin
from firebase_admin import credentials, db

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent if (BASE_DIR.parent / "config").exists() else BASE_DIR


def temukan_file(nama_file):
    """
    Mencari file di direktori config/ atau root proyek secara dinamis.
    """
    kandidat = [
        PROJECT_ROOT / "config" / nama_file,
        PROJECT_ROOT / nama_file,
        BASE_DIR / nama_file,
    ]
    for p in kandidat:
        if p.is_file():
            return p
    return PROJECT_ROOT / "config" / nama_file


def buka_database():
    """
    Membuka koneksi ke Firebase Realtime Database menggunakan
    konfigurasi di config.json dan kredensial serviceAccountKey.json.
    """
    file_config = temukan_file("config.json")
    if not file_config.exists():
        raise FileNotFoundError(f"File config.json tidak ditemukan di {file_config}")

    pengaturan = json.loads(file_config.read_text(encoding="utf-8"))
    url = pengaturan.get("database_url", "").strip()
    if not url.startswith("https://"):
        raise ValueError("Isi URL database di config.json terlebih dahulu.")

    try:
        aplikasi = firebase_admin.get_app()
    except ValueError:
        file_key = temukan_file("serviceAccountKey.json")
        if not file_key.exists():
            raise FileNotFoundError(
                f"File serviceAccountKey.json tidak ditemukan di {file_key}"
            )
        key = credentials.Certificate(str(file_key))
        aplikasi = firebase_admin.initialize_app(
            key, {"databaseURL": url, "httpTimeout": 15}
        )
    return db.reference("/latihan_sensor", app=aplikasi)
