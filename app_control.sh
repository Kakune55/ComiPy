#!/bin/bash

VENV_DIR=".venv"
PYTHON_APP="main.py"

start_app() {
    source "$VENV_DIR/bin/activate"
    nohup python3 $PYTHON_APP > output.log 2>&1 &
    echo -e "\033[32m Application started! \033[0m"
}

stop_app() {
    pid=$(ps aux | grep $PYTHON_APP | grep -v grep | awk '{print $2}')
    if [ -n "$pid" ]; then
        kill $pid
        echo -e "\033[32m Application ended! \033[0m"
    else
        echo -e "\033[31m Application not runing! \033[0m"
    fi
}

check_app_status() {
    pid=$(ps aux | grep $PYTHON_APP | grep -v grep | awk '{print $2}')
    if [ -n "$pid" ]; then
        echo -e "PID:" $pid
        echo -e "\033[32m Application runing! \033[0m"
    else
        echo -e "\033[31m Application not runing! \033[0m"
    fi
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
    *)
        echo -e "\033[33m Usage: $0 {start|stop|status}\033[0m"
        exit 1
        ;;
esac
