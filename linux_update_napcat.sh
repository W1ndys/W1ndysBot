#!/bin/bash

# 定义容器名称和镜像基础名称
container_name="napcat"
base_image_name="mlikiowa/napcat-docker"

# 获取 GitHub 上的最新 release 版本
repo="NapNeko/NapCatQQ"
latest_version=$(curl -s "https://api.github.com/repos/$repo/releases/latest" | jq -r '.tag_name')

if [ -z "$latest_version" ]; then
  echo "未找到可用的最新版本标签"
  exit 1
fi

# 构建完整的镜像名称
image_name="$base_image_name:$latest_version"

# Step 1: 删除当前定义容器名字的容器
echo "删除容器 $container_name"
docker stop $container_name
docker rm $container_name

# Step 2: 删除原有的镜像
echo "删除镜像 $image_name"
docker rmi $image_name

# Step 3: 拉取最新的镜像
echo "拉取最新的镜像 $image_name"
docker pull $image_name || { echo "镜像拉取失败"; exit 1; }

# Step 4: 使用新镜像运行容器
echo "以新版镜像运行同名容器 $container_name"
docker run -d --name $container_name --restart=always \
  -v ./napcat/app/.config/QQ:/app/.config/QQ \
  -v ./napcat/app/napcat:/app/napcat \
  -v ./app/napcat/config:/app/napcat/config \
  -v /home/bot/app/scripts/:/home/bot/app/scripts/ \
  $image_name || { echo "容器启动失败"; exit 1; }

echo "操作完成！"