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

echo "在前台启动Python程序..."
# 前台运行Python程序，可以直接观察输出
python3 main.py

# 退出虚拟环境
if [ -n "$VIRTUAL_ENV" ]; then
    deactivate
fi