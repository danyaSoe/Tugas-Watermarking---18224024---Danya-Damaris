import cv2
import numpy as np
from pathlib import Path


def extract_watermark(watermarked_image, cover_path):
    if isinstance(watermarked_image, (str, Path)):
        wm_img = cv2.imread(str(watermarked_image))
    else:
        wm_img = watermarked_image

    cover = cv2.imread(str(cover_path))
    if cover is None:
        raise FileNotFoundError(f"File {cover_path} tidak ditemukan!")

    h, w, _ = cover.shape
    h_new, w_new = (h // 32) * 32, (w // 32) * 32

    cover_resized = cv2.resize(cover, (w_new, h_new))
    wm_img_resized = cv2.resize(wm_img, (w_new, h_new))

    yuv_orig = cv2.cvtColor(cover_resized, cv2.COLOR_BGR2YUV)
    y_orig, _, _ = cv2.split(yuv_orig)

    yuv_wm = cv2.cvtColor(wm_img_resized, cv2.COLOR_BGR2YUV)
    y_wm, _, _ = cv2.split(yuv_wm)

    y_orig_f = y_orig.astype(np.float32)
    y_wm_f = y_wm.astype(np.float32)

    block_h, block_w = h_new // 32, w_new // 32
    extracted_wm = np.zeros((32, 32), dtype=np.uint8)

    for i in range(32):
        for j in range(32):
            by, bx = i * block_h, j * block_w

            block_orig = y_orig_f[by:by+block_h, bx:bx+block_w]
            block_wm = y_wm_f[by:by+block_h, bx:bx+block_w]

            dct_orig = cv2.dct(block_orig)
            dct_wm = cv2.dct(block_wm)

            diff_01 = dct_wm[0, 1] - dct_orig[0, 1]
            diff_10 = dct_wm[1, 0] - dct_orig[1, 0]

            if diff_01 - diff_10 > 0:
                extracted_wm[i, j] = 1
            else:
                extracted_wm[i, j] = 0

    return extracted_wm
