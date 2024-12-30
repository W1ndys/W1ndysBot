#!/bin/bash

# 构建 Docker 镜像
docker build -t bot .

# 运行 Docker 容器，并映射主机的 3001 端口到容器的 3001 端口
docker run -d -v $(pwd)/app:/app --name bot -p 3001:3001 bot
