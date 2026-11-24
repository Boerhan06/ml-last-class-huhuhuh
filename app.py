import sys
import time
from pathlib import Path
import joblib
import pandas as pd
import streamlit as st

ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

try:
    from src.koneksi import buka_database
    from src.prediksi import PengolahData
except ImportError:
    from koneksi import buka_database
    from prediksi import PengolahData


def cari_model():
    p = ROOT_DIR / "models" / "model.joblib"
    if p.exists():
        return p
    return ROOT_DIR / "model.joblib"


st.set_page_config(page_title="Latihan Sensor", layout="wide")
st.title("Latihan membaca sensor dan menampilkan prediksi")
st.write("Setiap prediksi menggunakan 100 data baru.")


@st.cache_resource
def persiapan():
    akar = buka_database()
    paket = joblib.load(cari_model())
    return akar, paket


try:
    akar, paket = persiapan()
except Exception as error:
    st.error(f"Persiapan gagal: {error}")
    st.stop()


@st.fragment(run_every="1s")
def tampilkan():
    try:
        id_aktif = akar.child("pengiriman_aktif").get()
        if not id_aktif:
            st.info("Belum ada data. Jalankan sensor_dummy.py terlebih dahulu.")
            return
        if st.session_state.get("id_pengiriman") != id_aktif:
            st.session_state.id_pengiriman = id_aktif
            st.session_state.pengolah = PengolahData(paket)
        pengolah = st.session_state.pengolah
        lokasi = akar.child("pengiriman").child(id_aktif)
        pengaturan = lokasi.child("pengaturan").get() or {}
        if pengaturan.get("target_data_per_detik") != paket["target_hz"]:
            raise ValueError("Pengaturan sensor berbeda dari model.")
        mulai = f"d{pengolah.nomor_terakhir+1:012d}"
        data_baru = (
            lokasi.child("data")
            .order_by_key()
            .start_at(mulai)
            .limit_to_first(1000)
            .get()
            or {}
        )
        pengolah.masukkan(list(data_baru.values()))
    except Exception as error:
        st.error(f"Belum berhasil membaca atau mengolah data: {error}")
        return

    st.caption(f"ID pengiriman yang sedang dibaca: {id_aktif}")
    a, b, c = st.columns(3)
    a.metric("Nomor data terakhir dibaca", pengolah.nomor_terakhir)
    b.metric("Data menunggu prediksi (dari 100)", len(pengolah.penampungan))
    c.metric("Jumlah prediksi sejak halaman dibuka", pengolah.jumlah_hasil)
    if len(data_baru) == 1000:
        st.info("Masih membaca data yang menumpuk. Tunggu beberapa saat.")
    if pengolah.celah:
        st.warning("Ada nomor data yang terlewat. Penampungan dimulai ulang setelah celah.")
    if pengolah.terbaru is None:
        st.info("Menunggu sampai terkumpul 100 data pertama.")
        return
    terbaru = pengolah.terbaru
    catatan = terbaru["catatan"]
    x, y = st.columns(2)
    x.metric("Hasil prediksi model", catatan["hasil_model"])
    y.metric("Kondisi yang dibuat sensor contoh", catatan["kondisi_contoh"])
    st.caption(
        f"Hasil ini memakai data ke-{catatan['data_awal']} "
        f"sampai ke-{catatan['data_akhir']}."
    )
    usia = max(0, time.time() - terbaru["data"][-1]["waktu_ms"] / 1000)
    st.caption(f"Data terakhir pada hasil ini dibuat {usia:.1f} detik lalu.")
    if usia > 10:
        st.warning(
            "Hasil ini belum baru. Periksa sensor contoh atau tunggu pembacaan data lama selesai."
        )
    tabel = pd.DataFrame(terbaru["data"])
    tabel["detik"] = (tabel["waktu_ms"] - tabel["waktu_ms"].iloc[0]) / 1000
    st.subheader("100 nilai sensor yang digunakan")
    st.line_chart(tabel, x="detik", y="nilai")
    with st.expander("Lihat semua 100 baris data"):
        st.dataframe(tabel, hide_index=True)
    st.subheader("Ringkasan yang diberikan kepada model")
    st.dataframe(terbaru["fitur"], hide_index=True)
    st.caption(
        "Kecepatan sensor yang terukur pada kelompok ini: "
        f"{catatan['data_per_detik_terukur']} data per detik. Targetnya 50."
    )
    st.subheader("Hasil-hasil sebelumnya")
    st.dataframe(pd.DataFrame(pengolah.riwayat).iloc[::-1], hide_index=True)


tampilkan()
