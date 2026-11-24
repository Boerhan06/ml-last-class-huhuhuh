import numpy as np
import pandas as pd

try:
    from src.features import NAMA_FITUR, hitung_fitur
except ImportError:
    from features import NAMA_FITUR, hitung_fitur


class PengolahData:
    def __init__(self, paket_model):
        if (
            paket_model["jumlah_data"] != 100
            or paket_model["nama_fitur"] != NAMA_FITUR
            or paket_model["target_hz"] != 50
        ):
            raise ValueError("Pengaturan model tidak cocok dengan aplikasi.")
        self.model = paket_model["model"]
        self.penampungan = []
        self.nomor_terakhir = 0
        self.riwayat = []
        self.terbaru = None
        self.jumlah_hasil = 0
        self.celah = 0

    def masukkan(self, kumpulan_data):
        urut = sorted(kumpulan_data, key=lambda x: int(x["nomor"]))
        for data in urut:
            nomor = int(data["nomor"])
            if nomor <= self.nomor_terakhir:
                continue
            if not np.isfinite(float(data["nilai"])):
                raise ValueError("Nilai sensor tidak valid.")
            if nomor != self.nomor_terakhir + 1:
                self.penampungan.clear()
                self.celah += 1
            self.penampungan.append(data)
            self.nomor_terakhir = nomor
            if len(self.penampungan) == 100:
                kelompok = self.penampungan.copy()
                fitur = hitung_fitur([d["nilai"] for d in kelompok])
                X = pd.DataFrame([fitur], columns=NAMA_FITUR)
                hasil = str(self.model.predict(X)[0])
                durasi = (kelompok[-1]["waktu_ms"] - kelompok[0]["waktu_ms"]) / 1000
                kecepatan = 99 / durasi if durasi > 0 else 0
                kondisi = {d.get("kondisi_contoh", "-") for d in kelompok}
                catatan = {
                    "data_awal": kelompok[0]["nomor"],
                    "data_akhir": kelompok[-1]["nomor"],
                    "hasil_model": hasil,
                    "kondisi_contoh": next(iter(kondisi)) if len(kondisi) == 1 else "campuran",
                    "data_per_detik_terukur": round(kecepatan, 2),
                    **fitur,
                }
                self.terbaru = {"data": kelompok, "fitur": X, "catatan": catatan}
                self.riwayat.append(catatan)
                self.riwayat = self.riwayat[-200:]
                self.jumlah_hasil += 1
                self.penampungan.clear()
