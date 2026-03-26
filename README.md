# Ros2-TurtleBot

## Instructions

### Connect to robot

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

### Set up desktop terminal

Make sure you're in the project workspace:

```bash
cd ros2_ws/
```

Only if you haven't built the project on this machine before, run:

```bash
colcon build --packages-select reactive_robot
```

#### Every time you open a new desktop terminal, run:

```bash
source install/setup.bash
robot-setup.sh
```

Follow the instructions it prints.

### Run the whole project (reactive controller, teleop, and RViz)

Make sure your terminal is set up with instructions above.

From desktop terminal, run:

```bash
source install/setup.bash && ros2 launch reactive_robot reactive_robot.launch.xml robot_name:=<turtlebot-name>
```

### Run teleop only

Make sure your terminal is set up with instructions above.

From desktop terminal, run:

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -p stamped:=true
```

### Run the reactive controller only

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

### Lidar

From robot SSH terminal, start lidar:

```bash
ros2 service call /start_motor std_srvs/srv/Empty "{}"
```

From robot SSH terminal, stop lidar:

```bash
ros2 service call /stop_motor std_srvs/srv/Empty "{}"
```

### Mapping

This should only ever be done while the Lidar is running.

On a desktop terminal, run this:

```bash
ros2 launch turtlebot4_navigation slam.launch.py
```

> Note: should be done after sourcing it and running `robot-setup.sh`, of course.

#### When you are finished mapping, run:

```bash
ros2 run nav2_map_server map_saver_cli -f ~/tb4_map
```

This will put the two map files in your home directory.

#### To view the map with RViz, do the following:

> Note: this is not necessary, but it gives a real-time visualization of the map.

Open a desktop terminal, source it and run `robot-setup.sh`.

Then, open RViz:

```
ros2 launch turtlebot4_viz view_robot.launch.py
```

Adjust the following settings:

1. Set `Fixed Frame` to: `odom`
2. Add `TF` display
   - Check and uncheck `All Enabled`
   - Enable only: `odom`
3. Add `RobotModel` display
   - Description Topic: /robot_description
4. Add `LaserScan` display
   - Topic: `/scan`
5. Add `Map` display
   - Topic: `/map`
6. Optional: Add `PointCloud2` display
   - Topic: `/oakd/rgb/preview/depth/points`
7. Optional: enable `oakd_rgb_camera_optical_frame` in `TF`

## Progress

### Robot Priorities

1. [x] Halt if collision(s) detected by bumper(s).
2. [x] Accept keyboard movement commands from a human user.
3. [x] Escape from (roughly) symmetric obstacles within 1ft in front of the robot.
4. [x] Avoid asymmetric obstacles within 1ft in front of the robot.
5. [x] Turn randomly (uniformly sampled within ±15°) after every 1ft forward movement.
6. [x] Drive forward.
7. [ ] Mapping

### Documentation

- [ ] Launch File
  - [ ] XML text for user
- [ ] Robot Code
  - [ ] Data Structure and Algorithm
  - [ ] Reactive Architecture Chosen
  - [ ] Reasons for Architecture
  - [ ] Particulars

### Other

- [ ] Demo between March 27th and April 2nd
- [ ] Well commented code
- [ ] Well structured code
