#!/usr/bin/env python3
"""Генерация сводных таблиц (summary_metrics.csv) из CSV-метрик симуляции.

Пример:
    python generate_report_tables.py --input results/metrics.csv \
        --output results/summary_metrics.csv
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.analysis_common import ensure_output_dir, load_metrics  # noqa: E402


def generate_summary(csv_path: str | Path, output: str | Path) -> pd.DataFrame:
    df = load_metrics(csv_path)
    out = ensure_output_dir(output)

    rows = []
    for drone_id, group in df.groupby("drone_id"):
        initial_dist = (
            (group["x"].iloc[0] - group["target_x"].iloc[0]) ** 2
            + (group["y"].iloc[0] - group["target_y"].iloc[0]) ** 2
            + (group["z"].iloc[0] - group["target_z"].iloc[0]) ** 2
        ) ** 0.5
        final_dist = (
            (group["x"].iloc[-1] - group["target_x"].iloc[-1]) ** 2
            + (group["y"].iloc[-1] - group["target_y"].iloc[-1]) ** 2
            + (group["z"].iloc[-1] - group["target_z"].iloc[-1]) ** 2
        ) ** 0.5
        rows.append(
            {
                "drone_id": int(float(drone_id)),
                "initial_distance_to_goal": round(initial_dist, 4),
                "final_distance_to_goal": round(final_dist, 4),
                "mean_formation_error": round(group["formation_error"].mean(), 4),
                "max_formation_error": round(group["formation_error"].max(), 4),
                "min_distance_overall": round(group["min_distance"].min(), 4),
            }
        )

    summary = pd.DataFrame(rows)
    summary.to_csv(out, index=False)
    print(f"Сохранено: {out}")
    print(summary.to_string(index=False))
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Сводные таблицы метрик")
    parser.add_argument("--input", default="results/metrics.csv")
    parser.add_argument("--output", default="results/summary_metrics.csv")
    args = parser.parse_args()
    generate_summary(args.input, args.output)


if __name__ == "__main__":
    main()