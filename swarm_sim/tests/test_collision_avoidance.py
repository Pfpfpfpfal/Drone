"""Тест 2: дроны не сталкиваются (min_distance >= safe_distance)."""

from __future__ import annotations

from swarm_sim.drone import Drone
from swarm_sim.swarm import Swarm
from swarm_sim.collision_avoidance import CollisionAvoidance


def _make_swarm(safe_distance=1.5):
    swarm = Swarm(
        goal_position=[20.0, 10.0, 2.0],
        max_velocity=2.0,
        safe_distance=safe_distance,
        k_avoidance=1.5,
    )
    # лидер и ведомые стартуют близко друг к другу
    leader = Drone(1, 0.0, 0.0, 2.0, is_leader=True)
    swarm.add_drone(leader, offset=[0.0, 0.0, 0.0])
    d2 = Drone(2, 0.8, 0.0, 2.0)
    swarm.add_drone(d2, offset=[-2.0, -2.0, 0.0])
    d3 = Drone(3, 0.8, 0.5, 2.0)
    swarm.add_drone(d3, offset=[-2.0, 2.0, 0.0])
    return swarm, safe_distance


def test_min_distance_respects_safe_distance():
    swarm, safe_distance = _make_swarm()
    # разгоняем дроны из стартового «кучного» положения (начальный транзит)
    for _ in range(30):
        swarm.step(0.1)

    min_d = float("inf")
    for _ in range(800):
        swarm.step(0.1)
        min_d = min(min_d, swarm.min_distance())

    # в установившемся движении расстояние не должно проваливаться ниже safe_distance
    assert min_d > safe_distance - 0.05, (
        f"Дроны подошли слишком близко: min_distance = {min_d:.3f}"
    )


def test_collision_avoidance_force_repels():
    ca = CollisionAvoidance(safe_distance=1.5, k_avoidance=1.0)
    a = Drone(1, 0.0, 0.0, 0.0)
    b = Drone(2, 0.5, 0.0, 0.0)
    force = ca.avoidance_force(a, [b])
    # a лежит слева от b, отталкивание толкает a ещё левее (по оси -x)
    assert force[0] < 0
    # сила существует только внутри зоны влияния
    far = Drone(3, 100.0, 0.0, 0.0)
    assert ca.avoidance_force(a, [far])[0] == 0.0