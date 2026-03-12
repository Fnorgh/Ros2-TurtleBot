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

echo "=== Stopping LiDAR on all TurtleBots ==="
echo ""

for ROBOT in "${ROBOTS[@]}"; do
    HOST="student@${ROBOT}.cs.nor.ou.edu"
    echo "[$ROBOT] Connecting to $HOST ..."

    # bash --login sources the robot's profile so ros2 is on PATH.
    # Command is a single-quoted argument — no heredoc, no stdin conflict with sshpass.
    sshpass -p "$PASSWORD" \
        ssh -o StrictHostKeyChecking=accept-new \
            -o StrictHostKeyChecking=accept-new \
            -o BatchMode=no \
            -o ConnectTimeout=5 \
            "$HOST" \
            'bash --login -c "ros2 service call /stop_motor std_srvs/srv/Empty {}"'

    if [ $? -eq 0 ]; then
        echo "[$ROBOT] LiDAR stopped."
    else
        echo "[$ROBOT] FAILED – check output above for details."
    fi
    echo ""
done

echo "=== Done. Return all robots to their charging docks. ==="
