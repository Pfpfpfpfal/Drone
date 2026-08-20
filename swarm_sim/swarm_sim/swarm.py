"""Совокупность дронов: leader-follower, формация, избегание столкновений."""

from __future__ import annotations

from typing import List, Optional, Sequence

import numpy as np

from .drone import Drone
from .obstacle import Obstacle
from .formation_controller import FormationController
from .collision_avoidance import CollisionAvoidance
from .potential_fields import PotentialFields
from .utils import limit_speed


class Swarm:
    """Управляемый рой дронов.

    Суммарный управляющий вектор скорости для каждого дрона:
        v = k_goal     * направление_к_цели
          + k_formation* возврат_к_формации     (для ведомых)
          + k_avoidance* отталкивание_от_соседей
          + APF          обход_препятствий
    затем ограничивается по max_velocity.
    """

    def __init__(
        self,
        goal_position: Sequence[float],
        k_goal: float = 0.8,
        k_formation: float = 0.6,
        k_avoidance: float = 1.2,
        max_velocity: float = 2.0,
        safe_distance: float = 1.5,
        sensor_range: float = 5.0,
    ) -> None:
        self.goal_position = np.asarray(goal_position, dtype=float)
        self.k_goal = float(k_goal)
        self.max_velocity = float(max_velocity)

        self.drones: List[Drone] = []
        self.obstacles: List[Obstacle] = []
        self.leader: Optional[Drone] = None

        self.formation_controller = FormationController(k_formation=k_formation)
        self.collision_avoidance = CollisionAvoidance(
            safe_distance=safe_distance, k_avoidance=k_avoidance
        )
        self.potential_fields = PotentialFields(
            k_goal=k_goal, k_obstacle=1.5, sensor_range=sensor_range
        )

    # ------------------------------------------------------------------
    # Настройка роя
    # ------------------------------------------------------------------
    def add_drone(
        self,
        drone: Drone,
        offset: Optional[Sequence[float]] = None,
        set_goal: bool = True,
    ) -> Drone:
        """Добавление дрона. Первый добавленный становится лидером."""
        self.drones.append(drone)
        if offset is not None:
            drone.set_formation_offset(offset)

        if self.leader is None:
            self.leader = drone
            drone.is_leader = True
        if set_goal:
            drone.set_target(self.goal_position)
        return drone

    def add_obstacle(self, obstacle: Obstacle) -> None:
        """Добавление препятствия."""
        self.obstacles.append(obstacle)

    # ------------------------------------------------------------------
    # Управление
    # ------------------------------------------------------------------
    def desired_velocity(self, drone: Drone) -> np.ndarray:
        """Управляющая скорость одного дрона.

        Лидер летит к цели. Ведомые следуют за лидером, удерживая свою точку
        формации (leader.position + offset), — классический leader-follower.
        """
        assert self.leader is not None, "Рой не инициализирован (нет лидера)"

        # 1) стремление к цели:
        #    лидер -> абсолютная цель; ведомый -> точка формации за лидером
        if drone.is_leader or drone.id == self.leader.id:
            target = (
                drone.target_position
                if drone.target_position is not None
                else self.goal_position
            )
        else:
            target = self.leader.position + drone.formation_offset

        v_goal = self.potential_fields.attraction(drone.position, target)
        # насыщаем притяжение, чтобы оно не заглушало отталкивание от препятствий
        v_goal = limit_speed(v_goal, self.max_velocity)
        # подавляем притяжение в зоне влияния препятствий (обход по дуге)
        v_goal *= self.potential_fields.attraction_scale(drone.position, self.obstacles)

        # 2) возврат к формации (для ведомых) — усиливает удержание формации
        v_formation = self.formation_controller.formation_correction(drone, self.leader)

        # 3) отталкивание от соседей
        v_avoidance = self.collision_avoidance.avoidance_force(drone, self.drones)

        # 4) обход препятствий (только repulsion-часть APF)
        v_obstacle = np.zeros(3)
        for obs in self.obstacles:
            v_obstacle += self.potential_fields.repulsion_from_obstacle(
                drone.position, obs.center, obs.radius, obs.influence_radius
            )

        v = v_goal + v_formation + v_avoidance + v_obstacle
        return v

    def compute_commands(self) -> None:
        """Расчёт управляющих скоростей всех дронов."""
        for drone in self.drones:
            drone.velocity = self.desired_velocity(drone)
            n = float(np.linalg.norm(drone.velocity))
            if n > self.max_velocity and n > 0.0:
                drone.velocity *= self.max_velocity / n

    def step(self, dt: float) -> None:
        """Один шаг симуляции: расчёт команд и интегрирование движения."""
        self.compute_commands()
        for drone in self.drones:
            drone.step(dt)

    # ------------------------------------------------------------------
    # Метрики
    # ------------------------------------------------------------------
    def formation_error(self) -> float:
        """Средняя ошибка формации по всем ведомым."""
        if self.leader is None:
            return 0.0
        return self.formation_controller.swarm_formation_error(
            self.drones, self.leader
        )

    def min_distance(self) -> float:
        """Минимальное расстояние между дронами."""
        return self.collision_avoidance.min_distance(self.drones)

    def all_reached_goal(self, formation_threshold: float = 0.6) -> bool:
        """Достигнута ли цель миссии.

        Миссия считается выполненной, когда лидер достиг целевой точки,
        а ошибка формации всех ведомых мала (рой собрался у цели).
        """
        if self.leader is None:
            return False
        return self.leader.has_reached_goal() and self.formation_error() <= formation_threshold