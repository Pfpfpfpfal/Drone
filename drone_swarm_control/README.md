# drone_swarm_control

ROS 2-пакет управления роем дронов (Jazzy). Логика перенесена из чистого
Python-симулятора [`swarm_sim`](../swarm_sim) без изменений по сути —
это упрощает перенос проверенного алгоритма на реальные топики.

## Состав

```
drone_swarm_control/
├── drone_swarm_control/
│   ├── swarm_manager.py         # ROS 2-узел: позы -> cmd_vel
│   ├── formation_controller.py  # где должен быть каждый дрон относительно лидера
│   ├── collision_avoidance.py   # отталкивание от соседей
│   ├── metrics_logger.py        # сохранение метрик в CSV
│   └── utils.py                 # векторные операции
├── launch/swarm_test.launch.py
├── config/swarm_params.yaml
├── package.xml
├── setup.py
└── resource/drone_swarm_control
```

## Сборка

```bash
colcon build --packages-select drone_swarm_control
source install/setup.bash
```

## Запуск

```bash
ros2 launch drone_swarm_control swarm_test.launch.py
```

Ожидаемые топики на вход:
- `/drone_<id>/pose` (`geometry_msgs/PoseStamped`) — текущая поза каждого дрона;
на выход:
- `/drone_<id>/cmd_vel` (`geometry_msgs/Twist`) — линейная скорость дрона.

## Подключение к Gazebo

В `swarm_manager.py` замените источники поз (например, на
`/world/.../pose/info` через `ros_gz_bridge`) и названия топиков команд под
ваши дроны — как это сделано в [`drone_control/waypoint_follower.py`](../drone_control/waypoint_follower.py).

## Проверка логики без Gazebo

Вычислительные модули не зависят от rclpy и могут быть протестированы
отдельно в окружении `swarm_sim`.