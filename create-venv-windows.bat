@echo off
chcp 65001

:: 检查uv是否安装
where uv >nul 2>nul
if %errorlevel% neq 0 (
    echo uv 未安装，正在安装 uv...
    powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    
    :: 刷新环境变量
    call refreshenv.exe >nul 2>nul || (
        echo 请重新打开命令提示符以使 uv 生效，或手动将 uv 添加到 PATH。
        pause
        exit /b
    )
    
    :: 再次检查uv是否安装成功
    where uv >nul 2>nul
    if %errorlevel% neq 0 (
        echo uv 安装失败，请手动安装 uv 或重新打开命令提示符。
        pause
        exit /b
    )
)

:: 使用uv创建Python虚拟环境
echo 正在使用 uv 创建虚拟环境...
uv venv

:: 激活Python虚拟环境
call venv\Scripts\activate

:: 使用uv安装requirements.txt中的包
if exist requirements.txt (
    echo 正在使用 uv 安装依赖包...
    uv pip install -r requirements.txt
) else (
    echo requirements.txt 文件不存在，请确保该文件存在于当前目录。
)

echo 虚拟环境已创建并使用 uv 安装了所需的包。

pause