@echo off
rem 保存 Docker 镜像为 tar 文件
docker save -o "D:\docker-image\napcat.tar" docker.1panel.dev/mlikiowa/napcat-docker

rem 提示用户保存完成
echo Docker image saved to D:\docker-image\napcat.tar
pause
