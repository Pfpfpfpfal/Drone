"""Управление формацией (leader-follower).

Определяет желаемую позицию каждого дрона относительно лидера,
а также вычисляет ошибку формации.
"""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
from numpy.typing import ArrayLike

from .drone import Drone


class FormationController:
    """Расчёт целевых точек ведомых дронов относительно лидера.

    Атрибуты:
        k_formation: коэффициент возврата к точке формации.
        max_formation_error: порог ошибки, при достижении которого формация
            считается удержанной (используется в тестах).
    """

    def __init__(self, k_formation: float = 0.6, max_formation_error: float = 0.5) -> None:
        self.k_formation = float(k_formation)
        self.max_formation_error = float(max_formation_error)

    def desired_position(self, leader_pos: ArrayLike, offset: ArrayLike) -> np.ndarray:
        """Желаемая позиция дрона с офсетом offset относительно лидера."""
        return np.asarray(leader_pos, dtype=float) + np.asarray(offset, dtype=float)

    def formation_error(self, drone: Drone, leader: Drone) -> float:
        """Ошибка формации: отклонение дрона от желаемой точки.

        Если дрон — лидер, ошибка равна 0.
        """
        if drone.is_leader or drone.id == leader.id:
            return 0.0
        desired = self.desired_position(leader.position, drone.formation_offset)
        return float(np.linalg.norm(desired - drone.position))

    def formation_correction(self, drone: Drone, leader: Drone) -> np.ndarray:
        """Вектор возврата к точке формации (для ведомых)."""
        if drone.is_leader or drone.id == leader.id:
            return np.zeros(3)
        desired = self.desired_position(leader.position, drone.formation_offset)
        error_vec = desired - drone.position
        return self.k_formation * error_vec

    def swarm_formation_error(self, drones: Sequence[Drone], leader: Drone) -> float:
        """Средняя ошибка формации по всем ведомым дронам."""
        followers = [d for d in drones if d.id != leader.id]
        if not followers:
            return 0.0
        total = sum(self.formation_error(d, leader) for d in followers)
        return total / len(followers)