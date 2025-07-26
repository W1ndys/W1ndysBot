#!/bin/bash

# 在出错时停止脚本执行
set -e

# 进入当前目录的app目录
cd "$(dirname "$0")/app"

# 保存旧进程的PID
OLD_PID=""
if [ -f "app.pid" ]; then
    OLD_PID=$(cat app.pid)
    if ps -p $OLD_PID > /dev/null; then
        echo "发现正在运行的应用 (PID: $OLD_PID)，将在新应用启动后停止"
    else
        echo "应用不在运行状态，但pid文件存在，将清理pid文件"
        rm -f app.pid
        OLD_PID=""
    fi
else
    echo "没有找到pid文件，应用可能没有在运行"
fi

# 激活虚拟环境 - 优先检查uv创建的.venv目录
if [ -f "../.venv/bin/activate" ]; then
    echo "激活 uv 虚拟环境..."
    source "../.venv/bin/activate"
elif [ -f "../venv/bin/activate" ]; then
    echo "激活传统虚拟环境..."
    source "../venv/bin/activate"
else
    echo "未找到虚拟环境，使用系统 Python。"
fi

# 创建logs目录（如果不存在）
mkdir -p logs

# 生成带时间戳的日志文件名
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
LOG_FILE="logs/app_${TIMESTAMP}.log"

# 后台运行新的Python程序并保存PID - 记录所有输出到带时间戳的日志文件
echo "启动新的应用实例，日志将保存到 $LOG_FILE ..."
nohup python3 main.py >"$LOG_FILE" 2>&1 &

# 保存新进程的PID到文件
NEW_PID=$!
echo $NEW_PID >app.pid

echo "新的Python程序已启动，PID: $NEW_PID"

# 如果有旧进程在运行，等待5秒后停止旧进程
if [ -n "$OLD_PID" ]; then
    echo "等待0.5秒后停止旧应用..."
    sleep 0.5
    
    if ps -p $OLD_PID > /dev/null; then
        echo "停止旧应用 (PID: $OLD_PID)"
        kill $OLD_PID
        
        # 等待0.5秒检查是否正常退出
        sleep 0.5
        if ps -p $OLD_PID > /dev/null; then
            echo "旧应用未能正常停止，强制终止中..."
            kill -9 $OLD_PID
        fi
        echo "旧应用已停止"
    else
        echo "旧应用已经停止"
    fi
fi

# 创建最新日志的软链接，方便查看
ln -sf "app_${TIMESTAMP}.log" logs/latest.log

echo "应用重启完成，新PID保存在app/app.pid中"
echo "所有输出将记录到 $LOG_FILE 文件中"
echo "可通过 tail -f logs/latest.log 查看最新日志"

# 清理7天前的日志文件
find logs -name "app_*.log" -mtime +7 -delete 2>/dev/null || true

# 退出虚拟环境
if [ -n "$VIRTUAL_ENV" ]; then
    deactivate
fi