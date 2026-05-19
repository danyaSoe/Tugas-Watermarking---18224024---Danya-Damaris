# Tugas Watermarking Foto Wajah & Evaluasi Kompresi JPEG

Repositori ini dibuat untuk memenuhi tugas mata kuliah Multimedia / Pengolahan Citra Digital. Proyek ini mengimplementasikan teknik *Informed Digital Image Watermarking* pada domain frekuensi (DCT), serta menguji ketahanannya terhadap gangguan kompresi JPEG dengan berbagai Quality Factor (QF).

## 🌟 Fitur Utama
- Konversi ruang warna ke kanal **YUV (Luminance Y)** untuk minimalkan persepsi perubahan visual.
- Penyisipan bit biner ($32 \times 32$) pada koefisien frekuensi menengah DCT `[0,1]` dan `[1,0]`.
- Pengujian otomatis ketahanan watermark menggunakan parameter **Quality Factor (QF)**: 90, 70, 50, 30, 10, 5, dan 1.
- Evaluasi metrik performa kuantitatif: **Normalized Correlation (NC)**, **Bit Error Rate (BER)**, dan **PSNR**.

## 📂 Struktur Repositori

```
tugas-watermarking-jpeg/
│
├── data/
│   ├── input/
│   │   ├── wajah.JPG              # Foto wajah asli Anda (taruh di sini)
│   │   └── watermark.png          # Logo biner asli (ITB Jazz / R)
│   │
│   └── output/
│       ├── wajah_watermarked.jpg  # Hasil citra setelah disisipkan watermark
│       ├── compressed_qf_90.jpg   # Hasil kompresi berbagai QF
│       ├── compressed_qf_70.jpg
│       └── ...
│
├── src/
│   ├── __init__.py
│   ├── embedding.py               # Fungsi `embed_watermark`
│   ├── extraction.py              # Fungsi `extract_watermark_from_images`
│   └── main.py                    # Skrip utama untuk menjalankan eksperimen & grafik
│
├── reports/
│   ├── grafik_kinerja_dark.png
│   └── grafik_kinerja_light.png
│
├── .gitignore
├── README.md
└── requirements.txt
```

## 🚀 Cara Menjalankan Kode

### Prasyarat
Pastikan Anda sudah memasang Python 3.8+ dan dependensi:

```bash
pip install -r requirements.txt
```

### Menjalankan eksperimen

1. Letakkan `wajah.JPG` dan `watermark.png` di folder `data/input/`.
2. Jalankan skrip utama:

```bash
python src/main.py
```

Hasil citra akan disimpan di `data/output/` dan grafik performa akan tersimpan di `reports/`.

## 📊 Interpretasi Singkat Hasil
- Watermark biner (32×32) diekstrak dan dinilai menggunakan NC/BER.
- Threshold sederhana: `NC >= 0.5` dan `BER <= 0.3` dianggap `VALID`.
- Eksperimen tipikal menunjukkan watermark bertahan sampai QF rendah tertentu, sedangkan QF sangat kecil (mis. 5 atau 1) biasanya merusak (BER tinggi).

---
Jika Anda ingin saya menjalankan skrip ini di lingkungan Anda (atau menambahkan opsi CLI), beri tahu saya.
