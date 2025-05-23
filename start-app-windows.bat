@echo off
chcp 65001

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

:: 如果程序意外退出，暂停以便查看错误信息
pause 
