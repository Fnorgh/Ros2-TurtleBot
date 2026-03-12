#!/usr/bin/env bash
# shutdown_robot.sh
# Safely shuts down TurtleBot 4 peripherals before docking.
# Usage: ./shutdown_robot.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WS_DIR="$SCRIPT_DIR/ros2_ws"

# ── Prompt for robot name ────────────────────────────────────────────────────
read -rp "Enter TurtleBot name (printed on the robot): " ROBOT_NAME
if [[ -z "$ROBOT_NAME" ]]; then
    echo "ERROR: Robot name cannot be empty." >&2
    exit 1
fi

echo ""
echo "=== TurtleBot 4 Shutdown: $ROBOT_NAME ==="
echo ""

# ── Source workspace and connect via robot-setup.sh ─────────────────────────
cd "$WS_DIR"
echo "Sourcing install/setup.bash ..."
source install/setup.bash 2>/dev/null || true

echo "Running robot-setup.sh ..."
printf '%s\n' "${ROBOT_NAME}" | robot-setup.sh

echo ""

# ── Stop LiDAR motor ─────────────────────────────────────────────────────────
# Must be stopped before placing robot on charging dock (per OU_turtlebots4.pdf)
echo "Stopping LiDAR motor ..."
ros2 service call /stop_motor std_srvs/srv/Empty "{}"
echo "LiDAR motor stopped."

echo ""

# ── Stop ROS 2 daemon ────────────────────────────────────────────────────────
echo "Stopping ROS 2 daemon ..."
ros2 daemon stop
echo "ROS 2 daemon stopped."

echo ""
echo "======================================================"
echo "  Shutdown complete. Safe to dock the robot."
echo ""
echo "  REMINDER: Return the robot to its charging dock."
echo "  Lift the BASE with both hands — never by sensors"
echo "  or the tower. Do NOT place on elevated surfaces."
echo "======================================================"
