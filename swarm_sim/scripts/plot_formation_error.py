#!/usr/bin/env python3
"""График ошибки формации во времени.

Пример:
    python plot_formation_error.py --input results/metrics.csv \
        --output results/formation_error.png
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.analysis_common import ensure_output_dir, load_metrics  # noqa: E402


def plot_formation_error(csv_path: str | Path, output: str | Path) -> None:
    df = load_metrics(csv_path)
    out = ensure_output_dir(output)

    per_step = df.groupby("time").agg(
        mean=("formation_error", "mean"),
        max=("formation_error", "max"),
    ).reset_index()

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(per_step["time"], per_step["mean"], label="средняя ошибка", linewidth=2)
    ax.plot(per_step["time"], per_step["max"], label="макс. ошибка", linestyle="--", alpha=0.7)

    ax.set_xlabel("время, с")
    ax.set_ylabel("ошибка формации")
    ax.set_title("Ошибка формации во времени")
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    print(f"Сохранено: {out}")


def main() -> None:
    parser = argparse.ArgumentParser(description="График ошибки формации")
    parser.add_argument("--input", default="results/metrics.csv")
    parser.add_argument("--output", default="results/formation_error.png")
    args = parser.parse_args()
    plot_formation_error(args.input, args.output)


if __name__ == "__main__":
    main()