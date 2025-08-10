@echo off
chcp 65001

:: 检查Python是否安装
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python 未安装，请先安装 Python。
    pause
    exit /b
)

:: 检查uv是否安装
where uv >nul 2>nul
if %errorlevel% neq 0 (
    echo uv 未安装，正在使用 pip 安装 uv...
    python -m pip install uv

    :: 再次检查uv是否安装成功
    where uv >nul 2>nul
    if %errorlevel% neq 0 (
        echo uv 安装失败，请检查 pip 是否正常工作。
        pause
        exit /b
    )
)

:: 使用uv创建Python虚拟环境（如果不存在则创建）
if not exist .venv (
    echo 正在使用 uv 创建虚拟环境...
    uv venv
) else (
    echo 已检测到虚拟环境，跳过创建步骤。
)

:: 激活Python虚拟环境
call .venv\Scripts\activate

:: 使用uv安装requirements.txt中的包，支持重复安装新增库
if exist requirements.txt (
    echo 正在使用 uv 安装/更新依赖包...
    uv pip install -r requirements.txt
) else (
    echo requirements.txt 文件不存在，请确保该文件存在于当前目录。
)

echo 虚拟环境已准备好，并已使用 uv 安装/更新了所需的包。

pause