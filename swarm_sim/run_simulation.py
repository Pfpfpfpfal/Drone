#!/usr/bin/env python3
"""Запуск симуляции роя дронов из YAML-конфига.

Пример:
    python run_simulation.py --config configs/scenario_02_with_obstacle.yaml \
        --output results/metrics.csv

После запуска создаётся CSV с метриками и печатается сводка.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from swarm_sim.simulation import build_simulation_from_config
from swarm_sim.utils import load_config


def main() -> None:
    parser = argparse.ArgumentParser(description="Симуляция роя дронов")
    parser.add_argument(
        "--config",
        default=str(Path(__file__).parent / "configs" / "scenario_02_with_obstacle.yaml"),
        help="Путь к YAML-конфигу сценария",
    )
    parser.add_argument(
        "--output",
        default=str(Path(__file__).parent / "results" / "metrics.csv"),
        help="Путь к выходному CSV",
    )
    parser.add_argument(
        "--stop-when-reached",
        action="store_true",
        help="Остановиться, как только все дроны достигли целей",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    sim = build_simulation_from_config(config, args.output)

    print(f"Конфиг: {args.config}")
    print(f"Выходной CSV: {args.output}")
    print("Запуск симуляции...")

    summary = sim.run(stop_when_reached=args.stop_when_reached)
    sim.close()

    print("\n=== Сводка симуляции ===")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()