"""Логирование метрик полёта роя в CSV.

Формат строки совпадает с симулятором:
    time, drone_id, x, y, z, target_x, target_y, target_z,
    formation_error, min_distance
"""

from __future__ import annotations

import csv
from pathlib import Path


class MetricsLogger:
    """Запись метрик в CSV (в ROS 2-узле используется как хранилище)."""

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

    def log(
        self,
        t: float,
        drone_id: int,
        pos,
        target,
        formation_error: float,
        min_distance: float,
    ) -> None:
        """Запись одной строки метрик по одному дрону."""
        self._writer.writerow(
            {
                "time": round(float(t), 4),
                "drone_id": int(drone_id),
                "x": round(float(pos[0]), 4),
                "y": round(float(pos[1]), 4),
                "z": round(float(pos[2]), 4),
                "target_x": round(float(target[0]), 4),
                "target_y": round(float(target[1]), 4),
                "target_z": round(float(target[2]), 4),
                "formation_error": round(float(formation_error), 4),
                "min_distance": round(float(min_distance), 4),
            }
        )

    def close(self) -> None:
        if not self._file.closed:
            self._file.close()