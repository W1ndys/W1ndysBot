#!/bin/bash

# 获取当前时间的函数
log() {
  echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Step 1: 输入容器名字
log "请输入容器名字（默认: napcat）："
read container_name
if [ -z "$container_name" ]; then
  container_name="napcat"
fi

# 镜像名固定
image_name="mlikiowa/napcat-docker:latest"

# Step 2: 删除旧容器（如果存在）
log "删除容器 $container_name（如存在）"
docker stop "$container_name" 2>/dev/null
docker rm "$container_name" 2>/dev/null

# Step 3: 设置 UID 和 GID
NAPCAT_UID=1000
NAPCAT_GID=1000

# Step 4: 启动新容器
log "使用镜像 $image_name 启动容器 $container_name"
docker run -d --name "$container_name" --restart=always \
  --network host \
  --mac-address="02:42:ac:11:00:02" \
  --hostname="napcat-host" \
  -e NAPCAT_UID=$NAPCAT_UID \
  -e NAPCAT_GID=$NAPCAT_GID \
  -v ./napcat/app/.config/QQ:/app/.config/QQ \
  -v ./napcat/app/napcat/config:/app/napcat/config \
  "$image_name" || { log "容器启动失败"; exit 1; }

log "操作完成！"
