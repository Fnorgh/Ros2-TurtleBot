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
    testudo
)

PASSWORD="student"

echo "=== Stopping LiDAR on all TurtleBots ==="
echo ""

for ROBOT in "${ROBOTS[@]}"; do
    HOST="student@${ROBOT}.cs.nor.ou.edu"
    echo "[$ROBOT] Connecting to $HOST ..."

    # Single-quoted shell command inside Tcl braces so remote bash
    # sees it correctly. ROS2 is sourced explicitly since the login
    # profile on the robot does not set it up automatically.
    expect -c "
        set timeout 30
        spawn ssh -o StrictHostKeyChecking=accept-new -o ConnectTimeout=5 -tt $HOST
        expect {
            \"yes/no\"    { send \"yes\r\";       exp_continue }
            \"password:\" { send \"$PASSWORD\r\"; exp_continue }
            \"\\\$\"      { }
        }
        send \"robot-setup.sh\r\"
        expect \"\\\$\"
        send \"ros2 service call /stop_motor std_srvs/srv/Empty \\\"{}\\\"\r\"
        expect \"\\\$\"
        send \"exit\r\"
        expect eof
    "

    if [ $? -eq 0 ]; then
        echo "[$ROBOT] LiDAR stopped."
    else
        echo "[$ROBOT] FAILED – check output above for details."
    fi
    echo ""
done

echo "=== Done. Return all robots to their charging docks. ==="
