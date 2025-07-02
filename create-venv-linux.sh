#!/bin/bash

# 检查Python是否安装
if ! which python3 > /dev/null 2>&1
then
    echo "Python3 未安装，请先安装 Python3。"
    exit 1
fi

# 检查uv是否安装
if ! which uv > /dev/null 2>&1
then
    echo "uv 未安装，正在使用 pip 安装 uv..."
    python3 -m pip install uv
    
    # 再次检查uv是否安装成功
    if ! which uv > /dev/null 2>&1
    then
        echo "uv 安装失败，请检查 pip 是否正常工作。"
        exit 1
    fi
fi

# 使用uv创建虚拟环境
echo "正在使用 uv 创建虚拟环境..."
uv venv

# 激活虚拟环境
source .venv/bin/activate

# 使用uv安装requirements.txt中的包
if [ -f "requirements.txt" ]; then
    echo "正在使用 uv 安装依赖包..."
    uv pip install -r requirements.txt
else
    echo "requirements.txt 文件不存在，请确保该文件存在于当前目录。"
fi

echo "虚拟环境已创建并使用 uv 安装了所需的包。" 