import subprocess
import re
from typing import Optional, Tuple

WORLD_TOPIC = "/world/quadcopter_teleop/pose/info"
DRONE_NAME = "X3"


def get_pose_dump() -> str:
    result = subprocess.run(
        ["gz", "topic", "-e", "-n", "1", "-t", WORLD_TOPIC],
        capture_output=True,
        text=True,
        timeout=3.0
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr)
    return result.stdout


def extract_drone_position(topic_dump: str, drone_name: str = DRONE_NAME) -> Optional[Tuple[float, float, float]]:
    pattern = re.compile(
        rf'pose\s*\{{.*?name:\s*"{re.escape(drone_name)}".*?position\s*\{{\s*x:\s*([-0-9.eE]+)\s*y:\s*([-0-9.eE]+)\s*z:\s*([-0-9.eE]+)\s*\}}',
        re.DOTALL
    )
    m = pattern.search(topic_dump)
    if not m:
        return None

    return float(m.group(1)), float(m.group(2)), float(m.group(3))


if __name__ == "__main__":
    dump = get_pose_dump()
    pos = extract_drone_position(dump)
    print("Drone position:", pos)