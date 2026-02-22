"""
Signal-injection node: publishes state transitions on a schedule for testing.

Publishes to /state_transition (std_msgs/String) in a cycle:
  IDLE -> PLANNING -> EXECUTING -> IDLE ...
Optional: can inject other signals (e.g. pose targets) on configurable topics.
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class InjectorNode(Node):
    """Injects state-transition signals on a timer for harness/testing."""

    CYCLE = ("IDLE", "PLANNING", "EXECUTING")

    def __init__(self):
        super().__init__("injector")
        self._transition_pub = self.create_publisher(String, "state_transition", 10)
        self._index = 0
        # Cycle period in seconds (time per state before advancing)
        period_sec = self.declare_parameter("period_sec", 3.0).value
        self._timer = self.create_timer(period_sec, self._inject)
        self.get_logger().info(
            f"Signal injector started: cycling {self.CYCLE} every {period_sec}s"
        )

    def _inject(self) -> None:
        state = self.CYCLE[self._index]
        msg = String()
        msg.data = state
        self._transition_pub.publish(msg)
        self.get_logger().info(f"Inject: state_transition -> {state}")
        self._index = (self._index + 1) % len(self.CYCLE)


def main(args=None):
    rclpy.init(args=args)
    node = InjectorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
