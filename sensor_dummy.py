import sys
import time
import uuid
from pathlib import Path
import numpy as np

ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

try:
    from src.features import buat_data_contoh
    from src.koneksi import buka_database
except ImportError:
    from features import buat_data_contoh
    from koneksi import buka_database

akar = buka_database()
id_pengiriman = uuid.uuid4().hex
lokasi = akar.child("pengiriman").child(id_pengiriman)
lokasi.child("pengaturan").set({"target_data_per_detik": 50})
akar.child("pengiriman_aktif").set(id_pengiriman)
print("Sensor contoh berjalan. Tekan Ctrl+C untuk berhenti.", flush=True)
print("ID pengiriman:", id_pengiriman, flush=True)

rng = np.random.default_rng(2026)
nomor = 1
putaran = 0
menunggu_dikirim = {}
try:
    while True:
        kondisi = "normal" if (putaran // 5) % 2 == 0 else "getaran_tinggi"
        for nilai in buat_data_contoh(kondisi, rng):
            mulai = time.perf_counter()
            nama_data = f"d{nomor:012d}"
            menunggu_dikirim[nama_data] = {
                "nomor": nomor,
                "waktu_ms": int(time.time() * 1000),
                "nilai": float(nilai),
                "kondisi_contoh": kondisi,
            }
            if len(menunggu_dikirim) == 10:
                lokasi.child("data").update(menunggu_dikirim)
                print(f"Terkirim sampai data ke-{nomor}: {kondisi}", flush=True)
                menunggu_dikirim.clear()
            nomor += 1
            time.sleep(max(0, 0.02 - (time.perf_counter() - mulai)))
        putaran += 1
except KeyboardInterrupt:
    if menunggu_dikirim:
        lokasi.child("data").update(menunggu_dikirim)
    print("Sensor contoh dihentikan.")
