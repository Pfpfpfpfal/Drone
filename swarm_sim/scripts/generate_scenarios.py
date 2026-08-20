#!/usr/bin/env python3
"""Генератор YAML-конфигов сценариев эксперимента.

Создаёт типовые сценарии роя дронов, которые затем используются
и Python-симулятором, и ROS 2-пакетом.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def make_scenario(
    name: str,
    drones_count: int,
    goal,
    obstacles=None,
    followers=None,
    controller=None,
    simulation=None,
    safe_distance: float = 1.5,
    formation_type: str = "v_shape",
    leader_start=None,
):
    """Сборка словаря-конфига сценария."""
    leader_start = leader_start or [0.0, 0.0, 2.0]
    if followers is None:
        followers = _default_followers(drones_count)

    return {
        "name": name,
        "swarm": {
            "drones_count": drones_count,
            "safe_distance": safe_distance,
            "formation_type": formation_type,
        },
        "leader": {
            "start_position": leader_start,
            "goal_position": list(goal),
        },
        "followers": followers,
        "obstacles": obstacles or [],
        "controller": controller or {
            "k_goal": 0.8,
            "k_formation": 0.6,
            "k_avoidance": 1.2,
            "max_velocity": 2.0,
            "sensor_range": 5.0,
        },
        "simulation": simulation or {
            "dt": 0.1,
            "duration": 60.0,
        },
    }


def _default_followers(drones_count: int) -> list:
    """V-формация: offsets симметрично вокруг лидера."""
    followers = []
    idx = 2
    level = 1
    while idx <= drones_count:
        followers.append({"id": idx, "offset": [-2.0 * level, -2.0 * level, 0.0]})
        idx += 1
        if idx <= drones_count:
            followers.append({"id": idx, "offset": [-2.0 * level, 2.0 * level, 0.0]})
            idx += 1
        level += 1
    return followers


def build_all() -> dict:
    """Возвращает словарь всех стандартных сценариев."""
    obstacle = [{"center": [10.0, 5.0, 0.0], "radius": 2.0, "influence_radius": 4.0}]

    return {
        "scenario_01_no_obstacles.yaml": make_scenario(
            "no_obstacles", 3, [20.0, 10.0, 2.0], obstacles=[]
        ),
        "scenario_02_with_obstacle.yaml": make_scenario(
            "with_obstacle", 3, [20.0, 10.0, 2.0], obstacles=obstacle
        ),
        "scenario_03_five_drones.yaml": make_scenario(
            "five_drones", 5, [20.0, 10.0, 2.0], obstacles=obstacle
        ),
        "scenario_04_crossing_paths.yaml": make_scenario(
            "crossing_paths",
            5,
            [20.0, 20.0, 2.0],
            obstacles=[{"center": [10.0, 10.0, 0.0], "radius": 2.5, "influence_radius": 5.0}],
            safe_distance=1.5,
            formation_type="crossing",
            controller={
                "k_goal": 0.8,
                "k_formation": 0.5,
                "k_avoidance": 1.2,
                "max_velocity": 2.0,
                "sensor_range": 6.0,
            },
            simulation={"dt": 0.1, "duration": 120.0},
            followers=[
                {"id": 2, "offset": [-2.0, -2.0, 0.0], "start_position": [0.0, 10.0, 2.0]},
                {"id": 3, "offset": [-2.0, 2.0, 0.0], "start_position": [10.0, 0.0, 2.0]},
                # подгруппы стартуют с противоположных сторон и пересекаются;
                # офсеты уникальны (V-формация на 5 дронов)
                {"id": 4, "offset": [-4.0, -4.0, 0.0], "start_position": [20.0, 0.0, 2.0]},
                {"id": 5, "offset": [-4.0, 4.0, 0.0], "start_position": [0.0, 20.0, 2.0]},
            ],
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Генератор сценариев")
    parser.add_argument(
        "--outdir", default=str(Path(__file__).resolve().parents[1] / "configs")
    )
    args = parser.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    scenarios = build_all()
    for filename, config in scenarios.items():
        path = outdir / filename
        with open(path, "w", encoding="utf-8") as f:
            yaml.safe_dump(config, f, allow_unicode=True, sort_keys=False)
        print(f"Сгенерирован: {path}")


if __name__ == "__main__":
    main()