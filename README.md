# ROS 2 Jazzy + Gazebo Harmonic + ros_gz_bridge

```
https://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debs.html
```

```
https://gazebosim.org/docs/all/ros_installation/
```

# Установка
Для Jazzy deb-пакеты доступны под Ubuntu Noble 24.04

```bash
sudo apt update
sudo apt install -y software-properties-common curl
sudo add-apt-repository universe
sudo apt update
```

```bash
sudo apt install -y ros2-apt-source
sudo apt update
```

Альтернатива
```bash
export ROS_APT_SOURCE_VERSION=$(curl -s https://api.github.com/repos/ros-infrastructure/ros-apt-source/releases/latest | grep -F "tag_name" | awk -F'"' '{print $4}')

curl -L -o /tmp/ros2-apt-source.deb \
"https://github.com/ros-infrastructure/ros-apt-source/releases/download/${ROS_APT_SOURCE_VERSION}/ros2-apt-source_${ROS_APT_SOURCE_VERSION}.$(. /etc/os-release && echo ${UBUNTU_CODENAME:-${VERSION_CODENAME}})_all.deb"

sudo dpkg -i /tmp/ros2-apt-source.deb
sudo apt update
```

```bash
sudo apt install -y ros-jazzy-desktop
sudo apt install -y ros-jazzy-ros-gz
```

```bash
echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

Проверка
```bash
echo $ROS_DISTRO
ros2 --version
gz sim --versions
```

ROS-Gazebo
```bash
ros2 pkg list | grep ros_gz
```

Тестовый запуск Gazebo через ROS 2

Term1
```bash
ros2 launch ros_gz_sim gz_sim.launch.py gz_args:=shapes.sdf
```

term2
```bash
ros2 topic list
```

```bash
ros2 run ros_gz_bridge parameter_bridge /clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock
```

alt-term
```bash
ros2 topic echo /clock
```