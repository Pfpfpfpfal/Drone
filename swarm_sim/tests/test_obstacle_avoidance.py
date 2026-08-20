"""Тест 4: препятствие вызывает отклонение траектории (обход).

Траектория не должна проходить сквозь радиус препятствия.
"""

from __future__ import annotations

import numpy as np

from swarm_sim.drone import Drone
from swarm_sim.obstacle import Obstacle
from swarm_sim.swarm import Swarm


def test_trajectory_avoids_obstacle():
    obstacle = Obstacle(center=[10.0, 5.0, 0.0], radius=2.0, influence_radius=4.0)
    swarm = Swarm(
        goal_position=[20.0, 10.0, 2.0],
        max_velocity=2.0,
        sensor_range=6.0,
    )
    leader = Drone(1, 0.0, 0.0, 2.0, is_leader=True)
    swarm.add_drone(leader, offset=[0.0, 0.0, 0.0])
    swarm.add_obstacle(obstacle)

    inside_hits = 0
    for _ in range(600):
        swarm.step(0.1)
        # проверяем 2D-проекцию (z игнорируем): дистанция до центра > радиус
        dist_center = float(np.linalg.norm(leader.position[:2] - obstacle.center[:2]))
        if dist_center <= obstacle.radius + 0.1:
            inside_hits += 1

    assert inside_hits == 0, f"Траектория попала в препятствие {inside_hits} раз"


def test_obstacle_collision_free_distance():
    obs = Obstacle(center=[10.0, 5.0], radius=2.0)
    # отрезок в стороне от круга — свободен
    assert obs.collision_free_distance([0, 0], [20, 0]) is True
    # отрезок, идущий через центр круга — пересекает препятствие
    assert obs.collision_free_distance([0, 5], [20, 5]) is False


def test_repulsion_within_sensor_range():
    from swarm_sim.potential_fields import PotentialFields

    pf = PotentialFields(sensor_range=5.0)
    obs = Obstacle(center=[5.0, 0.0, 0.0], radius=1.0)
    # точка справа от препятствия (dist=1 -> у поверхности) — сильное отталкивание
    pos_in = np.array([6.0, 0.0, 0.0])
    force = pf.repulsion_from_obstacle(pos_in, obs.center, obs.radius, obs.influence_radius)
    assert force[0] > 0  # отталкивание толкает дальше от центра препятствия (+x)

    # точка за пределами sensor_range — сила равна нулю (имитация сенсора)
    pos_far = np.array([20.0, 0.0, 0.0])
    force_far = pf.repulsion_from_obstacle(pos_far, obs.center, obs.radius, obs.influence_radius)
    assert np.allclose(force_far, 0.0)