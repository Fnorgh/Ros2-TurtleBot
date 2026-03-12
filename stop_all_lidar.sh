#!/usr/bin/env bash
# stop_all_lidar.sh
# Stops the LiDAR motor on every OU TurtleBot 4 via SSH.
# Usage: ./stop_all_lidar.sh

ROBOTS=(
    loggerhead
    galapagos
    leatherback
    snapper
    hawksbill
    matamata
)

PASSWORD="student"
# Source ROS 2 before the service call so ros2 is on PATH in non-interactive SSH sessions.
# Tries jazzy (Ubuntu 24.04) then humble (22.04) as fallback.
STOP_CMD='for d in /opt/ros/jazzy /opt/ros/humble; do [ -f "$d/setup.bash" ] && source "$d/setup.bash" && break; done && ros2 service call /stop_motor std_srvs/srv/Empty "{}"'

echo "=== Stopping LiDAR on all TurtleBots ==="
echo ""

for ROBOT in "${ROBOTS[@]}"; do
    HOST="student@${ROBOT}.cs.nor.ou.edu"
    echo "[$ROBOT] Connecting to $HOST ..."
    sshpass -p "$PASSWORD" \
        ssh -o StrictHostKeyChecking=accept-new \
            -o ConnectTimeout=5 \
            "$HOST" "bash -c '$STOP_CMD'" \
        && echo "[$ROBOT] LiDAR stopped." \
        || echo "[$ROBOT] FAILED – robot may be offline or unreachable."
    echo ""
done

echo "=== Done. Return all robots to their charging docks. ==="
