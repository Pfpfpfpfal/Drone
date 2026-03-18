ROS 2 + Gazebo

https://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debs.html
https://gazebosim.org/docs/harmonic/install_ubuntu/

```bash
source /opt/ros/jazzy/setup.bash
ros2 launch ros_gz_sim gz_sim.launch.py
```

```bash
sudo apt install -y \
  python3-colcon-common-extensions \
  python3-rosdep \
  python3-vcstool \
  build-essential
```

```bash
cd ~/Документы/Project/Drone
source env.sh
```
# Запуск
пустая сцена
```bash
gz sim
```

ROS<->Gazebo

```bash
source /opt/ros/jazzy/setup.bash
ros2 run ros_gz_bridge parameter_bridge \
  /X3/cmd_vel@geometry_msgs/msg/Twist[gz.msgs.Twist
```

## Простой тест
```bash
gz topic -t /X3/cmd_vel -m gz.msgs.Twist -p "linear: {x: 1.0, y: 0.0, z: 0.5}"
```

Мост на ros
```bash
source /opt/ros/jazzy/setup.bash
ros2 run ros_gz_bridge parameter_bridge \
  /world/quadcopter_teleop/pose/info@geometry_msgs/msg/PoseArray@gz.msgs.Pose_V \
  /X3/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist
```

```bash
source /opt/ros/jazzy/setup.bash
ros2 topic list
```