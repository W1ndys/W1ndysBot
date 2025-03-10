@echo off
rem 运行 Docker 容器
docker run -d ^
  --name napcat ^
  -e ACCOUNT=3249474653 ^
  -e WS_ENABLE=true ^
  -e NAPCAT_UID=0 ^
  -e NAPCAT_GID=0 ^
  -p 3000:3000 ^
  -p 3001:3001 ^
  -p 6099:6099 ^
  --restart always ^
  -v "%cd%/napcat/app/.config/QQ:/app/.config/QQ" ^
  -v "%cd%/napcat/app/napcat/config:/app/napcat/config" ^
  -v "D:/Github-projects/W1ndys-bot/W1ndys-bot/app/scripts/ImageGenerate/output:/home/bot/app/scripts/ImageGenerate/output" ^
  mlikiowa/napcat-docker:latest

rem 提示用户容器已启动
echo Docker container 'napcat' started
pause