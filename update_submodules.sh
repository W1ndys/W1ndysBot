#!/bin/bash

# 获取当前 Git 仓库路径
repo_path=$(pwd)

# 遍历所有子模块并切换到 main 分支
git submodule foreach '
  echo "Updating submodule $name to track main branch"
  git checkout main
  git pull origin main
'

# 强制将所有子模块的引用更新到当前的最新 main 分支
git submodule update --remote --merge

echo "All submodules are now tracking the main branch."
