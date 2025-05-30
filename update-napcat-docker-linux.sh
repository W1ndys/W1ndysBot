#!/bin/bash

# 获取当前时间的函数
log() {
  echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Step 1: 接受用户输入的 docker pull 命令
log "请输入 docker pull 命令（默认: docker pull mlikiowa/napcat-docker:latest）："
read pull_command

# 如果用户没有输入，使用默认值
if [ -z "$pull_command" ]; then
  pull_command="docker pull mlikiowa/napcat-docker:latest"
fi

# 提取镜像名称和版本
image_name=$(echo $pull_command | awk '{print $3}')

# 打印提取到的镜像名称和版本
log "提取到的镜像名称和版本: $image_name"

# Step 2: 接受用户输入的容器名字
log "请输入容器名字（默认: napcat）："
read container_name

# 如果用户没有输入，使用默认值
if [ -z "$container_name" ]; then
  container_name="napcat"
fi

# 删除当前定义容器名字的容器
log "删除容器 $container_name"
docker stop $container_name
docker rm $container_name

# 设置 NAPCAT_UID 和 NAPCAT_GID
NAPCAT_UID=1000
NAPCAT_GID=1000

# Step 3: 使用新镜像运行容器
log "以新版镜像运行同名容器 $container_name"
docker run -d --name $container_name --restart=always \
  --network host \
  --mac-address="02:42:ac:11:00:02" \
  --hostname="napcat-host" \
  -e NAPCAT_UID=$NAPCAT_UID \
  -e NAPCAT_GID=$NAPCAT_GID \
  -e ACCOUNT=3649056059 \
  -v ./napcat/app/.config/QQ:/app/.config/QQ \
  -v ./napcat/app/napcat/config:/app/napcat/config \
  $image_name || { log "容器启动失败"; exit 1; }
log "操作完成！"