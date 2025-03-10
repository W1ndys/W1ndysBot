#!/bin/bash

# 进入当前目录的app目录
cd "$(dirname "$0")/app"

# 检查PID文件是否存在
if [ -f app.pid ]; then
    # 读取PID
    PID=$(cat app.pid)

    # 检查进程是否存在
    if ps -p $PID >/dev/null; then
        echo "杀死进程 $PID"
        kill $PID
    else
        echo "进程 $PID 不存在，直接启动新进程"
    fi

    # 删除PID文件
    rm app.pid
else
    echo "PID文件不存在，直接启动新进程"
fi

# 激活虚拟环境
. "../venv/bin/activate"

# 启动Python程序
nohup python main.py >app.log 2>&1 &

# 保存新的PID到文件
echo $! >app.pid

echo "Python程序已在虚拟环境中启动，新的PID保存在app/app.pid中"
