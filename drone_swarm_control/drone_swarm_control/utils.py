"""Вспомогательные векторные операции для ROS 2-узла управления роем."""

from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike


def safe_normalize(v: ArrayLike, eps: float = 1e-9) -> np.ndarray:
    """Нормализация вектора с защитой от деления на ноль."""
    arr = np.asarray(v, dtype=float)
    n = np.linalg.norm(arr)
    if n < eps:
        return np.zeros_like(arr)
    return arr / n


def limit_speed(v: ArrayLike, max_speed: float) -> np.ndarray:
    """Ограничение длины вектора скорости."""
    arr = np.asarray(v, dtype=float)
    n = np.linalg.norm(arr)
    if n > max_speed and n > 0.0:
        return arr * (max_speed / n)
    return arr


def distance(a: ArrayLike, b: ArrayLike) -> float:
    """Расстояние между двумя точками."""
    return float(
        np.linalg.norm(np.asarray(a, dtype=float) - np.asarray(b, dtype=float))
    )


def horizontal_distance(a: ArrayLike, b: ArrayLike) -> float:
    """Расстояние в горизонтальной плоскости XY."""
    pa = np.asarray(a, dtype=float)
    pb = np.asarray(b, dtype=float)
    return float(np.linalg.norm(pa[:2] - pb[:2]))