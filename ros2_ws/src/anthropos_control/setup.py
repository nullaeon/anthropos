import os
from glob import glob
from setuptools import find_packages, setup

package_name = "anthropos_control"

setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        (os.path.join("share", package_name, "launch"), glob("launch/*.py")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Anthropos",
    maintainer_email="dev@anthropos",
    description="State manager and controller nodes for Anthropos robot simulation.",
    license="Apache-2.0",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "state_manager = anthropos_control.state_manager_node:main",
            "controller = anthropos_control.controller_node:main",
            "injector = anthropos_control.injector_node:main",
        ],
    },
)
