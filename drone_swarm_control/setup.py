from setuptools import find_packages, setup

PACKAGE_NAME = "drone_swarm_control"

setup(
    name=PACKAGE_NAME,
    version="0.1.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + PACKAGE_NAME]),
        ("share/" + PACKAGE_NAME, ["package.xml"]),
        ("share/" + PACKAGE_NAME + "/launch", ["launch/swarm_test.launch.py"]),
        ("share/" + PACKAGE_NAME + "/config", ["config/swarm_params.yaml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Student",
    maintainer_email="you@example.com",
    description="Управление роем дронов (leader-follower, формация, обход препятствий)",
    license="MIT",
    entry_points={
        "console_scripts": [
            "swarm_manager = drone_swarm_control.swarm_manager:main",
        ],
    },
)