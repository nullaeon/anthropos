"""
Controller node: updates robot pose based on current state.

Subscribes to /robot_state (std_msgs/String).
Publishes /robot_pose (geometry_msgs/PoseStamped).

- IDLE:    hold current pose (no change).
- PLANNING: hold current pose (no change).
- EXECUTING: apply pose updates (e.g. simulate motion).
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import PoseStamped, Point, Quaternion


class ControllerNode(Node):
    """Publishes robot pose; updates pose based on state (e.g. motion in EXECUTING)."""

    def __init__(self):
        super().__init__("controller")
        self._state = "IDLE"
        self._pose_pub = self.create_publisher(PoseStamped, "robot_pose", 10)
        self._state_sub = self.create_subscription(
            String, "robot_state", self._on_state, 10
        )
        # Current pose (identity by default)
        self._x, self._y, self._z = 0.0, 0.0, 0.0
        self._qx, self._qy, self._qz, self._qw = 0.0, 0.0, 0.0, 1.0
        # Publish at 20 Hz; in EXECUTING we update pose each step
        self._timer = self.create_timer(0.05, self._tick)
        self.get_logger().info("Controller started. Subscribed to robot_state.")

    def _on_state(self, msg: String) -> None:
        self._state = msg.data.strip().upper()

    def _tick(self) -> None:
        if self._state == "EXECUTING":
            # Simulate forward motion in +x
            self._x += 0.01
        # IDLE and PLANNING: no pose change
        self._publish_pose()

    def _publish_pose(self) -> None:
        msg = PoseStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = "world"
        msg.pose.position = Point(x=self._x, y=self._y, z=self._z)
        msg.pose.orientation = Quaternion(
            x=self._qx, y=self._qy, z=self._qz, w=self._qw
        )
        self._pose_pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = ControllerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
