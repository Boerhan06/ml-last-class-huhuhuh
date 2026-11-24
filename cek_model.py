import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import joblib
import numpy as np

try:
    from src.features import buat_data_contoh
    from src.prediksi import PengolahData
except ImportError:
    from features import buat_data_contoh
    from prediksi import PengolahData


def cari_model():
    p = ROOT_DIR / "models" / "model.joblib"
    if p.exists():
        return p
    return ROOT_DIR / "model.joblib"


paket = joblib.load(cari_model())
rng = np.random.default_rng(123)
for kondisi in ["normal", "getaran_tinggi"]:
    pengolah = PengolahData(paket)
    nilai = buat_data_contoh(kondisi, rng)
    data = [
        {
            "nomor": i + 1,
            "waktu_ms": i * 20,
            "nilai": float(v),
            "kondisi_contoh": kondisi,
        }
        for i, v in enumerate(nilai)
    ]
    pengolah.masukkan(data[:90])
    assert pengolah.jumlah_hasil == 0
    pengolah.masukkan(data[90:])
    hasil = pengolah.terbaru["catatan"]["hasil_model"]
    assert hasil == kondisi
    assert pengolah.terbaru["fitur"].shape == (1, 5)
    pengolah.masukkan(data)
    assert pengolah.jumlah_hasil == 1
    print(f"Contoh {kondisi} -> {hasil}: BERHASIL")
print("Model dan penampungan data siap digunakan.")
