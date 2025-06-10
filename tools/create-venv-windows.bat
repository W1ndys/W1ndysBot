@echo off
chcp 65001
cd /d %~dp0
cd ..

:: 检查Python是否安装
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python 未安装，请先安装 Python。
    exit /b
)

:: 创建Python虚拟环境
python -m venv venv

:: 激活Python虚拟环境
call venv\Scripts\activate

:: 升级pip并配置镜像源
python -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

:: 安装requirements.txt中的包
if exist requirements.txt (
    pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
) else (
    echo requirements.txt 文件不存在，请确保该文件存在于当前目录。
)

echo 虚拟环境已创建并安装了所需的pip包。

pause