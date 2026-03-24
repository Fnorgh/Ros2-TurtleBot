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
        self.left_distance  = float('inf')
        self.right_distance = float('inf')

        # Set a very slow forward speed (meters/second)
        self.slow_speed   =  0.1
        self.backup_speed = -0.1

        # Most recent teleop command and the time it arrived
        self.teleop_cmd = None
        self.last_teleop_time = None

        self.FRONT_DEG = 30  # 30 deg each side (left 0→+30, right -30→0)
        self.FRONT_RAD = math.radians(self.FRONT_DEG)

        # If |left_distance - right_distance| > threshold → asymmetric
        self.SYMMETRY_THRESHOLD = 0.3  # meters

        # BEHAVIOR #5: random turn after every 1 ft forward
        self.ONE_FOOT_M    = 0.3048
        self.MAX_TURN_DEG  = 0.0
        self.turn_speed    = 0.5  # rad/s

        self.forward_distance_accum = 0.0

        # Random-turn state (Behavior 5)
        self.is_turning           = False
        self.turn_end_time        = None
        self.current_turn_direction = 0.0

        # Asymmetric avoidance turn state
        self.is_avoiding          = False
        self.avoid_end_time       = None
        self.avoid_turn_direction = 0.0

        # Symmetric escape state (back up then spin)
        self.is_escaping          = False
        self.escape_phase         = None   # 'backing' | 'turning'
        self.escape_phase_end_time = None
        self.escape_turn_direction = 0.0

    # ------------------------------------------------------------------
    # Sensor callback
    # ------------------------------------------------------------------

    def scan_callback(self, msg):
        n               = len(msg.ranges)
        angle_increment = msg.angle_increment

        # Compute the index that points directly forward (angle = 0)
        forward_index = int(round((0.0 - msg.angle_min) / angle_increment)) % n
        front_range   = int(self.FRONT_RAD / angle_increment)

        left_ranges  = []
        right_ranges = []

        for i in range(1, front_range + 1):
            r_left  = msg.ranges[(forward_index + i) % n]
            r_right = msg.ranges[(forward_index - i) % n]
            if math.isfinite(r_left):
                left_ranges.append(r_left)
            if math.isfinite(r_right):
                right_ranges.append(r_right)

        # Include the dead-ahead ray in both halves for front_distance
        center = msg.ranges[forward_index]
        all_ranges = left_ranges + right_ranges + ([center] if math.isfinite(center) else [])

        self.front_distance = min(all_ranges)   if all_ranges   else float('inf')
        self.left_distance  = min(left_ranges)  if left_ranges  else float('inf')
        self.right_distance = min(right_ranges) if right_ranges else float('inf')

    # ------------------------------------------------------------------
    # Teleop helpers
    # ------------------------------------------------------------------

    def teleop_callback(self, msg):
        self.teleop_cmd       = msg
        self.last_teleop_time = self.get_clock().now()

    def _teleop_active(self):
        if self.last_teleop_time is None:
            return False
        elapsed = (self.get_clock().now() - self.last_teleop_time).nanoseconds * 1e-9
        return elapsed < TELEOP_TIMEOUT

    # ------------------------------------------------------------------
    # Maneuver starters
    # ------------------------------------------------------------------

    def _start_random_turn(self):
        """Begin a random turn in range [-15 deg, +15 deg] (Behavior 5)."""
        angle_deg = random.uniform(-self.MAX_TURN_DEG, self.MAX_TURN_DEG)
        angle_rad = math.radians(angle_deg)
        if abs(angle_rad) < 1e-3:
            angle_rad = math.radians(5.0)

        turn_duration = abs(angle_rad) / self.turn_speed
        self.is_turning             = True
        self.current_turn_direction = 1.0 if angle_rad > 0.0 else -1.0
        self.turn_end_time          = self.get_clock().now().nanoseconds * 1e-9 + turn_duration
        self.get_logger().info(
            f"Reached 1 ft. Turning {angle_deg:.2f} deg for {turn_duration:.2f} s"
        )

    def _start_avoidance_turn(self):
        """Turn 90 deg: toward open side if asymmetric, random if symmetric."""
        asymmetry = abs(self.left_distance - self.right_distance)
        if asymmetry > self.SYMMETRY_THRESHOLD:
            self.avoid_turn_direction = 1.0 if self.left_distance >= self.right_distance else -1.0
        else:
            self.avoid_turn_direction = 1.0 if random.random() > 0.5 else -1.0

        turn_duration       = math.radians(90.0) / self.turn_speed
        self.is_avoiding    = True
        self.avoid_end_time = self.get_clock().now().nanoseconds * 1e-9 + turn_duration
        self.get_logger().info(
            f"Turning 90 deg {'left' if self.avoid_turn_direction > 0 else 'right'} "
            f"for {turn_duration:.2f} s"
        )

    def _start_escape(self):
        """Symmetric obstacle: back up for 1 s, then turn 90 deg."""
        self.is_escaping           = True
        self.escape_phase          = 'backing'
        self.escape_phase_end_time = self.get_clock().now().nanoseconds * 1e-9 + 1.0
        self.escape_turn_direction = 1.0 if random.random() > 0.5 else -1.0
        self.get_logger().info("Symmetric obstacle – escaping (backing up)")

    # ------------------------------------------------------------------
    # Publish helpers
    # ------------------------------------------------------------------

    def _publish_stop(self):
        cmd = TwistStamped()
        self.cmd_pub.publish(cmd)

    def _publish_forward(self):
        cmd = TwistStamped()
        cmd.twist.linear.x = self.slow_speed
        self.cmd_pub.publish(cmd)

    def _publish_backup(self):
        cmd = TwistStamped()
        cmd.twist.linear.x = self.backup_speed
        self.cmd_pub.publish(cmd)

    def _publish_turn(self, direction):
        cmd = TwistStamped()
        cmd.twist.angular.z = direction * self.turn_speed
        self.cmd_pub.publish(cmd)

    # ------------------------------------------------------------------
    # Main control loop
    # ------------------------------------------------------------------

    def control_loop(self):
        STOP_DISTANCE  = 0.1  # meters – full halt
        AVOID_DISTANCE = 0.6  # meters – turn 90 deg
        now_sec = self.get_clock().now().nanoseconds * 1e-9

        self.get_logger().info(
            f"Front:{self.front_distance:.2f}  L:{self.left_distance:.2f}  R:{self.right_distance:.2f}"
        )

        # --- Priority 1: too close – full stop ---
        if self.front_distance < STOP_DISTANCE:
            self.is_turning  = False
            self.is_avoiding = False
            self.get_logger().info(
                f"Too close ({self.front_distance:.2f} m) – full stop"
            )
            self._publish_stop()
            return

        # --- Priority 2: within avoid range – turn 90 deg ---
        if self.front_distance < AVOID_DISTANCE:
            self.is_turning  = False
            self.is_avoiding = False
            asymmetry = abs(self.left_distance - self.right_distance)
            if asymmetry > self.SYMMETRY_THRESHOLD:
                self.get_logger().info(
                    f"Asymmetric (L:{self.left_distance:.2f} R:{self.right_distance:.2f}) – turning toward open side"
                )
            else:
                self.get_logger().info(
                    f"Symmetric (L:{self.left_distance:.2f} R:{self.right_distance:.2f}) – turning 90 deg"
                )
            self._start_avoidance_turn()
            self._publish_turn(self.avoid_turn_direction)
            return

        # --- Priority 3: human teleop ---
        if self._teleop_active():
            self.is_turning  = False
            self.is_avoiding = False
            self.get_logger().info("Teleop active – forwarding human input")
            self.cmd_pub.publish(self.teleop_cmd)
            return

        # --- Priority 4: finish avoidance turn ---
        if self.is_avoiding:
            if now_sec < self.avoid_end_time:
                self._publish_turn(self.avoid_turn_direction)
            else:
                self.is_avoiding              = False
                self.forward_distance_accum   = 0.0
                self.get_logger().info("Avoidance turn complete – resuming forward drive")
                self._publish_forward()
            return

        # --- Priority 5: Behavior-5 random turn in progress ---
        if self.is_turning:
            if now_sec < self.turn_end_time:
                self._publish_turn(self.current_turn_direction)
            else:
                self.is_turning             = False
                self.forward_distance_accum = 0.0
                self.get_logger().info("Random turn complete – resuming forward drive")
                self._publish_forward()
            return

        # --- Priority 6: autonomous forward drive ---
        self.forward_distance_accum += self.slow_speed * self.timer_period
        if self.forward_distance_accum >= self.ONE_FOOT_M:
            self._start_random_turn()
            self._publish_turn(self.current_turn_direction)
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
