@echo off
chcp 65001

:: 检查uv虚拟环境是否存在
IF EXIST .venv\Scripts\activate (
    echo Activating uv virtual environment...
    call .venv\Scripts\activate
) ELSE IF EXIST venv\Scripts\activate (
    echo Activating traditional virtual environment...
    call venv\Scripts\activate
) ELSE (
    echo Virtual environment not found. Using system Python.
)

:: 进入app目录
cd app

:: 运行主程序
python main.py