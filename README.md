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

пустая сцена
```bash
gz sim
```

ROS<->Gazebo