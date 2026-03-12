import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TwistStamped
from sensor_msgs.msg import LaserScan
import math

# How long (seconds) to yield to human keyboard input before resuming autonomy
TELEOP_TIMEOUT = 5.0


class ReactiveController(Node):

    def __init__(self):
        super().__init__('reactive_controller')

        self.cmd_pub = self.create_publisher(TwistStamped, '/cmd_vel', 10)

        self.scan_sub = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            10
        )

        # Teleop publishes here (remapped in launch so we are the sole /cmd_vel publisher)
        self.teleop_sub = self.create_subscription(
            TwistStamped,
            '/teleop_cmd_vel',
            self.teleop_callback,
            10
        )

        self.timer = self.create_timer(0.05, self.control_loop)

        self.front_distance = float('inf')

        # Set a very slow forward speed (meters/second)
        self.slow_speed = 0.1  # adjust lower if needed

        # Most recent teleop command and the time it arrived
        self.teleop_cmd = None
        self.last_teleop_time = None

        self.FRONT_DEG = 30
        self.FRONT_RAD = math.radians(self.FRONT_DEG)

    def scan_callback(self, msg):
        mid_index = len(msg.ranges) // 2
        front_range = int(self.FRONT_RAD / msg.angle_increment)
        front_angles = msg.ranges[mid_index - front_range : mid_index + front_range]
        self.front_distance = min(front_angles)

    def teleop_callback(self, msg):
        """Store the latest teleop command and timestamp."""
        self.teleop_cmd = msg
        self.last_teleop_time = self.get_clock().now()

    def _teleop_active(self):
        """Return True if a teleop command arrived within the last TELEOP_TIMEOUT seconds."""
        if self.last_teleop_time is None:
            return False
        elapsed = (self.get_clock().now() - self.last_teleop_time).nanoseconds * 1e-9
        return elapsed < TELEOP_TIMEOUT

    def control_loop(self):
        
        SAFE_DISTANCE = 0.5  # meters, adjust as needed
        self.get_logger().info(f"Disatnce: {self.front_distance}")

        if self.front_distance < SAFE_DISTANCE:
            # Obstacle detected, stop
            cmd = TwistStamped()
            cmd.twist.linear.x = 0.0
            cmd.twist.angular.z = 0.0
            self.get_logger().info(f"Obstacle too close ({self.front_distance:.2f} m) – stopping")
            self.cmd_pub.publish(cmd)
        elif self._teleop_active():
            # Yield to human: forward the latest teleop command as-is
            self.get_logger().info("Teleop active – forwarding human input")
            self.cmd_pub.publish(self.teleop_cmd)
        else:
            # Resume autonomous drive-forward
            cmd = TwistStamped()
            cmd.twist.linear.x = self.slow_speed
            cmd.twist.angular.z = 0.0
            # self.get_logger().info("Driving")
            self.cmd_pub.publish(cmd)


def main(args=None):

    rclpy.init(args=args)

    node = ReactiveController()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()