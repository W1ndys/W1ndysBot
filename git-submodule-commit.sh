#!/bin/bash

# 获取当前日期和时间
current_date=$(date "+%Y-%m-%d %H:%M:%S")

# 自动生成提交信息
commit_message="chore(子模块): 更新子模块引用 - $current_date"

# 获取当前目录
current_dir=$(pwd)

# 检查是否有子模块更新
if [ -n "$(git status --porcelain | grep -E '^\s*M.*\.gitmodules|^\s*M.*子模块路径')" ]; then
    echo "检测到子模块引用更改，准备提交..."
    
    # 添加所有子模块引用更改
    git add .gitmodules
    git submodule foreach git add .
    
    # 提交子模块引用更改
    git commit -m "$commit_message"
    
    # 推送到远程仓库
    git push
    
    echo "子模块引用更改已提交并推送"
else
    echo "没有检测到子模块引用更改"
fi

echo "子模块引用处理完成" 