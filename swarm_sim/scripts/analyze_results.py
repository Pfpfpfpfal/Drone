#!/usr/bin/env python3
"""Полный анализ результатов: строит все графики и сводную таблицу.

Пример:
    python analyze_results.py --input results/metrics.csv --outdir results/
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.plot_trajectories import plot_trajectories  # noqa: E402
from scripts.plot_formation_error import plot_formation_error  # noqa: E402
from scripts.plot_min_distance import plot_min_distance  # noqa: E402
from scripts.plot_distance_to_goal import plot_distance_to_goal  # noqa: E402
from scripts.generate_report_tables import generate_summary  # noqa: E402


def analyze(input_csv: str | Path, outdir: str | Path, safe_distance: float = 1.5) -> None:
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    plot_trajectories(input_csv, outdir / "trajectory_plot.png")
    plot_formation_error(input_csv, outdir / "formation_error.png")
    plot_min_distance(input_csv, outdir / "min_distance.png", safe_distance=safe_distance)
    plot_distance_to_goal(input_csv, outdir / "distance_to_goal.png")
    generate_summary(input_csv, outdir / "summary_metrics.csv")


def main() -> None:
    parser = argparse.ArgumentParser(description="Полный анализ результатов")
    parser.add_argument("--input", default="results/metrics.csv")
    parser.add_argument("--outdir", default="results/")
    parser.add_argument("--safe-distance", type=float, default=1.5)
    args = parser.parse_args()
    analyze(args.input, args.outdir, args.safe_distance)


if __name__ == "__main__":
    main()