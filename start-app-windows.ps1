# 设置控制台输出编码为 UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# 切换到 app 目录并运行 main.py
Set-Location -Path "app"
uv run main.py
