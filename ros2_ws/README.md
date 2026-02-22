# Anthropos ROS 2 Workspace

## Build

From workspace root (e.g. inside container with ROS 2 sourced):

```bash
source /opt/ros/humble/setup.bash
cd ros2_ws
colcon build
source install/setup.bash
```

## Packages

### anthropos_control

- **state_manager** – Manages robot state: `IDLE`, `PLANNING`, `EXECUTING`.
  - Publishes: `/robot_state` (std_msgs/String)
  - Subscribes: `/state_transition` (std_msgs/String) to request state changes

- **controller** – Updates robot pose based on state.
  - Subscribes: `/robot_state`
  - Publishes: `/robot_pose` (geometry_msgs/PoseStamped)
  - In `EXECUTING`, pose is updated (e.g. simulated motion); in `IDLE`/`PLANNING` pose is held.

## Run

### Harness (recommended): launch all nodes + signal injector

Starts state_manager, controller, and an **injector** node that cycles state every few seconds (IDLE → PLANNING → EXECUTING → IDLE …). No manual `ros2 topic pub` needed.

```bash
source install/setup.bash
ros2 launch anthropos_control harness.launch.py
```

Optional: change cycle period (default 3 s per state):

```bash
ros2 launch anthropos_control harness.launch.py injector_period_sec:=5.0
```

In another terminal you can watch state and pose:

```bash
ros2 topic echo /robot_state
ros2 topic echo /robot_pose
```

### Manual: run nodes only (no injector)

```bash
# Terminal 1: state manager
ros2 run anthropos_control state_manager

# Terminal 2: controller
ros2 run anthropos_control controller

# Request state change (e.g. from another terminal)
ros2 topic pub --once /state_transition std_msgs/msg/String "{data: 'EXECUTING'}"

# Inspect state and pose
ros2 topic echo /robot_state
ros2 topic echo /robot_pose
```

### Injector node alone

Run the injector with a custom period (e.g. 2 s):

```bash
ros2 run anthropos_control injector --ros-args -p period_sec:=2.0
```
