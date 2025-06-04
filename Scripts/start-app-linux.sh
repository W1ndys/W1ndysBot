#!/bin/bash
# 进入当前目录
cd "$(dirname "$0")"
# 进入上一级目录
cd ..
# 进入app目录
cd app

# 激活虚拟环境
source "../venv/bin/activate"

# 后台运行Python程序并保存PID
nohup python main.py >app.log 2>&1 &

# 保存PID到文件
echo $! >app.pid

echo "Python程序已在虚拟环境中启动，PID保存在app/app.pid中"

# 退出虚拟环境
deactivate