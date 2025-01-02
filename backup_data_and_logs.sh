#!/bin/bash

# 进入app目录
cd app || {
    echo "app 目录不存在或无法访问"
    exit 1
}

# 检查data和logs目录是否存在
if [ ! -d "data" ] || [ ! -d "logs" ]; then
    echo "data 或 logs 目录不存在"
    exit 1
fi

# 获取当前日期
current_date=$(date +%Y%m%d)

# 定义压缩文件名
archive_name="backup.tar.gz"

# 打包data和logs目录
tar -czvf $archive_name data logs

# 输出打包结果
if [ $? -eq 0 ]; then
    echo "打包成功: $archive_name"
else
    echo "打包失败"
fi
