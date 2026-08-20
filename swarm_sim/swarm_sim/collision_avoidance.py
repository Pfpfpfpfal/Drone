"""Избегание столкновений между дронами (отталкивание от соседей).

Если расстояние между дронами меньше safe_distance — добавляется
отталкивающий вектор.
"""

from __future__ import annotations

from typing import Sequence

import numpy as np

from .drone import Drone
from .utils import safe_normalize


class CollisionAvoidance:
    """Отталкивание соседних дронов друг от друга.

    Атрибуты:
        safe_distance: минимально допустимое расстояние между дронами.
        k_avoidance: коэффициент силы отталкивания.
        influence: радиус, в пределах которого включается отталкивание
            (обычно несколько больше safe_distance).
    """

    def __init__(
        self,
        safe_distance: float = 1.5,
        k_avoidance: float = 1.2,
        influence: float | None = None,
    ) -> None:
        self.safe_distance = float(safe_distance)
        self.k_avoidance = float(k_avoidance)
        self.influence = float(influence) if influence else self.safe_distance * 2.0

    def avoidance_force(
        self, drone: Drone, others: Sequence[Drone]
    ) -> np.ndarray:
        """Суммарный отталкивающий вектор от всех соседей."""
        force = np.zeros(3)
        for other in others:
            if other.id == drone.id:
                continue
            delta = drone.position - other.position
            dist = float(np.linalg.norm(delta))
            if dist < 1e-9:
                # дроны совпали — отталкиваем в случайном направлении по оси x
                delta = np.array([1.0, 0.0, 0.0])
                dist = 1e-9

            if dist >= self.influence:
                continue

            # сила максимальна при dist <= safe_distance и спадает к influence
            penetration = max(self.influence - dist, 0.0)
            strength = self.k_avoidance * penetration / self.influence
            force += strength * safe_normalize(delta)
        return force

    def min_distance(self, drones: Sequence[Drone]) -> float:
        """Минимальное попарное расстояние между всеми дронами."""
        if len(drones) < 2:
            return float("inf")
        min_d = float("inf")
        for i, a in enumerate(drones):
            for b in drones[i + 1:]:
                d = float(np.linalg.norm(a.position - b.position))
                if d < min_d:
                    min_d = d
        return min_d

    def collisions_exist(self, drones: Sequence[Drone]) -> bool:
        """Нарушено ли безопасное расстояние хотя бы для одной пары."""
        for i, a in enumerate(drones):
            for b in drones[i + 1:]:
                if float(np.linalg.norm(a.position - b.position)) < self.safe_distance:
                    return True
        return False