#!/usr/bin/env python3
"""График минимального расстояния между дронами во времени.

Пример:
    python plot_min_distance.py --input results/metrics.csv \
        --output results/min_distance.png
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.analysis_common import ensure_output_dir, load_metrics  # noqa: E402


def plot_min_distance(csv_path: str | Path, output: str | Path, safe_distance: float = 1.5) -> None:
    df = load_metrics(csv_path)
    out = ensure_output_dir(output)

    per_step = df.groupby("time")["min_distance"].min().reset_index()

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(per_step["time"], per_step["min_distance"], label="мин. расстояние", linewidth=2)
    ax.axhline(safe_distance, color="red", linestyle="--", label=f"safe_distance={safe_distance}")

    ax.set_xlabel("время, с")
    ax.set_ylabel("мин. расстояние между дронами")
    ax.set_title("Минимальное расстояние между дронами во времени")
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    print(f"Сохранено: {out}")


def main() -> None:
    parser = argparse.ArgumentParser(description="График минимального расстояния")
    parser.add_argument("--input", default="results/metrics.csv")
    parser.add_argument("--output", default="results/min_distance.png")
    parser.add_argument("--safe-distance", type=float, default=1.5)
    args = parser.parse_args()
    plot_min_distance(args.input, args.output, args.safe_distance)


if __name__ == "__main__":
    main()