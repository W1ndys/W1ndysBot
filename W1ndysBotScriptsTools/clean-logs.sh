#!/bin/bash

# 设置默认值
LOG_DIR="../app/logs"
DAYS_TO_KEEP=1

# 显示使用方法
usage() {
    echo "用法: $0 [-d 日志目录] [-k 保留天数]"
    echo "选项:"
    echo "  -d    指定日志目录 (默认: ./logs)"
    echo "  -k    指定要保留的天数 (默认: 1天)"
    exit 1
}

# 处理命令行参数
while getopts "d:k:h" opt; do
    case $opt in
        d) LOG_DIR="$OPTARG" ;;
        k) DAYS_TO_KEEP="$OPTARG" ;;
        h) usage ;;
        ?) usage ;;
    esac
done

# 检查日志目录是否存在
if [ ! -d "$LOG_DIR" ]; then
    echo "错误: 日志目录 '$LOG_DIR' 不存在"
    exit 1
fi

# 清理旧日志文件
echo "开始清理超过 $DAYS_TO_KEEP 天的日志文件..."
find "$LOG_DIR" -type f -name "*.log" -mtime +$DAYS_TO_KEEP -exec rm -f {} \;
echo "清理完成"

# 显示清理结果
remaining_files=$(find "$LOG_DIR" -type f -name "*.log" | wc -l)
echo "当前日志文件数量: $remaining_files" 