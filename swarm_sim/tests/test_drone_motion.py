"""Тест 1: дрон движется к цели (дистанция уменьшается после N шагов)."""

from __future__ import annotations

from swarm_sim.drone import Drone
from swarm_sim.swarm import Swarm


def _make_single_drone(goal=(10.0, 10.0, 2.0), start=(0.0, 0.0, 2.0)):
    swarm = Swarm(goal_position=goal, max_velocity=2.0)
    drone = Drone(1, *start, is_leader=True)
    swarm.add_drone(drone)
    return swarm, drone


def test_drone_distance_decreases():
    swarm, drone = _make_single_drone()
    initial = drone.distance_to_goal()

    for _ in range(100):
        swarm.step(0.1)

    final = drone.distance_to_goal()
    assert final < initial, f"Дистанция не уменьшилась: {initial:.3f} -> {final:.3f}"


def test_drone_reaches_goal():
    swarm, drone = _make_single_drone(goal=(5.0, 5.0, 2.0))
    for _ in range(600):
        swarm.step(0.1)
    assert drone.distance_to_goal() < 0.5


def test_motion_equation():
    """Проверка формулы pos_new = pos_old + vel * dt."""
    drone = Drone(1, 0.0, 0.0, 0.0, vx=1.0, vy=2.0, vz=0.0)
    drone.step(dt=0.5)
    assert abs(drone.x - 0.5) < 1e-9
    assert abs(drone.y - 1.0) < 1e-9