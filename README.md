# Ros2-TurtleBot

## Connect to robot
SSH into robot:
```bash
ssh student@<nameFromRobot>.cs.nor.ou.edu
```
Enter the password.

Check topic list:
```bash
ros2 topic list
```
If topics `/scan`, `/tf`, and `/odom` are not listed, restart the robot:
```bash
turtlebot4-daemon-restart
```
Check again to see if these topics are listed now.

This is the SSH terminal connected to the robot.

## Set up desktop terminal
**Every time you open a new desktop terminal, start from `ros2_ws/` and run:**
```bash
source install/setup.bash
robot-setup.sh
```
Follow the instructions it prints.

## Control the robot
Make sure your terminal is set up with instructions above.

From desktop terminal, run:
```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -p stamped:=true
```

## Run the reactive controller
Make sure your terminal is set up with instructions above.

From desktop terminal, build the project:
```bash
colcon build --packages-select reactive_robot
source install/setup.bash
```

From desktop terminal, run `reactive_controller.py`:
```bash
ros2 run reactive_robot reactive_controller
```

## Lidar
Start lidar:
```bash
ros2 service call /start_motor std_srvs/srv/Empty "{}"
```
Stop lidar:
```bash
ros2 service call /stop_motor std_srvs/srv/Empty "{}"
```
