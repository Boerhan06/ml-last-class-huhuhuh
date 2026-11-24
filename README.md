# IoT Sensor Stream & Real-time Machine Learning Deployment

Proyek ini mengimplementasikan simulasi pipeline IoT dan deployment model Machine Learning untuk klasifikasi kondisi getaran (kondisi `normal` vs `getaran_tinggi`) secara *real-time* berbasis streaming data ke **Firebase Realtime Database** dan divisualisasikan melalui **Streamlit**.

---

## 📁 Struktur Direktori

Struktur proyek telah diklasifikasikan ke dalam folder-folder tematik agar rapi, modular, dan mudah dikelola:

```text
ml-last-class-huhuhuh/
│
├── config/                          # Konfigurasi & Kredensial Firebase
│   ├── config.example.json          # Template konfigurasi database
│   ├── config.json                  # URL database aktif (git-ignored)
│   └── serviceAccountKey.json       # Kunci privat Firebase Admin SDK (git-ignored)
│
├── models/                          # Model Machine Learning & Artefak
│   └── model.joblib                 # Model Random Forest ter-pretrain (input: 5 fitur)
│
├── src/                             # Modul Inti Pemrosesan & Integrasi
│   ├── __init__.py
│   ├── features.py                  # Ekstraksi fitur statistik sinyal (mean, std, min, max, rms)
│   ├── koneksi.py                   # Handler koneksi Firebase Admin SDK
│   └── prediksi.py                  # Windowing buffer 100 sampel & inferensi model
│
├── tests/                           # Skrip Verifikasi & Pengujian
│   ├── cek_model.py                 # Uji inferensi model & ekstraksi fitur tanpa internet
│   └── cek_firebase.py              # Uji coba pembacaan & penulisan data ke Firebase
│
├── docs/                            # Dokumentasi & Panduan Praktikum
│   ├── Modul Panduan.pdf            # PDF panduan lengkap praktikum
│   └── screenshots/                 # Tangkapan layar dashboard live
│       ├── streamlit_hero.png
│       └── streamlit_dashboard.png
│
├── app.py                           # [Entrypoint] Dashboard visualisasi Streamlit
├── sensor_dummy.py                  # [Entrypoint] Simulator sensor IoT pengirim data
├── requirements.txt                 # Daftar dependensi Python
├── .gitignore                       # Proteksi kredensial rahasia & virtual environment
└── README.md                        # Dokumentasi proyek
```

---

## ⚙️ Arsitektur & Alur Kerja Sistem

```
+-------------------------------------------------------------+
| 1. SIMULATOR SENSOR (sensor_dummy.py)                       |
|    - Frekuensi sampling: 50 Hz (0.02 detik per sampel)      |
|    - Batch pengiriman: 10 sampel per pengiriman             |
+-------------------------------------------------------------+
                              │
                              ▼ (HTTPS / REST)
+-------------------------------------------------------------+
| 2. FIREBASE REALTIME DATABASE                               |
|    - Menyimpan sampel mentah, nomor urut, waktu (ms)        |
|    - Path: /latihan_sensor/pengiriman/<id>/data/            |
+-------------------------------------------------------------+
                              │
                              ▼ (Polling setiap 1 detik)
+-------------------------------------------------------------+
| 3. CONSUMER / WINDOW BUFFER (src/prediksi.py)               |
|    - Mengurutkan nomor data & mendeteksi celah (gap)        |
|    - Mengumpulkan window 100 data baru                      |
+-------------------------------------------------------------+
                              │
                              ▼ (Ekstraksi 5 Fitur: mean, std, min, max, rms)
+-------------------------------------------------------------+
| 4. MODEL MACHINE LEARNING (models/model.joblib)             |
|    - Prediksi klasifikasi: 'normal' vs 'getaran_tinggi'     |
+-------------------------------------------------------------+
                              │
                              ▼
+-------------------------------------------------------------+
| 5. DASHBOARD STREAMLIT (app.py)                             |
|    - Menampilkan grafik 100 nilai sensor terbaru            |
|    - Menampilkan hasil prediksi, ringkasan fitur, & riwayat |
+-------------------------------------------------------------+
```

---

## 🚀 Panduan Menjalankan

### 1. Persiapan Environment
Gunakan Python 3.12 (64-bit):
```powershell
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 2. Konfigurasi Firebase
1. Salin `config/config.example.json` menjadi `config/config.json`.
2. Masukkan URL Realtime Database Anda pada field `database_url`.
3. Letakkan kunci Firebase Admin SDK Anda di `config/serviceAccountKey.json`.

### 3. Verifikasi Sistem
Jalankan pengujian lokal dan koneksi cloud:
```powershell
# 1. Uji model ML (offline)
.venv\Scripts\python.exe tests/cek_model.py

# 2. Uji koneksi Firebase (online)
.venv\Scripts\python.exe tests/cek_firebase.py
```

### 4. Menjalankan Sistem
Jalankan simulator sensor dan dashboard pada 2 terminal terpisah:

- **Terminal A (Simulator Sensor):**
  ```powershell
  .venv\Scripts\python.exe sensor_dummy.py
  ```

- **Terminal B (Dashboard Streamlit):**
  ```powershell
  .venv\Scripts\python.exe -m streamlit run app.py
  ```

Buka browser di **[http://localhost:8501](http://localhost:8501)** untuk melihat visualisasi grafik dan hasil prediksi secara real-time.
