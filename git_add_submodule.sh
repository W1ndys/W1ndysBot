#!/bin/bash

# 检查是否提供了URL参数
if [ -z "$1" ]; then
    read -p "请输入仓库URL: " REPO_URL
else
    REPO_URL="$1"
fi

# 转换各种格式到SSH格式
HTTPS_PREFIX="https://github.com/"
SSH_PREFIX="git@github.com:"

if [[ $REPO_URL == ${HTTPS_PREFIX}* ]]; then
    REPO_URL="${REPO_URL/$HTTPS_PREFIX/$SSH_PREFIX}"
    if [[ $REPO_URL != *.git ]]; then
        REPO_URL="${REPO_URL}.git"
    fi
elif [[ $REPO_URL != git@* ]]; then
    if [[ $REPO_URL != *.git ]]; then
        REPO_URL="${SSH_PREFIX}${REPO_URL}.git"
    fi
fi

# 提取仓库名称
REPO_NAME=$(basename "${REPO_URL}" .git)

# 生成子模块路径
SUBMODULE_PATH="app/scripts/${REPO_NAME}"

# 添加子模块
git submodule add -b main "${REPO_URL}" "${SUBMODULE_PATH}"

# 输出结果
echo "子模块已添加到 ${SUBMODULE_PATH}"
# 暂停三秒
sleep 3
