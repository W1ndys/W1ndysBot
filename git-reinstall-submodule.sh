#!/bin/bash

# 设置输出颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 打印步骤函数
print_step() {
    echo "----------------------------------------"
    echo "🔧 $1"
    echo "----------------------------------------"
}

# 检查是否提供了URL参数
if [ -z "$1" ]; then
    read -p "请输入SSH仓库URL (格式: git@github.com:用户名/仓库名.git): " REPO_URL
else
    REPO_URL="$1"
fi

# 验证是否为SSH格式
if [[ ! $REPO_URL =~ ^git@github\.com:.+\.git$ ]]; then
    echo -e "${RED}❌ 错误: 请使用SSH格式的URL (例如: git@github.com:用户名/仓库名.git)${NC}"
    exit 1
fi

# 提取仓库名称
REPO_NAME=$(basename "${REPO_URL}" .git)
SUBMODULE_PATH="app/scripts/${REPO_NAME}"

print_step "开始重装子模块: $SUBMODULE_PATH"

# 1. 检查子模块是否存在
if [ ! -f ".gitmodules" ]; then
    echo -e "${YELLOW}⚠️ .gitmodules 文件不存在，直接进行安装${NC}"
else
    # 删除子模块的步骤
    print_step "1. 删除现有子模块"
    
    # 从 .git/config 中删除子模块配置
    git submodule deinit -f "$SUBMODULE_PATH"
    
    # 从工作区和索引中删除子模块
    git rm -f "$SUBMODULE_PATH" 2>/dev/null || true
    
    # 删除 .git/modules 中的子模块目录
    rm -rf ".git/modules/$SUBMODULE_PATH"
    
    # 清理可能存在的空目录
    if [ -d "$SUBMODULE_PATH" ]; then
        rm -rf "$SUBMODULE_PATH"
    fi
fi

# 2. 添加新的子模块
print_step "2. 添加新的子模块"
echo "使用的SSH URL: ${REPO_URL}"
git submodule add -b main "${REPO_URL}" "${SUBMODULE_PATH}"

# 3. 验证安装
print_step "3. 验证安装"
if [ -d "$SUBMODULE_PATH" ] && [ -f "$SUBMODULE_PATH/.git" ]; then
    echo -e "${GREEN}✅ 子模块重装成功${NC}"
else
    echo -e "${RED}❌ 子模块重装可能存在问题，请检查${NC}"
fi

print_step "重装完成"
echo -e "${GREEN}🎉 子模块 $SUBMODULE_PATH 已重装完成${NC}"

# 暂停三秒
sleep 3 