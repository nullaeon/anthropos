#!/usr/bin/env bash
set -eux

# Source ROS 2 when installed (for state manager, controller nodes, simulation)
# Temporarily allow unset vars so ROS setup.bash (which uses AMENT_TRACE_SETUP_FILES etc.) does not trigger set -u
if [ -f /opt/ros/humble/setup.bash ]; then
    set +u
    source /opt/ros/humble/setup.bash
    set -u
fi

# Use host UID:GID to avoid permission issues with mounted volumes
USER_ID=${LOCAL_UID:-9001}
GROUP_ID=${LOCAL_GID:-9001}
USERNAME=dev

# If running as root (UID 0), don't try to create users/groups — just run as root
if [[ "$USER_ID" == "0" || "$GROUP_ID" == "0" ]]; then
    echo "[entrypoint] Running as root, skipping user creation."
    exec "$@"
fi

# Create group if it doesn't exist
if ! getent group "$USERNAME" >/dev/null; then
    groupadd -g "$GROUP_ID" "$USERNAME"
fi

# Create user if it doesn't exist
if ! id -u "$USERNAME" >/dev/null 2>&1; then
    useradd -m -u "$USER_ID" -g "$GROUP_ID" -s /bin/bash "$USERNAME"
fi

# Ensure dev user owns /workspace so colcon build, pip, etc. work without sudo
if [ -d /workspace ]; then
    chown -R "${USER_ID}:${GROUP_ID}" /workspace
fi

# Drop privileges and execute the command
exec gosu "$USERNAME" "$@"
