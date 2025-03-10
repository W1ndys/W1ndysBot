@echo off

:: 检查 Python 是否已安装
where python >nul 2>nul
if errorlevel 1 (
    echo 未检测到 Python，请先安装 Python。
    exit /b
)

:: 检查 venv 环境是否存在
if not exist "venv\Scripts\activate.bat" (
    echo Python 虚拟环境 "venv" 不存在，请先创建环境。
    echo 可以使用命令：python -m venv venv
    exit /b
)

:: 打开一个新的命令提示符窗口并激活 venv 环境
start cmd /k "venv\Scripts\activate.bat"

echo 已打开一个新的命令提示符窗口并进入 Python 虚拟环境。 