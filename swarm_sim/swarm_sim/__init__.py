"""Пакет чистого Python-симулятора роя дронов (без Gazebo).

Модель движения как точек:
    новая позиция = старая позиция + скорость * dt

Основные компоненты:
    Drone            — отдельный дрон (точка с координатами и скоростью).
    Obstacle         — круглое препятствие (центр + радиус).
    Swarm            — совокупность дронов, leader-follower, формация, столкновения.
    Simulation       — главный цикл: интеграция движения и логирование метрик.

Логика управления одинакова для симулятора и ROS 2-ноды, поэтому алгоритмы
из этого пакета переносятся в пакет drone_swarm_control практически без изменений.
"""

from .drone import Drone
from .obstacle import Obstacle
from .swarm import Swarm
from .simulation import Simulation
from .metrics_logger import MetricsLogger

__all__ = [
    "Drone",
    "Obstacle",
    "Swarm",
    "Simulation",
    "MetricsLogger",
]