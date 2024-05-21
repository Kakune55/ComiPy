#!/bin/bash

VENV_DIR=".venv"
PYTHON_APP="main.py"
LOG_FILE="output.log"
PID_FILE="app.pid"

start_app() {
    if [ ! -d "$VENV_DIR" ]; then
        echo -e "\033[31m Virtual environment directory $VENV_DIR not found! \033[0m"
        exit 1
    fi

    if [ ! -f "$PYTHON_APP" ]; then
        echo -e "\033[31m Python application $PYTHON_APP not found! \033[0m"
        exit 1
    fi

    source "$VENV_DIR/bin/activate"
    nohup python3 "$PYTHON_APP" > "$LOG_FILE" 2>&1 &
    echo $! > "$PID_FILE"
    echo -e "\033[32m Application started! \033[0m"
}

stop_app() {
    if [ ! -f "$PID_FILE" ]; then
        echo -e "\033[31m PID file not found! \033[0m"
        exit 1
    fi

    pid=$(cat "$PID_FILE")
    if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
        kill "$pid"
        rm "$PID_FILE"
        echo -e "\033[32m Application ended! \033[0m"
    else
        echo -e "\033[31m Application not running or PID not found! \033[0m"
    fi
}

check_app_status() {
    if [ ! -f "$PID_FILE" ]; then
        echo -e "\033[31m Application not running! \033[0m"
        exit 1
    fi

    pid=$(cat "$PID_FILE")
    if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
        echo -e "PID: $pid"
        echo -e "\033[32m Application running! \033[0m"
    else
        echo -e "\033[31m Application not running! \033[0m"
    fi
}

restart_app() {
    stop_app
    start_app
    echo -e "\033[32m Application restarted! \033[0m"
}

case "$1" in
    start)
        start_app
        ;;
    stop)
        stop_app
        ;;
    status)
        check_app_status
        ;;
    restart)
        restart_app
        ;;
    *)
        echo -e "\033[33m Usage: $0 {start|stop|status|restart} \033[0m"
        exit 1
        ;;
esac
