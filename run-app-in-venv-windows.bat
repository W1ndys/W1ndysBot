@echo off
chcp 65001
:: 切换到脚本所在目录
cd /d %~dp0
echo 已切换到脚本所在目录

:: 激活 Python 虚拟环境（假设虚拟环境目录为 venv）
call venv\Scripts\activate
echo 已激活 Python 虚拟环境

:: 进入app目录
cd app
echo 已进入app目录

:: 运行 Python 脚本
python main.py

