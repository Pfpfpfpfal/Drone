"""Тест 3: формация сохраняется (formation_error < порога)."""

from __future__ import annotations

from swarm_sim.drone import Drone
from swarm_sim.swarm import Swarm
from swarm_sim.formation_controller import FormationController


def _make_swarm(k_formation=0.6):
    swarm = Swarm(
        goal_position=[20.0, 10.0, 2.0],
        k_formation=k_formation,
        max_velocity=2.0,
    )
    leader = Drone(1, 0.0, 0.0, 2.0, is_leader=True)
    swarm.add_drone(leader, offset=[0.0, 0.0, 0.0])
    # ведомые стартуют в точках формации, чтобы проверить удержание в движении
    d2 = Drone(2, -2.0, -2.0, 2.0)
    swarm.add_drone(d2, offset=[-2.0, -2.0, 0.0])
    d3 = Drone(3, -2.0, 2.0, 2.0)
    swarm.add_drone(d3, offset=[-2.0, 2.0, 0.0])
    return swarm


def test_formation_error_below_threshold():
    swarm = _make_swarm()
    # даём рою время собраться в формацию
    for _ in range(300):
        swarm.step(0.1)

    error = swarm.formation_error()
    assert error < 0.7, f"Ошибка формации слишком велика: {error:.3f}"


def test_formation_controller_desired_position():
    fc = FormationController(k_formation=0.6)
    desired = fc.desired_position([10.0, 5.0, 2.0], [-2.0, -2.0, 0.0])
    assert abs(desired[0] - 8.0) < 1e-9
    assert abs(desired[1] - 3.0) < 1e-9


def test_leader_formation_error_is_zero():
    fc = FormationController()
    leader = Drone(1, 0.0, 0.0, 0.0, is_leader=True)
    assert fc.formation_error(leader, leader) == 0.0