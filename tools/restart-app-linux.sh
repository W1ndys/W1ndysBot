#!/bin/bash

# 进入当前目录
cd "$(dirname "$0")"
# 进入上一级目录
cd ..
# 进入app目录
cd app

# 检查应用是否正在运行
if [ -f "app.pid" ]; then
    PID=$(cat app.pid)
    if ps -p $PID > /dev/null; then
        echo "停止正在运行的应用 (PID: $PID)"
        kill $PID
        if ps -p $PID > /dev/null; then
            echo "应用未能正常停止，强制终止中..."
            kill -9 $PID
        fi
    else
        echo "应用不在运行状态，但pid文件存在，将清理pid文件"
    fi
    rm -f app.pid
else
    echo "没有找到pid文件，应用可能没有在运行"
fi

# 激活虚拟环境
source "../venv/bin/activate"

# 后台运行Python程序并保存PID
echo "重新启动应用..."
nohup python main.py >app.log 2>&1 &

# 保存PID到文件
echo $! >app.pid

echo "Python程序已在虚拟环境中重新启动，PID保存在app/app.pid中"

# 退出虚拟环境
deactivate 