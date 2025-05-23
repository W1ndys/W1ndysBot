#!/bin/bash
dos2unix "$0"
# 设置严格模式
set -euo pipefail

# 日志函数
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# 检查必要的命令
check_requirements() {
    if ! command -v docker &> /dev/null; then
        log "错误: 未安装 Docker"
        exit 1
    fi
}

# 清理已存在的容器
cleanup() {
    if docker ps -a | grep -q "napcat"; then
        log "清理已存在的 napcat 容器..."
        docker rm -f napcat || true
    fi
}

# 获取脚本所在目录的绝对路径
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 主函数
main() {
    check_requirements
    cleanup

    # 设置 NAPCAT_UID 和 NAPCAT_GID
    NAPCAT_UID=1000
    NAPCAT_GID=1000

    log "启动 Napcat Docker 容器..."
    
    # 启动 Docker 容器
    if docker run -d \
        --network bridge \
        -e NAPCAT_GID=$NAPCAT_GID \
        -e NAPCAT_UID=$NAPCAT_UID \
        -e ACCOUNT=3649056059 \
        -p 3000:3000 \
        -p 3001:3001 \
        -p 6099:6099 \
        --name napcat \
        --restart=always \
        -v "${SCRIPT_DIR}/napcat/app/.config/QQ:/app/.config/QQ" \
        -v "${SCRIPT_DIR}/napcat/app/napcat:/app/napcat" \
        mlikiowa/napcat-docker; then
        log "Napcat Docker 容器已成功启动"
    else
        log "错误: 启动 Napcat Docker 容器失败"
        exit 1
    fi
}

# 运行主函数
main