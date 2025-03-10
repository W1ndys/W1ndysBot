#!/bin/bash

# 遍历所有子模块并切换到 main 分支
git submodule foreach 'git checkout main && git pull origin main'

echo "🔄 正在更新子模块到 main 分支..."
# 强制将所有子模块的引用更新到当前的最新 main 分支
git submodule update --remote --merge

echo "✅ 所有子模块已成功更新到 main 分支。" 