from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess

def generate_launch_description():

    kill_joystick = ExecuteProcess(
        cmd=['bash', '-lc', 'pkill -f teleop_twist_joy 2>/dev/null; true'],
        output='screen'
    )

    reactive_node = Node(
        package='reactive_robot',
        executable='reactive_controller',
        name='reactive_controller',
        output='screen'
    )

    return LaunchDescription([
        kill_joystick,
        reactive_node,
    ])
