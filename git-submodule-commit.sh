#!/bin/bash

# 添加所有更改到暂存区
git add .

# 提交更改，提交信息为"更新子模块"
git commit -m "chore(子模块): 更新子模块"

# 推送到远程仓库的当前分支
git push origin $(git symbolic-ref --short HEAD)

echo "已成功提交并推送更改"