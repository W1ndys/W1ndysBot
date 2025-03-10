#!/bin/bash

# 定义备份文件名
BACKUP_NAME="backup-scripts.tar.gz"

# 检查备份文件是否存在
if [ ! -f "$BACKUP_NAME" ]; then
    echo "错误：备份文件 $BACKUP_NAME 不存在"
    exit 1
fi

# 解压备份文件到当前目录
tar -xzf "$BACKUP_NAME"

# 删除备份文件
rm -f "$BACKUP_NAME"

echo "脚本备份文件 $BACKUP_NAME 已成功解压到当前目录"