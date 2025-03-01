#!/bin/bash

# 检查 backup.tar.gz 是否存在
if [ -f "backup.tar.gz" ]; then
    # 删除data和logs目录
    rm -rf data logs
    # 解压 backup.tar.gz 并覆盖重复文件
    tar -xzvf backup.tar.gz --overwrite

    # 删除 backup.tar.gz
    rm -f backup.tar.gz
else
    echo "Error: backup.tar.gz 文件不存在"
fi
