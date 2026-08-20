# pyright: reportMissingImports=false
# launch / launch_ros доступны только внутри окружения ROS 2.

"""Launch-файл для тестового запуска менеджера роя дронов."""

from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration


def generate_launch_description() -> LaunchDescription:
    params_file = LaunchConfiguration(
        "params_file",
        default="config/swarm_params.yaml",
    )

    swarm_manager = Node(
        package="drone_swarm_control",
        executable="swarm_manager",
        name="swarm_manager",
        output="screen",
        parameters=[params_file],
    )

    return LaunchDescription([swarm_manager])