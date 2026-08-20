# Управление роем дронов

Проект по управлению роем БПЛА: **чистый Python-симулятор** движения дронов
как точек, реализация leader-follower, удержание формации, избегание
столкновений, обход препятствий через artificial potential fields (APF),
метрики и графики. Алгоритмы затем переносятся в ROS 2-пакет без изменений.

Модель движения:
```
новая позиция = старая позиция + скорость * dt
```

## Структура репозитория

```
Drone/
├── PLAN.md                         # исходное техническое задание
├── requirements.txt                # зависимости Python
├── drone_control/                  # устаревший скрипт для Gazebo (один дрон)
│   └── waypoint_follower.py
├── swarm_sim/                      # чистый Python-симулятор роя
│   ├── swarm_sim/                  # пакет с классами и алгоритмами
│   │   ├── drone.py                #   класс Drone (точка)
│   │   ├── obstacle.py             #   класс Obstacle (круг/цилиндр)
│   │   ├── formation_controller.py #   leader-follower и ошибка формации
│   │   ├── collision_avoidance.py  #   отталкивание от соседей
│   │   ├── potential_fields.py     #   APF: притяжение к цели + обход препятствий
│   │   ├── swarm.py                #   класс Swarm (совокупность дронов)
│   │   ├── simulation.py           #   класс Simulation + сборка из YAML
│   │   ├── metrics_logger.py       #   запись метрик в CSV
│   │   └── utils.py                #   векторные операции
│   ├── configs/                    # YAML-конфиги сценариев
│   ├── scripts/                    # генератор сценариев и анализ результатов
│   ├── tests/                      # unit-тесты (pytest)
│   ├── run_simulation.py           # запуск симуляции из конфига
│   └── results/                    # выходные CSV и PNG (создаётся при запуске)
├── cv_module/                      # OpenCV-детектор цветной цели (без дрона)
│   ├── target_detector.py
│   └── demo_detector.py
└── drone_swarm_control/            # ROS 2-пакет (Jazzy), логика из swarm_sim
    ├── drone_swarm_control/        #   swarm_manager, formation_controller, ...
    ├── launch/swarm_test.launch.py
    ├── config/swarm_params.yaml
    ├── package.xml
    └── setup.py
```

## Установка

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Запуск симуляции и анализа

```bash
cd swarm_sim

# 1. запустить сценарий (остановка при достижении цели)
python run_simulation.py --config configs/scenario_01_no_obstacles.yaml \
    --output results/scenario01/metrics.csv --stop-when-reached

# 2. построить все графики и сводную таблицу
python scripts/analyze_results.py --input results/scenario01/metrics.csv \
    --outdir results/scenario01/

# 3. (опционально) перегенерировать YAML-конфиги сценариев
python scripts/generate_scenarios.py
```

На выходе в `results/` появляются:
- `trajectory_plot.png` — траектории дронов, старты, цель, препятствия;
- `formation_error.png` — ошибка формации во времени;
- `min_distance.png` — минимальное расстояние между дронами;
- `distance_to_goal.png` — дистанция каждого дрона до цели;
- `summary_metrics.csv` — сводные метрики по каждому дрону;
- `metrics.csv` — полный журнал метрик.

## Сценарии

| Файл | Описание |
|------|----------|
| `scenario_01_no_obstacles.yaml` | 3 дрона, без препятствий |
| `scenario_02_with_obstacle.yaml` | 3 дрона + препятствие на пути |
| `scenario_03_five_drones.yaml` | 5 дронов в V-формации |
| `scenario_04_crossing_paths.yaml` | пересекающиеся траектории |

## Тесты

```bash
cd swarm_sim && pytest -v
```

Проверяются четыре ключевых свойства алгоритма:
1. дрон движется к цели;
2. дроны не сталкиваются (мин. расстояние >= safe_distance);
3. формация сохраняется (ошибка формации < порога);
4. препятствие вызывает отклонение траектории (нет прохода через круг).

## OpenCV-детектор цели

```bash
cd cv_module && python demo_detector.py
```

Находит красный круг на синтетическом кадре, определяет центр и выдаёт
команду движения (влево/вправо/вперёд/поиск).

## ROS 2 (drone_swarm_control)

См. [`drone_swarm_control/README.md`](drone_swarm_control/README.md).
Сборка: `colcon build --packages-select drone_swarm_control`.

## Установка ROS 2 Jazzy + Gazebo Harmonic

Инструкция сохранена в истории README; кратко:

```bash
sudo apt install -y ros-jazzy-desktop ros-jazzy-ros-gz
echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc
```

Подробнее — в официальных документах:
- https://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debs.html
- https://gazebosim.org/docs/all/ros_installation/