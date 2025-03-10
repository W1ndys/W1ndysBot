#!/bin/bash

# 检查当前目录是否为 Git 仓库
if [ ! -d ".git" ]; then
    echo "当前目录不是一个 Git 仓库。"
    exit 1
fi

# 拉取主仓库的最新更改
git pull

# 更新子模块
git submodule update --init --recursive

echo "项目及其子模块已成功更新。"
read -p "按回车键继续..." 