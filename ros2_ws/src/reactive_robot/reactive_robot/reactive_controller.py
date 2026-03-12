import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
from std_msgs.msg import String
import random

class ReactiveController(Node):

    def __init__(self):
        super().__init__('reactive_controller')

        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)

        self.scan_sub = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            10
        )

        self.timer = self.create_timer(0.1, self.control_loop)

        self.front_distance = float('inf')

    def scan_callback(self, msg):
        self.front_distance = min(msg.ranges)

    def control_loop(self):

        cmd = Twist()

        if self.front_distance < 0.3:
            cmd.angular.z = 0.5
        else:
            cmd.linear.x = 0.1

        self.cmd_pub.publish(cmd)


def main(args=None):

    rclpy.init(args=args)

    node = ReactiveController()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
