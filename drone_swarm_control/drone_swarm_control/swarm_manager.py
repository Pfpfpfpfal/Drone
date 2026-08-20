# pyright: reportMissingImports=false
# rclpy / geometry_msgs доступны только внутри окружения ROS 2.

"""ROS 2-узел управления роем дронов.

Подписывается на позы дронов, вычисляет управляющие скорости
(leader-follower + формация + избегание столкновений) и публикует
команды в топики cmd_vel каждого дрона.

Пример запуска (после сборки пакета):
    ros2 launch drone_swarm_control swarm_test.launch.py

Замечание: узел написан так, чтобы логику можно было проверить без Gazebo —
вычислительные модули (formation_controller, collision_avoidance, utils)
не зависят от rclpy и тестируются отдельно.
"""

from __future__ import annotations

import math

import numpy as np
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, PoseStamped

from .collision_avoidance import CollisionAvoidance
from .formation_controller import FormationController
from .utils import limit_speed


class SwarmManager(Node):
    """Менеджер роя: приём поз, расчёт команд, публикация cmd_vel."""

    def __init__(self) -> None:
        super().__init__("swarm_manager")

        # --- параметры ---
        self.declare_parameter("goal_position", [20.0, 10.0, 2.0])
        self.declare_parameter("k_goal", 0.8)
        self.declare_parameter("k_formation", 0.6)
        self.declare_parameter("k_avoidance", 1.2)
        self.declare_parameter("max_velocity", 2.0)
        self.declare_parameter("safe_distance", 1.5)
        self.declare_parameter("drone_ids", [1, 2, 3])
        self.declare_parameter("offsets", [[0.0, 0.0, 0.0], [-2.0, -2.0, 0.0], [-2.0, 2.0, 0.0]])
        self.declare_parameter("update_rate_hz", 20.0)

        goal = self.get_parameter("goal_position").value
        self.goal_position = np.asarray(goal, dtype=float)
        self.k_goal = float(self.get_parameter("k_goal").value)
        self.max_velocity = float(self.get_parameter("max_velocity").value)

        drone_ids = list(self.get_parameter("drone_ids").value)
        offsets = self.get_parameter("offsets").value
        self.offsets = {int(d): np.asarray(o, dtype=float) for d, o in zip(drone_ids, offsets)}

        self.formation = FormationController(
            k_formation=float(self.get_parameter("k_formation").value),
            offsets=self.offsets,
        )
        self.collision = CollisionAvoidance(
            safe_distance=float(self.get_parameter("safe_distance").value),
            k_avoidance=float(self.get_parameter("k_avoidance").value),
        )

        self.positions: dict[int, np.ndarray] = {}
        self.leader_id = drone_ids[0] if drone_ids else 1

        # --- топики ---
        self.pose_subs = {}
        self.cmd_pubs = {}
        for did in drone_ids:
            self.pose_subs[did] = self.create_subscription(
                PoseStamped,
                f"/drone_{did}/pose",
                lambda msg, d=did: self._on_pose(msg, d),
                10,
            )
            self.cmd_pubs[did] = self.create_publisher(Twist, f"/drone_{did}/cmd_vel", 10)

        rate = float(self.get_parameter("update_rate_hz").value)
        self.create_timer(1.0 / rate, self._control_loop)

        self.get_logger().info("SwarmManager запущен")

    def _on_pose(self, msg: PoseStamped, drone_id: int) -> None:
        p = msg.pose.position
        self.positions[drone_id] = np.array([p.x, p.y, p.z])

    def compute_command(self, drone_id: int) -> np.ndarray:
        """Управляющая скорость одного дрона (вектор)."""
        pos = self.positions.get(drone_id)
        if pos is None:
            return np.zeros(3)

        if drone_id == self.leader_id:
            target = self.goal_position
        else:
            target = self.formation.desired_position(
                self.positions[self.leader_id], drone_id
            )

        v_goal = self.k_goal * (target - pos)
        v_formation = self.formation.correction(pos, self.positions[self.leader_id], drone_id)
        v_avoid = self.collision.avoidance_force(pos, self.positions, drone_id)

        v = limit_speed(v_goal + v_formation + v_avoid, self.max_velocity)
        return v

    def _control_loop(self) -> None:
        if self.leader_id not in self.positions:
            return
        for did, pub in self.cmd_pubs.items():
            v = self.compute_command(did)
            twist = Twist()
            twist.linear.x = float(v[0])
            twist.linear.y = float(v[1])
            twist.linear.z = float(v[2])
            pub.publish(twist)

    def stop_all(self) -> None:
        for pub in self.cmd_pubs.values():
            twist = Twist()
            pub.publish(twist)


def main(args=None) -> None:
    rclpy.init(args=args)
    node = SwarmManager()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.stop_all()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()