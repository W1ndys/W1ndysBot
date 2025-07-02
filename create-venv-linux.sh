#!/bin/bash

# 检查uv是否安装
if ! which uv > /dev/null 2>&1
then
    echo "uv 未安装，正在安装 uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    # 重新加载环境变量
    export PATH="$HOME/.cargo/bin:$PATH"
    
    # 再次检查uv是否安装成功
    if ! which uv > /dev/null 2>&1
    then
        echo "uv 安装失败，请手动安装 uv。"
        exit 1
    fi
fi

# 使用uv创建虚拟环境
echo "正在使用 uv 创建虚拟环境..."
uv venv

# 激活虚拟环境
. venv/bin/activate

# 使用uv安装requirements.txt中的包
if [ -f "requirements.txt" ]; then
    echo "正在使用 uv 安装依赖包..."
    uv pip install -r requirements.txt
else
    echo "requirements.txt 文件不存在，请确保该文件存在于当前目录。"
fi

echo "虚拟环境已创建并使用 uv 安装了所需的包。" 