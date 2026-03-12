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

    # Use bash -i so the robot's .bashrc is sourced (gives ros2 on PATH).
    # The remote script is piped via stdin to avoid all quoting issues.
    sshpass -p "$PASSWORD" \
        ssh -o StrictHostKeyChecking=accept-new \
            -o ConnectTimeout=5 \
            -T "$HOST" bash -i << 'REMOTE'
ros2 service call /stop_motor std_srvs/srv/Empty "{}"
REMOTE

    if [ $? -eq 0 ]; then
        echo "[$ROBOT] LiDAR stopped."
    else
        echo "[$ROBOT] FAILED – check output above for details."
    fi
    echo ""
done

echo "=== Done. Return all robots to their charging docks. ==="
