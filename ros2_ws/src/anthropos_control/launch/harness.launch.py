"""
Launch harness: state_manager + controller + signal injector.

Runs all three nodes so the system cycles through IDLE / PLANNING / EXECUTING
and the controller updates pose in EXECUTING.

To drive state manually (no injector), run state_manager and controller separately
and publish to /state_transition.
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    period_arg = DeclareLaunchArgument(
        "injector_period_sec",
        default_value="3.0",
        description="Seconds per state in the injector cycle (IDLE->PLANNING->EXECUTING->...).",
    )

    state_manager = Node(
        package="anthropos_control",
        executable="state_manager",
        name="state_manager",
        output="screen",
    )

    controller = Node(
        package="anthropos_control",
        executable="controller",
        name="controller",
        output="screen",
    )

    injector = Node(
        package="anthropos_control",
        executable="injector",
        name="injector",
        output="screen",
        parameters=[{"period_sec": LaunchConfiguration("injector_period_sec")}],
    )

    return LaunchDescription([
        period_arg,
        state_manager,
        controller,
        injector,
    ])
