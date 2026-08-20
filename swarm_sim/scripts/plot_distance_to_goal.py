#!/usr/bin/env python3
"""График дистанции каждого дрона до его цели во времени.

Пример:
    python plot_distance_to_goal.py --input results/metrics.csv \
        --output results/distance_to_goal.png
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.analysis_common import ensure_output_dir, load_metrics  # noqa: E402


def plot_distance_to_goal(csv_path: str | Path, output: str | Path) -> None:
    df = load_metrics(csv_path)
    df = df.copy()
    df["distance_to_goal"] = (
        (df["x"] - df["target_x"]) ** 2
        + (df["y"] - df["target_y"]) ** 2
        + (df["z"] - df["target_z"]) ** 2
    ) ** 0.5
    out = ensure_output_dir(output)

    fig, ax = plt.subplots(figsize=(10, 6))
    for drone_id, group in df.groupby("drone_id"):
        ax.plot(
            group["time"], group["distance_to_goal"],
            linewidth=2, label=f"Drone {int(float(drone_id))}",
        )

    ax.set_xlabel("время, с")
    ax.set_ylabel("дистанция до цели")
    ax.set_title("Дистанция дронов до цели во времени")
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    print(f"Сохранено: {out}")


def main() -> None:
    parser = argparse.ArgumentParser(description="График дистанции до цели")
    parser.add_argument("--input", default="results/metrics.csv")
    parser.add_argument("--output", default="results/distance_to_goal.png")
    args = parser.parse_args()
    plot_distance_to_goal(args.input, args.output)


if __name__ == "__main__":
    main()