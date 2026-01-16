#!/usr/bin/env bash

MAX_TEMP=85

# Get the directory where the script is located and move to project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR/.." || exit 1

while true; do
    # Orin Nano temperature (CPU)
    TEMP=$(( $(cat /sys/devices/virtual/thermal/thermal_zone0/temp) / 1000 ))

    echo "Temp: ${TEMP}C"

    if [ "$TEMP" -ge "$MAX_TEMP" ]; then
        echo "Temperature above ${MAX_TEMP}C — shutting down."
        sudo shutdown -h now
        exit 0
    fi

    # Start Vector in background if not already running
    if ! pgrep -x "vector" > /dev/null; then
        echo "Starting Vector..."
        vector --config vector.toml &
    fi

    # Start Uploader Service
    echo "Starting Upload Worker..."
    python3 uploader/upload_worker.py &
    UPLOADER_PID=$!

    # Your app
    python3 -m runners.jetson_prod_runner_multi
    EXIT_CODE=$?

    # Stop Uploader Service
    echo "Stopping Upload Worker (PID $UPLOADER_PID)..."
    kill $UPLOADER_PID

    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S,%3N')
    LOG_MSG="${TIMESTAMP} - shell-monitor - CRITICAL - Process exited with code ${EXIT_CODE}. Restarting in 5 seconds..."
    
    # Log to stdout
    echo "$LOG_MSG"
    
    # Log to file (ensure directory exists)
    mkdir -p data/logs
    echo "$LOG_MSG" >> data/logs/app.log

    sleep 5
done
