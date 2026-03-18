import subprocess
import time
import math
import re
from typing import Optional, Tuple, List

WORLD_TOPIC = "/world/quadcopter_teleop/pose/info"   # замени на свой
CMD_TOPIC = "/X3/cmd_vel"
DRONE_NAME = "X3"

WAYPOINTS: List[Tuple[float, float, float]] = [
    (0.0, 0.0, 1.5),
    (2.0, 0.0, 1.5),
    (2.0, 2.0, 1.5),
    (0.0, 2.0, 1.5),
    (0.0, 0.0, 1.5),
]

MAX_SPEED = 0.6
REACH_EPS = 0.5
CONTROL_DT = 0.15
KP = 0.8

def run_cmd(cmd: List[str], timeout: float = 3.0) -> str:
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"Command failed: {' '.join(cmd)}\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )
    return result.stdout

def get_pose_dump() -> str:
    return run_cmd(
        ["gz", "topic", "-e", "-n", "1", "-t", WORLD_TOPIC],
        timeout=3.0
    )

def extract_drone_position(topic_dump: str, drone_name: str = DRONE_NAME) -> Optional[Tuple[float, float, float]]:
    pattern = re.compile(
        rf'pose\s*\{{.*?name:\s*"{re.escape(drone_name)}".*?position\s*\{{\s*x:\s*([-0-9.eE]+)?\s*y:\s*([-0-9.eE]+)?\s*z:\s*([-0-9.eE]+)?\s*\}}',
        re.DOTALL
    )
    m = pattern.search(topic_dump)
    if not m:
        return None

    x = float(m.group(1) or 0.0)
    y = float(m.group(2) or 0.0)
    z = float(m.group(3) or 0.0)
    return (x, y, z)


def publish_cmd_vel(vx: float, vy: float, vz: float, yaw_rate: float = 0.0) -> None:
    msg = (
        f'linear: {{x: {vx}, y: {vy}, z: {vz}}}, '
        f'angular: {{x: 0.0, y: 0.0, z: {yaw_rate}}}'
    )
    subprocess.run(
        ["gz", "topic", "-t", CMD_TOPIC, "-m", "gz.msgs.Twist", "-p", msg],
        capture_output=True,
        text=True
    )

def stop_drone() -> None:
    publish_cmd_vel(0.0, 0.0, 0.0, 0.0)

def compute_cmd(pos: Tuple[float, float, float],
                target: Tuple[float, float, float],
                kp: float = KP,
                max_speed: float = MAX_SPEED) -> Tuple[float, float, float]:
    dx = target[0] - pos[0]
    dy = target[1] - pos[1]
    dz = target[2] - pos[2]

    vx = kp * dx
    vy = kp * dy
    vz = kp * dz

    speed = math.sqrt(vx * vx + vy * vy + vz * vz)
    if speed > max_speed:
        scale = max_speed / speed
        vx *= scale
        vy *= scale
        vz *= scale

    return vx, vy, vz

def main() -> None:
    print("Старт waypoint follower")

    try:
        for idx, target in enumerate(WAYPOINTS):
            print(f"\nИдем к точке {idx}: {target}")

            stable_hits = 0

            while True:
                dump = get_pose_dump()
                pos = extract_drone_position(dump, DRONE_NAME)

                if pos is None:
                    print("Не удалось найти позицию дрона")
                    stop_drone()
                    time.sleep(CONTROL_DT)
                    continue

                dx = target[0] - pos[0]
                dy = target[1] - pos[1]
                dz = target[2] - pos[2]
                dist = math.sqrt(dx * dx + dy * dy + dz * dz)

                print(
                    f"pos=({pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f}) "
                    f"target={target} dist={dist:.2f}"
                )

                if dist < REACH_EPS:
                    stable_hits += 1
                    stop_drone()
                    if stable_hits >= 3:
                        print(f"Точка {idx} достигнута")
                        time.sleep(0.8)
                        break
                else:
                    stable_hits = 0
                    vx, vy, vz = compute_cmd(pos, target)
                    publish_cmd_vel(vx, vy, vz)

                time.sleep(CONTROL_DT)

        print("\nВсе точки пройдены")
        stop_drone()

    except KeyboardInterrupt:
        print("\nОстановлено пользователем")
        stop_drone()
    except Exception as e:
        print(f"\nОшибка: {e}")
        stop_drone()

if __name__ == "__main__":
    main()