import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TwistStamped
from sensor_msgs.msg import LaserScan
import math
import random

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

        self.timer_period = 0.05
        self.timer = self.create_timer(self.timer_period, self.control_loop)

        self.front_distance = float('inf')

        # Set a very slow forward speed (meters/second)
        self.slow_speed = 0.1

        # Most recent teleop command and the time it arrived
        self.teleop_cmd = None
        self.last_teleop_time = None

        self.FRONT_DEG = 15 # ~15 seems to work well
        self.FRONT_RAD = math.radians(self.FRONT_DEG)

        # BEHAVIOR #5: random turn after every 1 ft forward
        self.ONE_FOOT_M = 0.3048
        self.MAX_TURN_DEG = 15.0
        self.turn_speed = 0.5  # rad/s

        self.forward_distance_accum = 0.0 # Estimated forward distance traveled during autonomous driving

        # Turning state
        self.is_turning = False
        self.turn_end_time = None
        self.current_turn_direction = 0.0

    def scan_callback(self, msg):
        mid_index = len(msg.ranges) // 2
        front_range = int(self.FRONT_RAD / msg.angle_increment)

        start = max(0, mid_index - front_range)
        end = min(len(msg.ranges), mid_index + front_range)

        front_angles = msg.ranges[start:end]

        # Filter out inf/nan values
        valid_ranges = [r for r in front_angles if math.isfinite(r)]

        if valid_ranges:
            self.front_distance = min(valid_ranges)
        else:
            self.front_distance = float('inf')

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


    # For Behavior 5
    def _start_random_turn(self):
        """Begin a random turn in range [-15 deg, +15 deg]."""
        angle_deg = random.uniform(-self.MAX_TURN_DEG, self.MAX_TURN_DEG)
        angle_rad = math.radians(angle_deg)

        # Don't turn if its super close to zero
        if abs(angle_rad) < 1e-3:
            angle_rad = math.radians(5.0)

        turn_duration = abs(angle_rad) / self.turn_speed

        self.is_turning = True
        self.current_turn_direction = 1.0 if angle_rad > 0.0 else -1.0
        self.turn_end_time = self.get_clock().now().nanoseconds * 1e-9 + turn_duration

        # Debugging output
        self.get_logger().info(
            f"Reached 1 ft. Turning {angle_deg:.2f} deg "
            f"for {turn_duration:.2f} s"
        )

    def _publish_stop(self):
        cmd = TwistStamped()
        cmd.twist.linear.x = 0.0
        cmd.twist.angular.z = 0.0
        self.cmd_pub.publish(cmd)

    def _publish_forward(self):
        cmd = TwistStamped()
        cmd.twist.linear.x = self.slow_speed
        cmd.twist.angular.z = 0.0
        self.cmd_pub.publish(cmd)

    def _publish_turn(self):
        cmd = TwistStamped()
        cmd.twist.linear.x = 0.0
        cmd.twist.angular.z = self.current_turn_direction * self.turn_speed
        self.cmd_pub.publish(cmd)

    def control_loop(self):
        SAFE_DISTANCE = 0.5  # In meters
        now_sec = self.get_clock().now().nanoseconds * 1e-9

        self.get_logger().info(f"Distance: {self.front_distance:.2f}")

        if self.front_distance < SAFE_DISTANCE:
            # Highest priority: stop for obstacle
            self.is_turning = False
            self.turn_end_time = None
            self.get_logger().info(
                f"Obstacle too close ({self.front_distance:.2f} m) - stopping"
            )
            self._publish_stop()

        elif self._teleop_active():
            # Next priority: human teleop
            self.is_turning = False
            self.turn_end_time = None
            self.get_logger().info("Teleop active - forwarding human input")
            self.cmd_pub.publish(self.teleop_cmd)

        elif self.is_turning:
            # Continue random turn until done
            if now_sec < self.turn_end_time:
                self.get_logger().info("Executing random turn")
                self._publish_turn()
            else:
                self.is_turning = False
                self.turn_end_time = None
                self.forward_distance_accum = 0.0
                self.get_logger().info("Turn complete, resuming forward drive")
                self._publish_forward()

        else:
            # Autonomous forward drive
            self.forward_distance_accum += self.slow_speed * self.timer_period

            if self.forward_distance_accum >= self.ONE_FOOT_M:
                self._start_random_turn()
                self._publish_turn()
            else:
                self._publish_forward()


def main(args=None):
    rclpy.init(args=args)

    node = ReactiveController()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
