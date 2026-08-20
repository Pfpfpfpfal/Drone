"""Вспомогательные функции: векторы, ограничения, загрузка YAML-конфигов."""

from __future__ import annotations

from typing import Any, Dict, List, Sequence, Union

import numpy as np
from numpy.typing import ArrayLike


def to_vec(x: float, y: float, z: float) -> np.ndarray:
    """Преобразование тройки чисел в numpy-вектор."""
    return np.array([x, y, z], dtype=float)


def norm(v: ArrayLike) -> float:
    """Евклидова норма вектора."""
    arr = np.asarray(v, dtype=float)
    return float(np.linalg.norm(arr))


def safe_normalize(v: ArrayLike, eps: float = 1e-9) -> np.ndarray:
    """Нормализация вектора с защитой от деления на ноль.

    Возвращает нулевой вектор, если длина близка к нулю.
    """
    arr = np.asarray(v, dtype=float)
    n = np.linalg.norm(arr)
    if n < eps:
        return np.zeros_like(arr)
    return arr / n


def clamp(value: float, low: float, high: float) -> float:
    """Ограничение значения диапазоном [low, high]."""
    return max(low, min(high, value))


def limit_speed(v: ArrayLike, max_speed: float) -> np.ndarray:
    """Ограничение длины вектора скорости значением max_speed."""
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


def load_config(path: str) -> Dict[str, Any]:
    """Загрузка YAML-конфига сценария.

    Требуется наличие PyYAML. При отсутствии файла выбрасывает FileNotFoundError.
    """
    import yaml

    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def deep_get(d: Dict[str, Any], keys: Sequence[str], default: Any = None) -> Any:
    """Безопасное извлечение вложенного значения по цепочке ключей."""
    cur: Any = d
    for key in keys:
        if not isinstance(cur, dict) or key not in cur:
            return default
        cur = cur[key]
    return cur


def parse_position(value: Union[Sequence[float], np.ndarray]) -> List[float]:
    """Приведение стартовой/целевой позиции к списку из трёх координат.

    Если заданы только 2D-координаты, добавляется z=0.
    """
    out = [float(v) for v in value]
    while len(out) < 3:
        out.append(0.0)
    return out[:3]