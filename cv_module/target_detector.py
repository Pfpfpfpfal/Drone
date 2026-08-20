"""Детектор цветной цели (например, красного круга) через OpenCV.

На вход — кадр BGR. На выходе — координаты центра объекта, его радиус,
а также команда движения по горизонтали:

    если круг слева от центра кадра  -> повернуть влево
    если круг справа                 -> повернуть вправо
    если круг по центру              -> лететь вперёд

Детекция строится на пороге по цвету (HSV) + поиске контуров.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import cv2
import numpy as np


@dataclass
class Detection:
    """Результат детекции цели в кадре."""

    found: bool
    cx: float = 0.0   # центр по x (пиксели)
    cy: float = 0.0   # центр по y (пиксели)
    radius: float = 0.0
    area_fraction: float = 0.0  # доля площади кадра, занятая целью

    @property
    def command(self) -> str:
        """Текстовая команда (заполняется вне при наличии центра кадра)."""
        return self._command if hasattr(self, "_command") else "forward"

    def set_command(self, cmd: str) -> None:
        self._command = cmd


class TargetDetector:
    """Поиск цветной цели в кадре по диапазону HSV.

    Параметры:
        hsv_lower / hsv_upper: диапазон цвета цели (например, красного).
        min_area_fraction: минимальная доля площади кадра для считывания цели.
    """

    # Диапазон красного цвета по умолчанию (с учётом оборачивания H=0..179).
    DEFAULT_LOWER = (0, 100, 100)
    DEFAULT_UPPER = (10, 255, 255)

    def __init__(
        self,
        hsv_lower: Tuple[int, int, int] = DEFAULT_LOWER,
        hsv_upper: Tuple[int, int, int] = DEFAULT_UPPER,
        min_area_fraction: float = 0.002,
    ) -> None:
        self.hsv_lower = np.array(hsv_lower, dtype=np.uint8)
        self.hsv_upper = np.array(hsv_upper, dtype=np.uint8)
        self.min_area_fraction = min_area_fraction

    def _mask_from_hsv(self, hsv: np.ndarray) -> np.ndarray:
        """Бинарная маска пикселей, попадающих в диапазон цвета."""
        mask = cv2.inRange(hsv, self.hsv_lower, self.hsv_upper)
        # красный цвет «оборачивается» через 0 градусов — добавим верхний кусок
        if self.hsv_lower[0] < self.hsv_upper[0]:
            mask = cv2.bitwise_or(
                mask,
                cv2.inRange(
                    hsv,
                    np.array([self.hsv_lower[0], self.hsv_lower[1], self.hsv_lower[2]], np.uint8),
                    np.array([179, self.hsv_upper[1], self.hsv_upper[2]], np.uint8),
                ),
            )
        # убираем шум
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
        mask = cv2.dilate(mask, np.ones((5, 5), np.uint8), iterations=2)
        return mask

    def detect(self, frame_bgr: np.ndarray) -> Detection:
        """Поиск цели в кадре BGR."""
        hsv = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV)
        mask = self._mask_from_hsv(hsv)

        contours, _ = cv2.findContours(
            mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        if not contours:
            return Detection(found=False)

        # берём самый большой контур
        largest = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(largest)
        frame_area = frame_bgr.shape[0] * frame_bgr.shape[1]
        area_fraction = area / frame_area

        if area_fraction < self.min_area_fraction:
            return Detection(found=False)

        (cx, cy), radius = cv2.minEnclosingCircle(largest)
        return Detection(
            found=True,
            cx=float(cx),
            cy=float(cy),
            radius=float(radius),
            area_fraction=float(area_fraction),
        )

    def control_command(self, detection: Detection, frame_width: int) -> str:
        """Команда движения по горизонтальному смещению цели от центра кадра."""
        if not detection.found:
            return "search"
        center_x = frame_width / 2.0
        offset = detection.cx - center_x
        # порог «по центру», например 10% ширины кадра
        threshold = frame_width * 0.10
        if abs(offset) < threshold:
            return "forward"
        return "left" if offset < 0 else "right"

    def draw(self, frame_bgr: np.ndarray, detection: Detection) -> np.ndarray:
        """Отрисовка найденной цели на кадре (для визуализации)."""
        out = frame_bgr.copy()
        if detection.found:
            cv2.circle(
                out,
                (int(detection.cx), int(detection.cy)),
                int(detection.radius),
                (0, 255, 0),
                2,
            )
            cv2.circle(out, (int(detection.cx), int(detection.cy)), 3, (0, 255, 0), -1)
        return out


def command_to_motion(command: str, speed: float = 0.5) -> dict:
    """Преобразование текстовой команды в вектор движения дрона.

    Возвращает словарь {vx, vy, yaw_rate}: vx — вперёд, yaw_rate — поворот.
    """
    if command == "left":
        return {"vx": 0.0, "vy": 0.0, "yaw_rate": speed}
    if command == "right":
        return {"vx": 0.0, "vy": 0.0, "yaw_rate": -speed}
    if command == "search":
        return {"vx": 0.0, "vy": 0.0, "yaw_rate": speed * 0.5}
    # forward
    return {"vx": speed, "vy": 0.0, "yaw_rate": 0.0}