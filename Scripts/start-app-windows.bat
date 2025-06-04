@echo off
chcp 65001
cd /d %~dp0
cd ..

:: 检查Python虚拟环境是否存在
IF EXIST venv\Scripts\activate (
    echo Activating virtual environment...
    call venv\Scripts\activate
) ELSE (
    echo Virtual environment not found. Using system Python.
)

:: 进入app目录
cd app

:: 运行主程序
python main.py