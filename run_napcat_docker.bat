@echo off
rem 运行 Docker Compose
docker compose up -d

rem 提示用户容器已启动
echo Docker containers started using 'docker compose up -d'
pause
