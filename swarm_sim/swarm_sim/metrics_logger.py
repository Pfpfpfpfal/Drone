"""Логирование метрик симуляции в CSV.

Формат строки (из PLAN.md):
    time, drone_id, x, y, z, target_x, target_y, target_z,
    formation_error, min_distance
"""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

from .drone import Drone
from .formation_controller import FormationController
from .collision_avoidance import CollisionAvoidance


class MetricsLogger:
    """Сбор и запись метрик в CSV.

    Метод log_step вызывается на каждом шаге симуляции и собирает данные
    по всем дронам. Файл записывается постепенно (построчно), что позволяет
    анализировать результаты сразу после симуляции.
    """

    HEADER = [
        "time",
        "drone_id",
        "x",
        "y",
        "z",
        "target_x",
        "target_y",
        "target_z",
        "formation_error",
        "min_distance",
    ]

    def __init__(self, filepath: str | Path) -> None:
        self.filepath = Path(filepath)
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        self._file = open(self.filepath, "w", newline="", encoding="utf-8")
        self._writer = csv.DictWriter(self._file, fieldnames=self.HEADER)
        self._writer.writeheader()
        self._rows_written = 0

    def log_step(
        self,
        t: float,
        drones: list,
        formation_controller: FormationController,
        leader: Drone,
        collision_avoidance: CollisionAvoidance,
    ) -> None:
        """Запись одного временного шага по всем дронам."""
        min_distance = collision_avoidance.min_distance(drones)
        for drone in drones:
            target = (
                drone.target_position
                if drone.target_position is not None
                else np.zeros(3)
            )
            row = {
                "time": round(t, 4),
                "drone_id": drone.id,
                "x": round(drone.x, 4),
                "y": round(drone.y, 4),
                "z": round(drone.z, 4),
                "target_x": round(float(target[0]), 4),
                "target_y": round(float(target[1]), 4),
                "target_z": round(float(target[2]), 4),
                "formation_error": round(
                    formation_controller.formation_error(drone, leader), 4
                ),
                "min_distance": round(min_distance, 4),
            }
            self._writer.writerow(row)
            self._rows_written += 1

    def close(self) -> None:
        """Закрытие файла."""
        if not self._file.closed:
            self._file.close()

    @property
    def count(self) -> int:
        return self._rows_written

    def __del__(self) -> None:  # pragma: no cover
        try:
            self.close()
        except Exception:
            pass