#!/bin/bash

VENV_DIR=".venv"
PYTHON_APP="main.py"
LOG_FILE="output.log"
PID_FILE="app.pid"

# 显示帮助信息
show_help() {
    echo -e "\033[1mUsage: $0 {start|stop|status|restart|help}\033[0m"
    echo -e "\n\033[1mCommands:\033[0m"
    echo -e "  start    Start the application (with virtual environment and logging)."
    echo -e "  stop     Stop the application (based on PID stored in $PID_FILE)."
    echo -e "  status   Check if the application is running (based on PID file)."
    echo -e "  restart  Stop and then start the application."
    echo -e "  help     Display this help message.\n"
    echo -e "\033[1mEnvironment:\033[0m"
    echo -e "  VENV_DIR     The directory for the Python virtual environment (default: .venv)."
    echo -e "  PYTHON_APP   The Python application to run (default: main.py)."
    echo -e "  LOG_FILE     The log file where the output is stored (default: output.log)."
    echo -e "  PID_FILE     The file where the PID of the application is stored (default: app.pid).\n"
    echo -e "Make sure to set up your Python virtual environment before running the script.\n"
}

# 检查Python3是否可用
check_python() {
    if ! command -v python3 &> /dev/null; then
        echo -e "\033[31mError: Python3 is not installed or not found in PATH.\033[0m"
        exit 1
    fi
}

# 启动应用
start_app() {
    if [ ! -d "$VENV_DIR" ]; then
        echo -e "\033[31mError: Virtual environment directory $VENV_DIR not found! \033[0m"
        exit 1
    fi

    if [ ! -f "$PYTHON_APP" ]; then
        echo -e "\033[31mError: Python application $PYTHON_APP not found! \033[0m"
        exit 1
    fi

    # 激活虚拟环境
    source "$VENV_DIR/bin/activate"

    # 检查Python是否正确安装
    check_python

    # 启动应用并将输出重定向到日志文件
    nohup python3 "$PYTHON_APP" > "$LOG_FILE" 2>&1 &
    echo $! > "$PID_FILE"
    echo -e "\033[32mApplication started! Logs are being written to $LOG_FILE\033[0m"
}

# 停止应用
stop_app() {
    if [ ! -f "$PID_FILE" ]; then
        echo -e "\033[31mError: PID file $PID_FILE not found! \033[0m"
        exit 1
    fi

    pid=$(cat "$PID_FILE")
    if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
        kill "$pid"
        rm "$PID_FILE"
        echo -e "\033[32mApplication stopped!\033[0m"
    else
        echo -e "\033[31mError: Application not running or PID not found! \033[0m"
    fi
}

# 检查应用状态
check_app_status() {
    if [ ! -f "$PID_FILE" ]; then
        echo -e "\033[31mError: Application not running! No PID file found.\033[0m"
        exit 1
    fi

    pid=$(cat "$PID_FILE")
    if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
        echo -e "PID: $pid"
        echo -e "\033[32mApplication is running.\033[0m"
    else
        echo -e "\033[31mError: Application not running. PID not found or process not running.\033[0m"
    fi
}

# 重启应用
restart_app() {
    stop_app
    start_app
    echo -e "\033[32mApplication restarted!\033[0m"
}

# 处理命令行参数
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
    help)
        show_help
        ;;
    *)
        echo -e "\033[33mInvalid command.\033[0m"
        show_help
        exit 1
        ;;
esac
