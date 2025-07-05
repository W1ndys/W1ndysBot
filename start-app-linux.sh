#!/bin/bash

# 进入当前目录的app目录
cd "$(dirname "$0")/app"

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

# 后台运行Python程序并保存PID - 只记录错误输出到日志
nohup python3 main.py >/dev/null 2>app.log &

# 保存PID到文件
echo $! >app.pid

echo "Python程序已在虚拟环境中启动，PID保存在app/app.pid中"
echo "仅错误输出将记录到app.log文件中"

# 退出虚拟环境
if [ -n "$VIRTUAL_ENV" ]; then
    deactivate
fi