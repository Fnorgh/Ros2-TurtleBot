from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():

    reactive_node = Node(
        package='reactive_robot',
        executable='reactive_controller',
        name='reactive_controller',
        output='screen'
    )

    return LaunchDescription([
        reactive_node
    ])
