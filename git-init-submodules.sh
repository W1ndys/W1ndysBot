#!/bin/bash

# 设置输出颜色
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}开始初始化所有子模块...${NC}"

# 初始化并更新所有子模块（包括嵌套的子模块）
git submodule update --init --recursive

echo -e "${BLUE}正在更新所有子模块到最新版本...${NC}"
# 更新所有子模块到最新版本
git submodule update --remote --merge

echo -e "${GREEN}✅ 所有子模块初始化和更新完成！${NC}"

# 暂停两秒
sleep 2 