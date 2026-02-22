"""
State manager node: manages robot state (IDLE, PLANNING, EXECUTING).

Publishes current state on /robot_state.
Accepts transition requests on /state_transition (std_msgs/String: "IDLE" | "PLANNING" | "EXECUTING").
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class StateManagerNode(Node):
    """Publishes and updates robot state; validates transitions."""

    VALID_STATES = ("IDLE", "PLANNING", "EXECUTING")

    def __init__(self):
        super().__init__("state_manager")
        self._state = "IDLE"
        self._state_pub = self.create_publisher(String, "robot_state", 10)
        self._transition_sub = self.create_subscription(
            String, "state_transition", self._on_transition, 10
        )
        self._timer = self.create_timer(0.5, self._publish_state)
        self.get_logger().info("State manager started. Current state: IDLE")

    def _on_transition(self, msg: String) -> None:
        requested = msg.data.strip().upper()
        if requested not in self.VALID_STATES:
            self.get_logger().warn(
                f"Ignoring invalid state '{msg.data}'. Valid: {self.VALID_STATES}"
            )
            return
        if requested != self._state:
            self._state = requested
            self.get_logger().info(f"State transition -> {self._state}")

    def _publish_state(self) -> None:
        msg = String()
        msg.data = self._state
        self._state_pub.publish(msg)

    def get_state(self) -> str:
        return self._state


def main(args=None):
    rclpy.init(args=args)
    node = StateManagerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
