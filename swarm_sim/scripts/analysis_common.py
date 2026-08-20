"""Общие функции для скриптов анализа и построения графиков."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

METRICS_COLUMNS = [
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


def load_metrics(csv_path: str | Path) -> pd.DataFrame:
    """Загрузка CSV с метриками в DataFrame."""
    return pd.read_csv(csv_path)


def ensure_output_dir(path: str | Path) -> Path:
    """Создание каталога для выходных файлов."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def collect_per_step(df: pd.DataFrame) -> pd.DataFrame:
    """Сводные метрики по каждому временному шагу (по всем дронам)."""
    grouped = df.groupby("time", as_index=False).agg(
        formation_error_mean=("formation_error", "mean"),
        formation_error_max=("formation_error", "max"),
        min_distance=("min_distance", "min"),
    )
    return grouped


def distance_to_goal_row(df: pd.DataFrame) -> pd.DataFrame:
    """Дистанция каждого дрона до своей цели."""
    df = df.copy()
    df["distance_to_goal"] = (
        (df["x"] - df["target_x"]) ** 2
        + (df["y"] - df["target_y"]) ** 2
        + (df["z"] - df["target_z"]) ** 2
    ) ** 0.5
    return df