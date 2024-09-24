#!/bin/bash

# 检查是否提供了URL参数
if [ -z "$1" ]; then
  read -p "请输入仓库URL: " REPO_URL
else
  REPO_URL=$1
fi

# 提取仓库名称
REPO_NAME=$(basename -s .git "$REPO_URL")

# 生成子模块路径
SUBMODULE_PATH="app/scripts/$REPO_NAME"

# 添加子模块
git submodule add -b main "$REPO_URL" "$SUBMODULE_PATH"

echo "Submodule added at $SUBMODULE_PATH"

# 暂停三秒
sleep 3
