#!/bin/bash


# 删除已有的容器
docker rm -f bot

# 运行容器
docker run -d -v $(pwd)/app:/app --name bot -p 3001:3001 bot
