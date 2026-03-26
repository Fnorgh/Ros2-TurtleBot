#!/usr/bin/env bash
# launch_robot.sh
# Opens all terminals needed for Project 2 TurtleBot 4 operation.
# Usage: ./launch_robot.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WS_DIR="$SCRIPT_DIR/ros2_ws"

# ── Prompt for robot name ────────────────────────────────────────────────────
read -rp "Enter TurtleBot name (printed on the robot): " ROBOT_NAME
if [[ -z "$ROBOT_NAME" ]]; then
    echo "ERROR: Robot name cannot be empty." >&2
    exit 1
fi

ROBOT_HOST="student@${ROBOT_NAME}.cs.nor.ou.edu"

echo ""
echo "Opening terminals for robot: $ROBOT_NAME"
echo "Workspace: $WS_DIR"
echo ""

# ── Helper: open a gnome-terminal tab with a title and command ────────────────
# Usage: open_tab "TITLE" "BASH_COMMANDS"
open_tab() {
    local title="$1"
    local cmd="$2"
    gnome-terminal \
        --title="$title" \
        -- bash -c "$cmd; exec bash" &
    sleep 0.4   # small delay so windows open in a visible order
}

# ── Terminal 1: SSH into the Robot ───────────────────────────────────────────
# Log in, verify /scan /tf /odom are published, start LiDAR motor.
open_tab "TB4 – Robot SSH" "
echo '=== TurtleBot 4 SSH Terminal ==='
echo 'SSHing into ${ROBOT_HOST} ...'
echo ''
echo 'Once logged in:'
echo '  1. Run:  ros2 topic list'
echo '     Verify /scan, /tf, and /odom are present.'
echo '  2. If they are missing run:  turtlebot4-daemon-restart'
echo '     Then run ros2 topic list again.'
echo '  3. Start LiDAR motor:'
echo '     ros2 service call /start_motor std_srvs/srv/Empty \"{}\"'
echo ''
ssh -o StrictHostKeyChecking=accept-new ${ROBOT_HOST}
"

# ── Terminal 2: Build & Run reactive_controller ──────────────────────────────
# Sources workspace, runs robot-setup.sh, builds the package, then launches.
open_tab "TB4 – Reactive Controller" "
echo '=== Reactive Controller Terminal ==='
echo ''
cd \"$WS_DIR\"
echo 'Sourcing install/setup.bash ...'
source install/setup.bash 2>/dev/null || true
echo ''
echo 'Running robot-setup.sh ...'
printf '%s\n' "${ROBOT_NAME}" | robot-setup.sh
echo ''
echo 'Building reactive_robot package ...'
colcon build --packages-select reactive_robot
echo ''
echo 'Sourcing install/setup.bash after build ...'
source install/setup.bash
echo ''
echo 'Launching reactive_controller ...'
ros2 run reactive_robot reactive_controller
"

# ── Terminal 3: Keyboard Teleoperation ───────────────────────────────────────
open_tab "TB4 – Teleop Keyboard" "
echo '=== Keyboard Teleoperation Terminal ==='
echo ''
cd \"$WS_DIR\"
echo 'Sourcing install/setup.bash ...'
source install/setup.bash 2>/dev/null || true
echo ''
echo 'Running robot-setup.sh ...'
printf '%s\n' "${ROBOT_NAME}" | robot-setup.sh
echo ''
echo 'Starting teleop_twist_keyboard (use conservative speeds: speed=0.1 turn=0.2) ...'
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -p stamped:=true --remap /cmd_vel:=/teleop_cmd_vel
"

# ── Terminal 4: SLAM Mapping ────────────────────────────────────────────────
open_tab "TB4 – SLAM Mapping" "
echo '=== SLAM Mapping Terminal ==='
echo ''
cd \"$WS_DIR\"
echo 'Sourcing install/setup.bash ...'
source install/setup.bash 2>/dev/null || true
echo ''
echo 'Running robot-setup.sh ...'
printf '%s\n' "${ROBOT_NAME}" | robot-setup.sh
echo ''
echo 'Launching TurtleBot4 SLAM ...'
echo ''
echo 'Drive the robot from the teleop terminal while the reactive controller stays running.'
echo ''
ros2 launch turtlebot4_navigation slam.launch.py
"

# ── Terminal 5: RViz Visualization ──────────────────────────────────────────
open_tab "TB4 – RViz" "
echo '=== RViz Visualization Terminal ==='
echo ''
cd \"$WS_DIR\"
echo 'Sourcing install/setup.bash ...'
source install/setup.bash 2>/dev/null || true
echo ''
echo 'Running robot-setup.sh ...'
printf '%s\n' "${ROBOT_NAME}" | robot-setup.sh
echo ''
echo 'Launching RViz2 (view_robot) ...'
echo ''
echo 'Configure RViz like this:'
echo '  1. Set Fixed Frame to: odom'
echo '  2. Add TF display'
echo '     - Uncheck All Enabled'
echo '     - Enable only: odom'
echo '  3. Add RobotModel display'
echo '     - Description Topic: /robot_description'
echo '  4. Add LaserScan display'
echo '     - Topic: /scan'
echo '  5. Add Map display'
echo '     - Topic: /map'
echo '  6. Optional: Add PointCloud2 display'
echo '     - Topic: /oakd/rgb/preview/depth/points'
echo '  7. Optional: enable oakd_rgb_camera_optical_frame in TF'
echo ''
ros2 launch turtlebot4_viz view_robot.launch.py
"

echo ""
echo "All terminals launched."
echo ""
echo "Order of operations:"
echo "  1. Terminal 1 (SSH): verify /scan /tf /odom, start LiDAR motor"
echo "  2. Terminal 2 (Reactive Controller): run robot-setup.sh, build, then run"
echo "  3. Terminal 4 (SLAM Mapping): launch slam.launch.py"
echo "  4. Terminal 5 (RViz): launch view_robot.launch.py and configure displays"
echo "  5. Terminal 3 (Teleop): drive the robot for mapping"
echo "  6. When finished, save the map from a sourced desktop terminal:"
echo "     ros2 run nav2_map_server map_saver_cli -f ~/tb4_map"
