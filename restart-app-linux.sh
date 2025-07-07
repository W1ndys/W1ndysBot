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

# 后台运行新的Python程序并保存PID - 只记录错误输出到日志
echo "启动新的应用实例..."
nohup python3 main.py >/dev/null 2>app.log &

# 保存新进程的PID到文件
NEW_PID=$!
echo $NEW_PID >app.pid

echo "新的Python程序已启动，PID: $NEW_PID"

# 如果有旧进程在运行，等待5秒后停止旧进程
if [ -n "$OLD_PID" ]; then
    echo "等待1秒后停止旧应用..."
    sleep 1
    
    if ps -p $OLD_PID > /dev/null; then
        echo "停止旧应用 (PID: $OLD_PID)"
        kill $OLD_PID
        
        # 等待1秒检查是否正常退出
        sleep 1
        if ps -p $OLD_PID > /dev/null; then
            echo "旧应用未能正常停止，强制终止中..."
            kill -9 $OLD_PID
        fi
        echo "旧应用已停止"
    else
        echo "旧应用已经停止"
    fi
fi

echo "应用重启完成，新PID保存在app/app.pid中"
echo "仅错误输出将记录到app.log文件中"

# 退出虚拟环境
if [ -n "$VIRTUAL_ENV" ]; then
    deactivate
fi