#!/usr/bin/env python3
"""График траекторий роя: траектории дронов, старт, цель, препятствия.

Пример:
    python plot_trajectories.py --input results/metrics.csv \
        --output results/trajectory_plot.png
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.analysis_common import ensure_output_dir, load_metrics  # noqa: E402


def plot_trajectories(csv_path: str | Path, output: str | Path, obstacles=None) -> None:
    df = load_metrics(csv_path)
    out = ensure_output_dir(output)

    fig, ax = plt.subplots(figsize=(10, 8))

    colors = plt.cm.tab10(np.linspace(0, 1, df["drone_id"].nunique()))
    color_map = {d: colors[i] for i, d in enumerate(sorted(df["drone_id"].unique()))}

    for drone_id, group in df.groupby("drone_id"):
        ax.plot(
            group["x"], group["y"],
            color=color_map[drone_id], linewidth=2,
            label=f"Drone {int(float(drone_id))}",
        )
        # точка старта
        ax.scatter(
            group["x"].iloc[0], group["y"].iloc[0],
            color=color_map[drone_id], marker="o", s=80, zorder=5,
        )
        # точка цели
        ax.scatter(
            group["target_x"].iloc[-1], group["target_y"].iloc[-1],
            color=color_map[drone_id], marker="*", s=180, zorder=5,
        )

    # препятствия
    if obstacles:
        for obs in obstacles:
            circle = Circle(
                (obs["center"][0], obs["center"][1]),
                obs["radius"],
                color="red", alpha=0.3,
            )
            ax.add_patch(circle)

    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_title("Траектории роя дронов")
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend(loc="best")
    ax.set_aspect("equal")

    fig.tight_layout()
    fig.savefig(out, dpi=150)
    print(f"Сохранено: {out}")


def main() -> None:
    parser = argparse.ArgumentParser(description="График траекторий роя")
    parser.add_argument("--input", default="results/metrics.csv")
    parser.add_argument("--output", default="results/trajectory_plot.png")
    args = parser.parse_args()
    plot_trajectories(args.input, args.output)


if __name__ == "__main__":
    main()