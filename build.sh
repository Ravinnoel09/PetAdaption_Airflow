#!/bin/bash

# Path to your ETL runner script
RUNNER_SCRIPT="/home/dharshan/web-projects/apacheairflow-ravin/background_etl_runner.py"
# Path to your Python interpreter
PYTHON="/home/dharshan/web-projects/apacheairflow-ravin/etl/bin/python3"
# PID file to track the process
PID_FILE="/home/dharshan/web-projects/apacheairflow-ravin/etl_runner.pid"

start() {
    if [ -f $PID_FILE ]; then
        echo "ETL runner is already running (PID: $(cat $PID_FILE))"
    else
        echo "Starting ETL runner..."
        nohup $PYTHON $RUNNER_SCRIPT > nohup.out 2>&1 &
        echo $! > $PID_FILE
        echo "ETL runner started with PID: $!"
    fi
}

stop() {
    if [ -f $PID_FILE ]; then
        PID=$(cat $PID_FILE)
        echo "Stopping ETL runner process (PID: $PID)..."
        kill $PID
        rm $PID_FILE
        echo "ETL runner stopped"
    else
        echo "ETL runner is not running"
    fi
}

status() {
    if [ -f $PID_FILE ]; then
        PID=$(cat $PID_FILE)
        if ps -p $PID > /dev/null; then
            echo "ETL runner is running with PID: $PID"
        else
            echo "ETL runner is not running but PID file exists"
            rm $PID_FILE
        fi
    else
        echo "ETL runner is not running"
    fi
}

case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        stop
        start
        ;;
    status)
        status
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac