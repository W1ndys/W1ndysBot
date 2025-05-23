#!/bin/bash
dos2unix "$0"
# 进入当前目录的app目录
cd "$(dirname "$0")/app"

# 检查应用是否正在运行
if [ -f "app.pid" ]; then
    PID=$(cat app.pid)
    if ps -p $PID > /dev/null; then
        echo "正在停止应用 (PID: $PID)"
        kill $PID
        # 等待进程结束
        sleep 2
        if ps -p $PID > /dev/null; then
            echo "应用未能正常停止，强制终止中..."
            kill -9 $PID
            sleep 1
        fi
        echo "应用已成功停止"
    else
        echo "应用不在运行状态，但pid文件存在，将清理pid文件"
    fi
    rm -f app.pid
    echo "已删除PID文件"
else
    echo "没有找到pid文件，应用可能没有在运行"
fi