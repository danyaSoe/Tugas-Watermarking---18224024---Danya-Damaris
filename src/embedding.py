import cv2
import numpy as np
from pathlib import Path
from typing import Optional, Tuple


def embed_watermark(cover_path, watermark_path, alpha=15.0, save_intermediate: bool = False, output_dir: Optional[Path] = None) -> Tuple[np.ndarray, np.ndarray]:
    cover_path = Path(cover_path)
    watermark_path = Path(watermark_path)

    cover = cv2.imread(str(cover_path))
    if cover is None:
        raise FileNotFoundError(f"File {cover_path} tidak ditemukan!")

    wm = cv2.imread(str(watermark_path), cv2.IMREAD_GRAYSCALE)
    if wm is None:
        raise FileNotFoundError(f"File {watermark_path} tidak ditemukan!")

    wm_resized = cv2.resize(wm, (32, 32), interpolation=cv2.INTER_NEAREST)
    _, wm_binary = cv2.threshold(wm_resized, 127, 1, cv2.THRESH_BINARY)

    h, w, c = cover.shape
    h_new, w_new = (h // 32) * 32, (w // 32) * 32
    cover_resized = cv2.resize(cover, (w_new, h_new))

    yuv = cv2.cvtColor(cover_resized, cv2.COLOR_BGR2YUV)
    y, u, v = cv2.split(yuv)

    y_float = y.astype(np.float32)
    block_h, block_w = h_new // 32, w_new // 32

    for i in range(32):
        for j in range(32):
            by, bx = i * block_h, j * block_w
            block = y_float[by:by+block_h, bx:bx+block_w]
            block_dct = cv2.dct(block)

            if wm_binary[i, j] == 1:
                block_dct[0, 1] += alpha
                block_dct[1, 0] -= alpha
            else:
                block_dct[0, 1] -= alpha
                block_dct[1, 0] += alpha

            y_float[by:by+block_h, bx:bx+block_w] = cv2.idct(block_dct)

    y_watermarked = np.clip(y_float, 0, 255).astype(np.uint8)
    yuv_watermarked = cv2.merge((y_watermarked, u, v))
    watermarked_image = cv2.cvtColor(yuv_watermarked, cv2.COLOR_YUV2BGR)

    if save_intermediate:
        if output_dir is None:
            output_dir = cover_path.parent
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        cv2.imwrite(str(output_dir / 'watermark_binary.png'), wm_binary * 255)
        cv2.imwrite(str(output_dir / 'cover_y_channel.png'), y)
        cv2.imwrite(str(output_dir / 'watermarked_y_channel.png'), y_watermarked)

    # Resize back to original cover size
    watermarked_full = cv2.resize(watermarked_image, (w, h))

    return watermarked_full, wm_binary
