"""Общие фикстуры для тестов."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# добавляем корень пакета swarm_sim в путь импорта
SWARM_SIM_ROOT = Path(__file__).resolve().parents[1]
if str(SWARM_SIM_ROOT) not in sys.path:
    sys.path.insert(0, str(SWARM_SIM_ROOT))


@pytest.fixture
def scenario01_config_path() -> Path:
    return SWARM_SIM_ROOT / "configs" / "scenario_01_no_obstacles.yaml"


@pytest.fixture
def scenario02_config_path() -> Path:
    return SWARM_SIM_ROOT / "configs" / "scenario_02_with_obstacle.yaml"