"""Формирование: определяет желаемую позицию каждого дрона относительно лидера.

Перенос логики из swarm_sim/formation_controller.py в ROS 2.
"""

from __future__ import annotations

from typing import Dict, Mapping

import numpy as np
from numpy.typing import ArrayLike


class FormationController:
    """Расчёт целевых позиций ведомых и ошибки формации.

    Конфигурация:
        offsets: словарь {drone_id: [dx, dy, dz]} — сдвиг относительно лидера.
    """

    def __init__(
        self,
        k_formation: float = 0.6,
        offsets: Mapping[int, ArrayLike] | None = None,
    ) -> None:
        self.k_formation = float(k_formation)
        self.offsets: Dict[int, np.ndarray] = {
            int(did): np.asarray(off, dtype=float)
            for did, off in (offsets or {}).items()
        }

    def desired_position(self, leader_pos, drone_id: int) -> np.ndarray:
        """Желаемая позиция дрона drone_id относительно лидера."""
        leader = np.asarray(leader_pos, dtype=float)
        return leader + self.offsets.get(int(drone_id), np.zeros(3))

    def formation_error(self, pos, leader_pos, drone_id: int) -> float:
        """Отклонение дрона от желаемой точки формации."""
        return float(np.linalg.norm(
            np.asarray(pos, dtype=float) - self.desired_position(leader_pos, drone_id)
        ))

    def correction(self, pos, leader_pos, drone_id: int) -> np.ndarray:
        """Управляющий вектор возврата к точке формации."""
        return self.k_formation * (
            self.desired_position(leader_pos, drone_id) - np.asarray(pos, dtype=float)
        )