cd ros2_ws
colcon build --packages-select reactive_robot
source install/setup.bash
ros2 launch reactive_robot project2.launch.xml robot_name:=YOUR_ROBOT_NAME