#!/bin/bash

# 提示用户输入子模块仓库URL
read -p "请输入子模块仓库URL: " SUBMODULE_URL

# 提示用户输入子模块路径
read -p "请输入子模块路径: " SUBMODULE_PATH

# 添加子模块
git submodule add $SUBMODULE_URL $SUBMODULE_PATH

# 初始化并更新子模块
git submodule update --init --recursive

# 提交更改
git add .gitmodules $SUBMODULE_PATH
git commit -m "添加子模块 $SUBMODULE_PATH"
git push origin master

echo "子模块 $SUBMODULE_PATH 已成功添加并推送。"