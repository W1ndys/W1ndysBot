@echo off
rem 运行 Docker 容器
docker run -d ^
-e ACCOUNT=3249474653 ^
-e WS_ENABLE=true ^
-p 3001:3001 ^
-p 6099:6099 ^
--name napcat ^
--restart=always ^
mlikiowa/napcat-docker:latest

rem 提示用户容器已启动
echo Docker container 'napcat' started with image 'mlikiowa/napcat-docker:latest'
pause
