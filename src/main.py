import cv2
import numpy as np
import matplotlib.pyplot as plt
import os
from pathlib import Path
from src.embedding import embed_watermark
from src.extraction import extract_watermark


def main():
    repo_root = Path(__file__).resolve().parent.parent
    input_dir = repo_root / 'data' / 'input'
    output_dir = repo_root / 'data' / 'output'
    reports_dir = repo_root / 'reports'

    output_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    cover_file = input_dir / 'wajah.JPG'
    watermark_file = input_dir / 'watermark.png'

    if not cover_file.exists() or not watermark_file.exists():
        raise FileNotFoundError('Letakkan `wajah.JPG` dan `watermark.png` di folder data/input terlebih dahulu.')

    img_watermarked, wm_orig_binary = embed_watermark(
        cover_file,
        watermark_file,
        save_intermediate=True,
        output_dir=output_dir,
    )
    cv2.imwrite(str(output_dir / 'wajah_watermarked.jpg'), img_watermarked, [int(cv2.IMWRITE_JPEG_QUALITY), 95])

    img_orig = cv2.imread(str(cover_file))
    h_o, w_o, _ = img_orig.shape
    h_n, w_n = (h_o // 32) * 32, (w_o // 32) * 32
    img_orig_cropped = cv2.resize(img_orig, (w_n, h_n))

    quality_factors = [90, 70, 50, 30, 10, 5, 1]
    nc_values = []
    ber_values = []
    psnr_values = []
    file_sizes = []
    compressed_images = []
    extracted_wms = []

    print("--- Memulai Evaluasi Ketahanan DCT Watermarking terhadap Kompresi JPEG --- \n")

    for qf in quality_factors:
        compressed_filename = output_dir / f'compressed_qf_{qf}.jpg'
        cv2.imwrite(str(compressed_filename), img_watermarked, [int(cv2.IMWRITE_JPEG_QUALITY), qf])

        img_compressed = cv2.imread(str(compressed_filename))
        extracted_wm_binary = extract_watermark(img_compressed, cover_file)
        cv2.imwrite(str(reports_dir / f'extracted_wm_qf_{qf}.png'), extracted_wm_binary * 255)

        numerator = np.sum(wm_orig_binary * extracted_wm_binary)
        denominator = np.sqrt(np.sum(wm_orig_binary**2) * np.sum(extracted_wm_binary**2))
        nc = numerator / denominator if denominator != 0 else 0
        nc_values.append(float(nc))

        ber = np.sum(wm_orig_binary != extracted_wm_binary) / wm_orig_binary.size
        ber_values.append(float(ber))

        mse_c = np.mean((img_orig_cropped - cv2.resize(img_compressed, (w_n, h_n))) ** 2)
        psnr_c = 20 * np.log10(255.0 / np.sqrt(mse_c)) if mse_c != 0 else 100
        psnr_values.append(float(psnr_c))

        file_size = os.path.getsize(str(compressed_filename)) / 1024
        file_sizes.append(float(file_size))
        compressed_images.append(img_compressed.copy())
        extracted_wms.append(extracted_wm_binary.copy())

        status = "VALID" if (nc >= 0.5 and ber <= 0.3) else "RUSAK"
        print(f"QF = {qf:2d} -> Ukuran: {file_size:6.2f} KB | NC: {nc:.3f} | BER: {ber:.3f} | PSNR: {psnr_c:.2f} dB | Status: {status}")

    plt.style.use('dark_background')
    fig_plot, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    fig_plot.suptitle('Grafik Kinerja Metrik Kuantitatif terhadap Kompresi', fontsize=14, fontweight='bold', y=0.98)

    ax1.plot(quality_factors, nc_values, marker='o', markersize=8, color='#50c5f1', linewidth=2.5, label='NC (Correlation)')
    ax1.axhline(y=0.5, color='#ff6b6b', linestyle='--', linewidth=1.5, label='Threshold Valid (NC >= 0.5)')
    ax1.set_title('Normalized Correlation (NC) vs QF', fontsize=12, pad=10)
    ax1.set_xlabel('Quality Factor (QF)', fontsize=10)
    ax1.set_ylabel('Nilai NC', fontsize=10)
    ax1.set_ylim(-0.05, 1.05)
    ax1.set_xticks(quality_factors)
    ax1.invert_xaxis()
    ax1.grid(True, linestyle=':', alpha=0.3)
    ax1.legend(loc='upper left')

    ax2.plot(quality_factors, ber_values, marker='s', markersize=8, color='#5f9f11', linewidth=2.5, label='BER (Error Rate)')
    ax2.axhline(y=0.3, color='#ff6b6b', linestyle='--', linewidth=1.5, label='Threshold Valid (BER <= 0.3)')
    ax2.set_title('Bit Error Rate (BER) vs QF', fontsize=12, pad=10)
    ax2.set_xlabel('Quality Factor (QF)', fontsize=10)
    ax2.set_ylabel('Nilai BER', fontsize=10)
    ax2.set_ylim(-0.05, 0.6)
    ax2.set_xticks(quality_factors)
    ax2.invert_xaxis()
    ax2.grid(True, linestyle=':', alpha=0.3)
    ax2.legend(loc='upper right')

    fig_plot.tight_layout()
    fig_plot.savefig(str(reports_dir / 'grafik_kinerja_dark.png'), dpi=200)

    print('\nPlot disimpan di folder `reports/`.')

    plt.style.use('default')
    n = len(quality_factors)
    fig_img, axes = plt.subplots(n, 2, figsize=(10, 3.5 * n))
    fig_img.suptitle('Analisis Visual Citra Terkompresi & Ekstraksi Watermark', fontsize=14, fontweight='bold', y=0.99)

    for idx, qf in enumerate(quality_factors):
        img_c = compressed_images[idx]
        wm_bin = extracted_wms[idx]
        psnr_c = psnr_values[idx]
        file_size = file_sizes[idx]
        nc = nc_values[idx]
        ber = ber_values[idx]
        status = "VALID" if (nc >= 0.5 and ber <= 0.3) else "RUSAK"
        color_status = 'green' if status == 'VALID' else 'red'

        ax_l = axes[idx, 0] if n > 1 else axes[0]
        img_rgb = cv2.cvtColor(img_c, cv2.COLOR_BGR2RGB)
        ax_l.imshow(img_rgb)
        ax_l.set_title(f"Foto Terkompresi (QF = {qf})\nUkuran: {file_size:.2f} KB | PSNR: {psnr_c:.2f} dB", fontsize=10)
        ax_l.axis('off')

        ax_r = axes[idx, 1] if n > 1 else axes[1]
        ax_r.imshow(wm_bin * 255, cmap='gray')
        ax_r.set_title(f"Ekstraksi Watermark (QF = {qf})\nNC: {nc:.3f} | BER: {ber:.3f}", fontsize=10)
        ax_r.text(1.05, 0.5, status, transform=ax_r.transAxes, color=color_status, fontweight='bold', fontsize=12, va='center')
        ax_r.axis('off')

    plt.tight_layout()
    fig_img.savefig(str(reports_dir / 'analisis_visual.png'), dpi=200)
    print('Gambar analisis visual disimpan di `reports/analisis_visual.png`.')


if __name__ == '__main__':
    main()
