"""Модель отдельного дрона как точки в 3D-пространстве."""

from __future__ import annotations

from typing import Optional, Sequence

import numpy as np


class Drone:
    """Дрон — точка с координатами, скоростью и целевой позицией.

    Атрибуты:
        id: уникальный идентификатор дрона.
        position: numpy-вектор [x, y, z].
        velocity: numpy-вектор скорости [vx, vy, vz].
        target_position: целевая точка (None — лететь в (0,0,0) не обязательно).
        formation_offset: сдвиг относительно лидера для ведомых дронов.
        is_leader: признак лидера формации.
        reach_epsilon: порог считания точки достигнутой.
    """

    def __init__(
        self,
        drone_id: int,
        x: float = 0.0,
        y: float = 0.0,
        z: float = 0.0,
        vx: float = 0.0,
        vy: float = 0.0,
        vz: float = 0.0,
        is_leader: bool = False,
    ) -> None:
        self.id = int(drone_id)
        self.position = np.array([x, y, z], dtype=float)
        self.velocity = np.array([vx, vy, vz], dtype=float)
        self.target_position: Optional[np.ndarray] = None
        self.formation_offset = np.zeros(3)
        self.is_leader = is_leader
        self.reach_epsilon = 0.2

    # ------------------------------------------------------------------
    # Доступ к координатам
    # ------------------------------------------------------------------
    @property
    def pos(self) -> np.ndarray:
        return self.position

    @property
    def vel(self) -> np.ndarray:
        return self.velocity

    @property
    def x(self) -> float:
        return float(self.position[0])

    @property
    def y(self) -> float:
        return float(self.position[1])

    @property
    def z(self) -> float:
        return float(self.position[2])

    def set_target(self, target: Sequence[float]) -> None:
        """Установка целевой позиции."""
        self.target_position = np.asarray(target, dtype=float)

    def set_formation_offset(self, offset: Sequence[float]) -> None:
        """Установка офсета формации относительно лидера."""
        self.formation_offset = np.asarray(offset, dtype=float)

    def set_state(
        self,
        position: Sequence[float],
        velocity: Optional[Sequence[float]] = None,
    ) -> None:
        """Прямая установка состояния (для тестов и телепортации)."""
        self.position = np.asarray(position, dtype=float)
        if velocity is not None:
            self.velocity = np.asarray(velocity, dtype=float)

    def distance_to_goal(self) -> float:
        """Текущее расстояние до цели (inf, если цель не задана)."""
        if self.target_position is None:
            return float("inf")
        return float(np.linalg.norm(self.target_position - self.position))

    def has_reached_goal(self) -> bool:
        """Достиг ли дрон целевой точки."""
        if self.target_position is None:
            return True
        return self.distance_to_goal() <= self.reach_epsilon

    def step(self, dt: float) -> None:
        """Интеграция движения: новая позиция = старая + скорость * dt."""
        self.position = self.position + self.velocity * dt

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"Drone(id={self.id}, pos=({self.x:.2f}, {self.y:.2f}, {self.z:.2f}), "
            f"vel=({self.velocity[0]:.2f}, {self.velocity[1]:.2f}, {self.velocity[2]:.2f}))"
        )