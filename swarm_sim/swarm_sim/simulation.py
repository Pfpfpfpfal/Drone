"""Главный цикл симуляции роя дронов."""

from __future__ import annotations

from typing import Optional

import numpy as np

from .swarm import Swarm
from .drone import Drone
from .obstacle import Obstacle
from .metrics_logger import MetricsLogger
from .utils import parse_position


class Simulation:
    """Запускает шаги симуляции и собирает метрики.

    Атрибуты:
        swarm: объект Swarm с настроенными дронами и препятствиями.
        dt: шаг интегрирования.
        duration: длительность симуляции (сек).
        logger: опциональный MetricsLogger для записи CSV.
    """

    def __init__(
        self,
        swarm: Swarm,
        dt: float = 0.1,
        duration: float = 60.0,
        logger: Optional[MetricsLogger] = None,
    ) -> None:
        self.swarm = swarm
        self.dt = float(dt)
        self.duration = float(duration)
        self.logger = logger
        self.t = 0.0

    def run(self, stop_when_reached: bool = False) -> dict:
        """Запуск симуляции.

        Возвращает сводку метрик (dict). Если stop_when_reached=True,
        цикл прерывается, как только все дроны достигли целей.
        """
        n_steps = int(self.duration / self.dt)
        for _ in range(n_steps):
            self.swarm.step(self.dt)
            self.t += self.dt

            if self.logger is not None:
                assert self.swarm.leader is not None
                self.logger.log_step(
                    self.t,
                    self.swarm.drones,
                    self.swarm.formation_controller,
                    self.swarm.leader,
                    self.swarm.collision_avoidance,
                )

            if stop_when_reached and self.swarm.all_reached_goal():
                break

        return self.summary()

    def summary(self) -> dict:
        """Сводные метрики симуляции."""
        sw = self.swarm
        return {
            "time": round(self.t, 3),
            "drones_count": len(sw.drones),
            "obstacles_count": len(sw.obstacles),
            "final_formation_error": round(sw.formation_error(), 4),
            "min_distance_overall": round(sw.min_distance(), 4),
            "all_reached_goal": sw.all_reached_goal(),
            "goal_position": list(sw.goal_position),
        }

    def close(self) -> None:
        """Закрытие логгера."""
        if self.logger is not None:
            self.logger.close()


# ----------------------------------------------------------------------
# Удобный конструктор из YAML-конфига
# ----------------------------------------------------------------------
def build_swarm_from_config(config: dict) -> Swarm:
    """Создание Swarm из конфига сценария (см. configs/scenario_*.yaml)."""
    swarm_cfg = config.get("swarm", {})
    leader_cfg = config.get("leader", {})
    followers_cfg = config.get("followers", [])
    controller_cfg = config.get("controller", {})
    obstacles_cfg = config.get("obstacles", [])

    goal = parse_position(leader_cfg.get("goal_position", [0.0, 0.0, 0.0]))

    swarm = Swarm(
        goal_position=goal,
        k_goal=controller_cfg.get("k_goal", 0.8),
        k_formation=controller_cfg.get("k_formation", 0.6),
        k_avoidance=controller_cfg.get("k_avoidance", 1.2),
        max_velocity=controller_cfg.get("max_velocity", 2.0),
        safe_distance=swarm_cfg.get("safe_distance", 1.5),
        sensor_range=controller_cfg.get("sensor_range", 5.0),
    )

    # лидер
    leader_start = parse_position(leader_cfg.get("start_position", [0.0, 0.0, 0.0]))
    leader = Drone(1, *leader_start, is_leader=True)
    swarm.add_drone(leader, offset=[0.0, 0.0, 0.0])

    # ведомые
    for f in followers_cfg:
        fid = f.get("id", 2)
        offset = f.get("offset", [0.0, 0.0, 0.0])
        start = f.get("start_position")
        if start is None:
            # по умолчанию стартуем в желаемой точке формации
            start = (
                np.asarray(parse_position(leader_start), dtype=float)
                + np.asarray(parse_position(offset), dtype=float)
            )
        start = parse_position(start)
        drone = Drone(fid, *start)
        swarm.add_drone(drone, offset=offset)

    # препятствия
    for obs in obstacles_cfg:
        swarm.add_obstacle(
            Obstacle(
                center=obs.get("center", [0.0, 0.0, 0.0]),
                radius=obs.get("radius", 1.0),
                influence_radius=obs.get("influence_radius"),
            )
        )

    return swarm


def build_simulation_from_config(config: dict, csv_path: str) -> Simulation:
    """Создание Simulation из YAML-конфига с логгером в csv_path."""
    sim_cfg = config.get("simulation", {})
    dt = sim_cfg.get("dt", 0.1)
    duration = sim_cfg.get("duration", 60.0)

    swarm = build_swarm_from_config(config)
    logger = MetricsLogger(csv_path)
    return Simulation(swarm, dt=dt, duration=duration, logger=logger)