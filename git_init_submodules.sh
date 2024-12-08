#!/bin/bash

echo "开始初始化所有子模块..."

# 初始化并更新所有子模块（包括嵌套的子模块）
git submodule update --init --recursive

echo "正在更新所有子模块到最新版本..."
# 更新所有子模块到最新版本
git submodule update --remote --merge

echo "所有子模块初始化和更新完成！"

# 暂停两秒
sleep 2 