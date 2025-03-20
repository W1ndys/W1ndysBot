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

# 提示用户输入
read -p "请输入要删除的子模块路径 (例如: app/scripts/LinkGroup): " SUBMODULE_PATH

# 检查输入是否为空
if [ -z "$SUBMODULE_PATH" ]; then
    echo -e "${RED}❌ 错误: 子模块路径不能为空${NC}"
    exit 1
fi

# 检查子模块是否存在
if [ ! -f ".gitmodules" ]; then
    echo -e "${RED}❌ 错误: .gitmodules 文件不存在${NC}"
    exit 1
fi

# 开始清理流程
print_step "开始清理子模块: $SUBMODULE_PATH"

# 1. 从 .git/config 中删除子模块配置
print_step "1. 删除 .git/config 中的子模块配置"
git submodule deinit -f -- "$SUBMODULE_PATH"

# 2. 从工作区和索引中删除子模块
print_step "2. 从工作区和索引中删除子模块"
git rm -f -- "$SUBMODULE_PATH"

# 3. 删除 .git/modules 中的子模块目录
print_step "3. 清理 .git/modules 目录"
rm -rf ".git/modules/$SUBMODULE_PATH"

# 4. 清理可能存在的空目录
print_step "4. 清理空目录"
if [ -d "$SUBMODULE_PATH" ]; then
    rm -rf "$SUBMODULE_PATH"
fi

# 5. 检查清理结果
print_step "检查清理结果"

# 检查 .git/config
if git config -l | grep -F "$SUBMODULE_PATH" > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  警告: 子模块在 .git/config 中仍有残留${NC}"
else
    echo -e "${GREEN}✅ .git/config 已清理完成${NC}"
fi

# 检查 .gitmodules
if grep -F "$SUBMODULE_PATH" .gitmodules > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  警告: 子模块在 .gitmodules 中仍有残留${NC}"
else
    echo -e "${GREEN}✅ .gitmodules 已清理完成${NC}"
fi

# 检查 .git/modules 目录
if [ -d ".git/modules/$SUBMODULE_PATH" ]; then
    echo -e "${YELLOW}⚠️  警告: .git/modules 中仍存在子模块目录${NC}"
else
    echo -e "${GREEN}✅ .git/modules 已清理完成${NC}"
fi

print_step "清理完成"
echo -e "${GREEN}🎉 子模块 $SUBMODULE_PATH 已被删除${NC}" 

# 询问用户是否要自动提交更改
read -p "是否要自动提交这些更改? (y/n): " AUTO_COMMIT

if [[ "$AUTO_COMMIT" =~ ^[Yy]$ ]]; then
    print_step "提交更改"
    
    # 生成提交信息
    COMMIT_MESSAGE="chore(git): 删除子模块 $SUBMODULE_PATH"
    
    # 提交更改
    git add .gitmodules
    git commit -m "$COMMIT_MESSAGE"
    
    echo -e "${GREEN}✅ 更改已提交: $COMMIT_MESSAGE${NC}"
else
    echo -e "${YELLOW}ℹ️ 未提交更改，您可以稍后手动提交${NC}"
fi 