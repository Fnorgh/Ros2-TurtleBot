import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TwistStamped
from sensor_msgs.msg import LaserScan

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

        self.timer = self.create_timer(0.1, self.control_loop)

        self.front_distance = float('inf')

        # Set a very slow forward speed (meters/second)
        self.slow_speed = 0.05  # adjust lower if needed

    def scan_callback(self, msg):
        # get the minimum distance in front (front 30 degrees)
        front_angles = msg.ranges[len(msg.ranges)//2 - 15: len(msg.ranges)//2 + 15]
        self.front_distance = min(front_angles)

    def control_loop(self):

        cmd = TwistStamped()

        # Stop only if something is too close (collision avoidance)
        # if self.front_distance < 0.3:
        #     cmd.linear.x = 0.0
        #     cmd.angular.z = 0.5  # turn away slowly
        # else:
        cmd.twist.linear.x = self.slow_speed  # move forward very slowly
        cmd.twist.angular.z = 0.0

        self.get_logger().info("Driving")

        self.cmd_pub.publish(cmd)


def main(args=None):

    rclpy.init(args=args)

    node = ReactiveController()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()