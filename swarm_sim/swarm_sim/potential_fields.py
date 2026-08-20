"""Компьютерная (искусственная) потенциальная функция для обхода препятствий.

Притяжение к цели + отталкивание от препятствий (artificial potential fields).
"""

from __future__ import annotations

import numpy as np

from .utils import safe_normalize


class PotentialFields:
    """Реализация artificial potential fields (APF).

    Суммарный вектор:
        F = k_goal * e_goal + k_obs * sum(e_obs_i * falloff_i)
    где e_goal — направление на цель, e_obs_i — направление от препятствия.
    """

    def __init__(
        self,
        k_goal: float = 0.8,
        k_obstacle: float = 2.5,
        sensor_range: float = 5.0,
        max_repulsion: float = 6.0,
    ) -> None:
        self.k_goal = float(k_goal)
        self.k_obstacle = float(k_obstacle)
        self.sensor_range = float(sensor_range)
        # верхний предел силы отталкивания (защита от деления на ~0)
        self.max_repulsion = float(max_repulsion)
        # доля тангенциальной составляющей (обходим препятствие по дуге)
        self.k_tangent = 0.9

    def attraction(self, pos: np.ndarray, goal: np.ndarray) -> np.ndarray:
        """Вектор притяжения к цели (пропорциональный P-регулятор).

        Величина пропорциональна расстоянию до цели, поэтому скорость плавно
        уменьшается при приближении и дрон устойчиво сходится к точке.
        Ограничение по max_velocity выполняется в Swarm.compute_commands().
        """
        return self.k_goal * (goal - pos)

    def repulsion_from_obstacle(
        self, pos: np.ndarray, center: np.ndarray, radius: float, influence: float
    ) -> np.ndarray:
        """Вектор отталкивания от одного препятствия (в пределах сенсора).

        Состоит из радиальной и тангенциальной составляющих. Тангенциальная
        составляющая направлена перпендикулярно направлению к центру и помогает
        обойти препятствие по дуге, избегая локального минимума при лобовом
        подходе.

        Если препятствие за пределами sensor_range — возвращается нулевой вектор
        (имитация ограниченного восприятия среды / псевдо-SLAM, вариант B).
        """
        # препятствие рассматриваем как «круг» в горизонтальной плоскости XY
        # (модель цилиндра): обход считаем по 2D-проекции, вертикаль не мешает
        delta = np.array([pos[0] - center[0], pos[1] - center[1], 0.0])
        dist = float(np.linalg.norm(delta))
        if dist < 1e-9:
            return np.zeros(3)

        # не учитываем препятствия дальше зоны восприятия сенсора
        if dist > self.sensor_range:
            return np.zeros(3)

        # сила растёт при приближении к поверхности (поверхность на dist == radius)
        surface_dist = max(dist - radius, 1e-6)
        if surface_dist >= influence:
            return np.zeros(3)

        # гиперболическая зависимость: сила резко растёт около поверхности,
        # чтобы преодолевать притяжение к цели и огибать препятствие
        ratio = 1.0 / surface_dist - 1.0 / influence
        strength = min(self.k_obstacle * ratio, self.max_repulsion)

        radial_dir = safe_normalize(delta)  # от центра препятствия к дрону
        # тангенциальное направление (перпендикуляр в плоскости XY)
        tangent_dir = np.array([-radial_dir[1], radial_dir[0], 0.0])

        return strength * radial_dir + self.k_tangent * strength * tangent_dir

    def attraction_scale(self, pos: np.ndarray, obstacles: list) -> float:
        """Коэффициент подавления притяжения к цели вблизи препятствий.

        1.0 — вдали от препятствий; 0.0 — на поверхности препятствия.
        Подавление притяжения предотвращает лобовое врезание и локальный
        минимум APF: рядом с препятствием дрон уступает отталкиванию
        (в т.ч. тангенциальному) и огибает его по дуге.
        """
        if not obstacles:
            return 1.0
        scale = 1.0
        for obs in obstacles:
            # используем горизонтальную дистанцию (препятствие = цилиндр)
            dist = float(np.linalg.norm(np.array([pos[0] - obs.center[0], pos[1] - obs.center[1]])))
            surface_dist = max(dist - obs.radius, 0.0)
            if surface_dist >= obs.influence_radius:
                continue
            f = max(surface_dist / obs.influence_radius, 0.0)
            scale = min(scale, f)
        return float(scale)

    def compute_force(
        self,
        pos: np.ndarray,
        goal: np.ndarray,
        obstacles: list,
    ) -> np.ndarray:
        """Суммарный управляющий вектор от потенциальных полей."""
        force = self.attraction(pos, goal) * self.attraction_scale(pos, obstacles)
        for obs in obstacles:
            force += self.repulsion_from_obstacle(
                pos, obs.center, obs.radius, obs.influence_radius
            )
        return force