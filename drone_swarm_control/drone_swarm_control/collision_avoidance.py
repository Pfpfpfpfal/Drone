"""Избегание столкновений: отталкивание от соседей.

Перенос логики из swarm_sim/collision_avoidance.py в ROS 2.
"""

from __future__ import annotations

from typing import Dict

import numpy as np

from .utils import safe_normalize


class CollisionAvoidance:
    """Отталкивание соседних дронов друг от друга."""

    def __init__(
        self,
        safe_distance: float = 1.5,
        k_avoidance: float = 1.2,
        influence: float | None = None,
    ) -> None:
        self.safe_distance = float(safe_distance)
        self.k_avoidance = float(k_avoidance)
        self.influence = float(influence) if influence else self.safe_distance * 2.0

    def avoidance_force(self, pos, others: Dict[int, np.ndarray], self_id: int) -> np.ndarray:
        """Суммарный отталкивающий вектор от всех соседей."""
        force = np.zeros(3)
        pos = np.asarray(pos, dtype=float)
        for other_id, other_pos in others.items():
            if other_id == self_id:
                continue
            delta = pos - np.asarray(other_pos, dtype=float)
            dist = float(np.linalg.norm(delta))
            if dist < 1e-9:
                delta = np.array([1.0, 0.0, 0.0])
                dist = 1e-9
            if dist >= self.influence:
                continue
            penetration = max(self.influence - dist, 0.0)
            strength = self.k_avoidance * penetration / self.influence
            force += strength * safe_normalize(delta)
        return force

    def min_distance(self, positions: Dict[int, np.ndarray]) -> float:
        """Минимальное попарное расстояние между дронами."""
        items = list(positions.values())
        if len(items) < 2:
            return float("inf")
        return min(
            float(np.linalg.norm(a - b))
            for i, a in enumerate(items)
            for b in items[i + 1:]
        )