# Ros2-TurtleBot

## Connect to robot
From CSN machine:
```bash
ssh student@<nameFromRobot>.cs.nor.ou.edu
```
Enter the password, then run:
```bash
ros2 topic list
```
If topics `/scan`, `/tf`, and `/odom` are not listed, run:
```bash
turtlebot4-daemon-restart
```
Check again to see if these topics are listed now.

## Set up terminal
**Every time you open a new desktop terminal, start from `ros2_ws/` and run:**
```bash
source install/setup.bash
robot-setup.sh
```
Follow the instructions it prints.

## Control the robot
From desktop terminal, run:
```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -p stamped:=true
```

## Run the reactive controller
If opening a new terminal, start from `ros2_ws/` and run:
```bash
source install/setup.bash
robot-setup.sh
```
Follow the instructions it prints.



Build the project:
```bash
colcon build --packages-select reactive_robot
```

Run `reactive_controller.py`:
```bash
ros2 run reactive_robot reactive_controller
```
