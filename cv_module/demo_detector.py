#!/usr/bin/env python3
"""Демонстрация OpenCV-детектора цели на синтетическом изображении.

Создаёт картинку с красным кругом, находит его центр и выводит команду
движения без подключения реальной камеры.
"""

from __future__ import annotations

import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from target_detector import TargetDetector, command_to_motion  # noqa: E402


def make_test_frame(width: int = 640, height: int = 480) -> np.ndarray:
    """Синтетический кадр: тёмный фон + красный круг смещён вправо."""
    img = np.zeros((height, width, 3), dtype=np.uint8)
    img[:] = (60, 60, 60)  # серый фон (BGR)
    cx, cy, r = int(width * 0.7), int(height * 0.5), 40
    cv2.circle(img, (cx, cy), r, (0, 0, 255), -1)  # красный круг
    return img


def main() -> None:
    frame = make_test_frame()
    detector = TargetDetector()
    det = detector.detect(frame)
    command = detector.control_command(det, frame.shape[1])
    motion = command_to_motion(command)

    print("Цель найдена:", det.found)
    if det.found:
        print(f"  центр = ({det.cx:.1f}, {det.cy:.1f}), радиус = {det.radius:.1f}")
    print("Команда:", command)
    print("Движение:", motion)

    annotated = detector.draw(frame, det)
    out = Path(__file__).resolve().parent / "detection_result.png"
    cv2.imwrite(str(out), annotated)
    print(f"Кадр с разметкой сохранён: {out}")


if __name__ == "__main__":
    main()