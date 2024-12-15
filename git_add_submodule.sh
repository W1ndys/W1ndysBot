#!/bin/bash

# 检查是否提供了URL参数
if [ -z "$1" ]; then
  read -p "请输入仓库URL: " REPO_URL
else
  REPO_URL=$1
fi

# 提取仓库名称
# 同时支持HTTPS和SSH格式
if [[ $REPO_URL == git@* ]]; then
    # SSH格式 (git@github.com:username/repo.git)
    REPO_NAME=$(echo "$REPO_URL" | sed 's/.*:\(.*\)\.git/\1/' | awk -F'/' '{print $NF}')
else
    # HTTPS格式
    REPO_NAME=$(basename -s .git "$REPO_URL")
fi

# 生成子模块路径
SUBMODULE_PATH="app/scripts/$REPO_NAME"

# 添加子模块
git submodule add -b main "$REPO_URL" "$SUBMODULE_PATH"

# 更新子模块
git submodule update --remote --merge

# 输出结果
echo "子模块已添加到 $SUBMODULE_PATH"

# 暂停三秒
sleep 3