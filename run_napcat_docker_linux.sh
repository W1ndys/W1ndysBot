#!/bin/bash

# 获取当前用户的 UID 和 GID
NAPCAT_UID=$(id -u)
NAPCAT_GID=$(id -g)

# 启动 Docker 容器
docker run -d \
  -e NAPCAT_GID=$NAPCAT_GID \
  -e NAPCAT_UID=$NAPCAT_UID \
  -p 3000:3000 \
  -p 3001:3001 \
  -p 6099:6099 \
  --name napcat \
  --restart=always \
  -v ./napcat/app/.config/QQ:/app/.config/QQ \
  -v ./napcat/app/napcat:/app/napcat \
  -v ./app/napcat/config:/app/napcat/config \
  -v /home/bot/app/scripts/WeatherSubscribe:/home/bot/app/scripts/WeatherSubscribe \
  -v /home/bot/app/scripts/ImageGenerate/output:/home/bot/app/scripts/ImageGenerate/output \
  mlikiowa/napcat-docker:latest

# 提示容器已启动
echo "Napcat Docker container is now running."
