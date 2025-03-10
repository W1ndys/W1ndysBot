#!/bin/bash

BACKUP_NAME="backup_scripts.tar.gz"

# 创建备份，排除 data 和 logs 目录，排除.tar.gz文件
tar -czf "$BACKUP_NAME" --exclude="./data" --exclude="./logs" . --exclude='*.tar.gz'

echo "备份已完成: $BACKUP_NAME" 