#!/bin/bash

# 设置颜色变量
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 显示警告信息
echo -e "${RED}⚠️  危险操作警告！⚠️${NC}"
echo -e "${RED}=============================${NC}"
echo -e "${YELLOW}🔄 此脚本将执行以下操作：${NC}"
echo "📝 1. 删除所有的 Git 历史记录"
echo "🌿 2. 删除所有的分支信息"
echo "✨ 3. 创建全新的提交历史"
echo "🚀 4. 强制推送到远程仓库"
echo -e "${RED}⚠️ 此操作不可逆！⚠️${NC}"
echo ""
echo -e "${YELLOW}✅ 执行前请确保：${NC}"
echo "💾 1. 已经备份了所有重要数据"
echo "👥 2. 已通知所有团队成员"
echo "🔑 3. 确认具有仓库管理员权限"
echo ""

# 要求用户确认
read -p "⚠️ 请输入 'YES' 确认继续操作: " confirm
if [ "$confirm" != "YES" ]; then
    echo -e "${YELLOW}❌ 操作已取消${NC}"
    exit 1
fi

# 记录开始时间
start_time=$(date +%s)

echo -e "\n${GREEN}🚀 开始执行仓库重置...${NC}"

echo -e "\n${YELLOW}📁 步骤 1: 创建新的孤立分支${NC}"
git checkout --orphan latest_branch
echo -e "${GREEN}✅ 创建孤立分支完成${NC}"

echo -e "\n${YELLOW}📝 步骤 2: 添加所有文件${NC}"
git add -A
echo -e "${GREEN}✅ 文件添加完成${NC}"

echo -e "\n${YELLOW}💾 步骤 3: 提交更改${NC}"
git commit -m "feat: 重新初始化仓库"
echo -e "${GREEN}✅ 提交完成${NC}"

echo -e "\n${YELLOW}🗑️  步骤 4: 删除主分支${NC}"
git branch -D main 2>/dev/null || echo "主分支不存在，跳过删除"
echo -e "${GREEN}✅ 主分支处理完成${NC}"

echo -e "\n${YELLOW}📝 步骤 5: 将当前分支重命名为主分支${NC}"
git branch -m main
echo -e "${GREEN}✅ 分支重命名完成${NC}"

echo -e "\n${YELLOW}🚀 步骤 6: 强制推送到远程仓库${NC}"
git push -f origin main
echo -e "${GREEN}✅ 推送完成${NC}"

# 计算执行时间
end_time=$(date +%s)
duration=$((end_time - start_time))

echo -e "\n${GREEN}🎉 操作全部完成！${NC}"
echo -e "${YELLOW}⏱️  总执行时间: ${duration} 秒${NC}"
echo -e "\n${YELLOW}📢 注意事项：${NC}"
echo "🔄 1. 所有团队成员需要重新克隆仓库"
echo "⚠️  2. 旧的克隆仓库将无法正常推送，需要重置"
echo "📝 3. 所有历史记录已被永久删除"
echo "🔍 4. 如需查看详细日志，请检查终端输出"
