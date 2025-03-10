#!/bin/bash

# 设置输出颜色
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 检查当前目录是否是 Git 仓库
if [ ! -d ".git" ]; then
    echo -e "${RED}❌ 当前目录不是一个 Git 仓库。${NC}"
    exit 1
fi

echo -e "${BLUE}🔄 正在拉取主仓库的最新更改...${NC}"
git pull

echo -e "${BLUE}🔄 正在初始化子模块...${NC}"
git submodule update --init --recursive

echo -e "${BLUE}🔄 正在更新子模块到 main 分支...${NC}"
git submodule foreach 'git checkout main && git pull origin main'

echo -e "${GREEN}✅ 项目及其子模块已成功更新。${NC}"
