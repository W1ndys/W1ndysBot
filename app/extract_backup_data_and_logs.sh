#!/bin/bash

# 定义备份文件名
BACKUP_NAME="backup_data_and_logs.tar.gz"
# 定义解压目标目录
EXTRACT_DIR="."

# 检查备份文件是否存在
if [ ! -f "$BACKUP_NAME" ]; then
    echo "错误：备份文件 $BACKUP_NAME 不存在"
    exit 1
fi

# 创建解压目标目录（如果不存在）
mkdir -p "$EXTRACT_DIR"

# 解压备份文件到目标目录
tar -xzf "$BACKUP_NAME" -C "$EXTRACT_DIR"

echo "备份文件 $BACKUP_NAME 已成功解压到 $EXTRACT_DIR 目录"
