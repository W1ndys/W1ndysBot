#!/bin/bash
cd "$(dirname "$0")"
cd ..

# 检查Python是否安装
if ! which python3 > /dev/null 2>&1
then
    echo "Python3 未安装，请先安装 Python3。"
    exit 1
fi

# 检查是否已安装 python3-venv
if ! dpkg -l | grep -q python3-venv; then
    echo "正在安装 python3-venv..."
    apt install -y python3-venv
    if [ $? -ne 0 ]; then
        echo "安装 python3-venv 失败，请使用 sudo 权限运行此脚本。"
        exit 1
    fi
fi

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
. venv/bin/activate

# 配置pip使用清华镜像源
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# 升级pip
pip install --upgrade pip

# 安装requirements.txt中的包
if [ -f "requirements.txt" ]; then
    echo "正在从清华镜像源安装依赖包..."
    pip install -r requirements.txt
else
    echo "requirements.txt 文件不存在，请确保该文件存在于当前目录。"
fi

echo "虚拟环境已创建并安装了所需的pip包。" 