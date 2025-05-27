#!/bin/bash

# 设置颜色输出
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "开始安装依赖..."

# 检查 pnpm 是否已安装
if ! command -v pnpm &> /dev/null; then
    echo -e "${RED}错误: pnpm 未安装${NC}"
    echo "正在尝试安装 pnpm..."
    # 使用 npm 安装 pnpm
    npm install -g pnpm
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}pnpm 安装失败，请手动安装 pnpm${NC}"
        exit 1
    fi
fi

# 执行 pnpm install
echo "执行 pnpm install..."
pnpm install

# 检查安装结果
if [ $? -eq 0 ]; then
    echo -e "${GREEN}依赖安装成功！${NC}"
else
    echo -e "${RED}依赖安装失败，请检查错误信息${NC}"
    exit 1
fi 