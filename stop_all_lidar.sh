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
STOP_CMD='ros2 service call /stop_motor std_srvs/srv/Empty "{}"'

echo "=== Stopping LiDAR on all TurtleBots ==="
echo ""

for ROBOT in "${ROBOTS[@]}"; do
    HOST="student@${ROBOT}.cs.nor.ou.edu"
    echo "[$ROBOT] Connecting to $HOST ..."
    sshpass -p "$PASSWORD" \
        ssh -o StrictHostKeyChecking=accept-new \
            -o ConnectTimeout=5 \
            "$HOST" "$STOP_CMD" \
        && echo "[$ROBOT] LiDAR stopped." \
        || echo "[$ROBOT] FAILED – robot may be offline or unreachable."
    echo ""
done

echo "=== Done. Return all robots to their charging docks. ==="
