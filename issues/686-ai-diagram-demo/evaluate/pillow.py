"""Pillow 图片基础分析评估器。

提供客观技术指标（尺寸、清晰度、亮度分布、留白比等）。
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image


class PillowSingleEvaluator:
    """基于 Pillow 的图片基础分析评估器。

    计算图片的客观技术指标，供后续视觉 LLM 评估参考。
    """

    def evaluate(self, image_path: str) -> dict:
        """对单张图片执行 Pillow 基础分析。

        Args:
            image_path: 图片文件路径。

        Returns:
            包含尺寸、清晰度、亮度分布等指标的字典。
        """
        img = Image.open(image_path)
        w, h = img.size

        result: dict = {
            "file": Path(image_path).name,
            "width": w,
            "height": h,
            "aspect_ratio": round(w / h, 2),
            "resolution_megapixels": round(w * h / 1_000_000, 2),
        }

        try:
            import numpy as np
            from scipy.ndimage import convolve

            gray = np.array(img.convert("L"), dtype=np.float64)
            total = gray.size

            # 亮度分布
            bins = [0, 51, 102, 153, 204, 255]
            labels = ["极暗", "偏暗", "适中", "偏亮", "极亮"]
            brightness_dist: dict[str, float] = {}
            for i in range(5):
                count = int(np.sum((gray >= bins[i]) & (gray < bins[i + 1])))
                brightness_dist[labels[i]] = round(count / total * 100, 1)
            result["brightness_distribution_%"] = brightness_dist

            # 清晰度（拉普拉斯方差）
            lap = np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]], dtype=np.float64)
            edges = convolve(gray, lap)
            result["sharpness_score"] = round(float(np.var(edges)), 1)

            # 留白比
            white_ratio = float(np.sum(gray > 240)) / total * 100
            result["whitespace_ratio_%"] = round(white_ratio, 1)

        except ImportError:
            result["sharpness_score"] = "N/A"
            result["whitespace_ratio_%"] = "N/A"

        return result
