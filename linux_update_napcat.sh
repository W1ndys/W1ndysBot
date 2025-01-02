#!/bin/bash

# Step 1: 接受用户输入的 docker pull 命令
echo "请输入 docker pull 命令："
read pull_command

# 提取镜像名称和版本
image_name=$(echo $pull_command | awk '{print $2}')
container_name="napcat"

# 执行 docker pull 命令
eval $pull_command || { echo "镜像拉取失败"; exit 1; }

# Step 2: 删除当前定义容器名字的容器
echo "删除容器 $container_name"
docker stop $container_name
docker rm $container_name

# Step 3: 删除原有的镜像
echo "删除镜像 $image_name"
docker rmi $image_name

# Step 4: 使用新镜像运行容器
echo "以新版镜像运行同名容器 $container_name"
docker run -d --name $container_name --restart=always \
  -v ./napcat/app/.config/QQ:/app/.config/QQ \
  -v ./napcat/app/napcat:/app/napcat \
  -v ./app/napcat/config:/app/napcat/config \
  -v /home/bot/app/scripts/WeatherSubscribe:/home/bot/app/scripts/WeatherSubscribe \
  -v /home/bot/app/scripts/ImageGenerate/output:/home/bot/app/scripts/ImageGenerate/output \
  $image_name || { echo "容器启动失败"; exit 1; }

echo "操作完成！"