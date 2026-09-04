#!/bin/bash

APP_FILE="main_agent.py"
LOG_FILE="agent.log"
PID_FILE="agent.pid"

start_agent() {
    if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
        echo "⚠️ Agent is already running (PID: $(cat $PID_FILE))."
    else
        nohup python $APP_FILE > $LOG_FILE 2>&1 &
        echo $! > $PID_FILE
        echo "✅ Smart Agent started in background (PID: $!). Logs written to $LOG_FILE."
    fi
}

stop_agent() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        kill $PID 2>/dev/null
        rm -f "$PID_FILE"
        echo "🛑 Smart Agent stopped (PID: $PID)."
    else
        echo "⚠️ No running agent PID file found."
    fi
}

status_agent() {
    if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
        echo "🟢 Agent is RUNNING (PID: $(cat $PID_FILE))."
    else
        echo "🔴 Agent is STOPPED."
    fi
}

case "$1" in
    start)
        start_agent
        ;;
    stop)
        stop_agent
        ;;
    status)
        status_agent
        ;;
    *)
        echo "Usage: $0 {start|stop|status}"
        exit 1
esac

