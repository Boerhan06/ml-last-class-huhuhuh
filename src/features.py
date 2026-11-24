import numpy as np

NAMA_FITUR = ["mean", "std", "min", "max", "rms"]


def buat_data_contoh(kondisi, rng):
    """
    Membuat 100 titik data sinyal sintetis untuk simulasi pembacaan sensor.
    Kondisi 'normal' menghasilkan amplitudo rendah,
    sedangkan 'getaran_tinggi' menghasilkan amplitudo dan noise tinggi.
    """
    waktu = np.arange(100) / 50
    fase = rng.uniform(0, 2 * np.pi)
    frekuensi = rng.uniform(3, 7)
    if kondisi == "normal":
        amplitudo = rng.uniform(0.15, 0.4)
        noise = 0.05
    else:
        amplitudo = rng.uniform(0.9, 1.5)
        noise = 0.15
    return (
        amplitudo * np.sin(2 * np.pi * frekuensi * waktu + fase)
        + rng.normal(0, noise, 100)
    )


def hitung_fitur(nilai):
    """
    Mengekstrak 5 nilai ringkasan statistik (mean, std, min, max, rms)
    dari tepat 100 titik data sensor.
    """
    x = np.asarray(nilai, dtype=float)
    if x.ndim != 1 or len(x) != 100:
        raise ValueError("Diperlukan tepat 100 nilai sensor.")
    if not np.isfinite(x).all():
        raise ValueError("Ada nilai sensor yang tidak valid.")
    return {
        "mean": float(x.mean()),
        "std": float(x.std(ddof=0)),
        "min": float(x.min()),
        "max": float(x.max()),
        "rms": float(np.sqrt(np.mean(x ** 2))),
    }
