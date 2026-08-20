"""Круглое препятствие для artificial potential fields."""

from __future__ import annotations

from typing import Sequence

import numpy as np


class Obstacle:
    """Препятствие в виде круга (2D) или сферы (3D).

    Атрибуты:
        center: координаты центра [x, y, z].
        radius: радиус препятствия.
        influence_radius: радиус зоны отталкивания вокруг препятствия
            (обычно > radius, чтобы дрон начинал маневр заранее).
    """

    def __init__(
        self,
        center: Sequence[float],
        radius: float,
        influence_radius: float | None = None,
    ) -> None:
        self.center = np.asarray(center, dtype=float)
        if len(self.center) == 2:  # автоматический перевод 2D -> 3D
            self.center = np.array([self.center[0], self.center[1], 0.0], dtype=float)
        self.radius = float(radius)
        # Зона влияния по умолчанию в 2 раза больше радиуса препятствия.
        self.influence_radius = float(influence_radius) if influence_radius else self.radius * 2.0

    def distance_from(self, point: Sequence[float]) -> float:
        """Расстояние от точки до поверхности препятствия."""
        p = np.asarray(point, dtype=float)
        return float(np.linalg.norm(p - self.center)) - self.radius

    def inside(self, point: Sequence[float]) -> bool:
        """Находится ли точка внутри препятствия."""
        return self.distance_from(point) <= 0.0

    def collision_free_distance(self, a: Sequence[float], b: Sequence[float]) -> bool:
        """Проверка, что отрезок a-b не пересекает препятствие.

        Используется в тестах для проверки обхода препятствий.
        """
        def _to3d(pt):
            pt = np.asarray(pt, dtype=float)
            if pt.ndim == 0:
                pt = pt.reshape(1)
            while pt.shape[0] < 3:
                pt = np.append(pt, 0.0)
            return pt

        p = _to3d(a)
        q = _to3d(b)
        d = q - p
        length = float(np.linalg.norm(d))
        if length < 1e-9:
            return not self.inside(p)

        u = d / length
        ap = p - self.center
        # проекция центра на прямую через p,q
        t = -float(np.dot(ap, u))
        # ближайшая точка отрезка
        t = max(0.0, min(length, t))
        closest = p + u * t
        dist_to_center = float(np.linalg.norm(closest - self.center))
        return dist_to_center > self.radius + 1e-6

    def __repr__(self) -> str:  # pragma: no cover
        return f"Obstacle(center={self.center.tolist()}, radius={self.radius})"