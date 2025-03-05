#!/bin/bash

BACKUP_NAME="backup_scripts.tar.gz"

# 创建备份，排除 data 和 logs 目录
tar -czf "$BACKUP_NAME" --exclude="./data" --exclude="./logs" .

echo "备份已完成: $BACKUP_NAME" 