# =================================================================
# ||                                                             ||
# ||                  -- 用户配置区 --                           ||
# ||           请在此处修改所有必要的上传参数                    ||
# ||                                                             ||
# =================================================================

# --- 基础配置 ---
# 本地源文件夹路径
$LOCAL_PATH = ".\app\modules"

# 远程服务器配置
$REMOTE_HOST = "my.server"
$REMOTE_PORT = "22"
$REMOTE_USER = "root"

# 远程服务器的目标路径 (末尾不要带斜杠)
# !! 重要: 脚本会先清空此目录，请确保路径正确 !!
$REMOTE_PATH = "/root/bot/app/modules"

# --- 密钥配置 ---
# SSH 私钥文件路径
$PRIVATE_KEY_PATH = "$env:USERPROFILE\.ssh\id_rsa"

# --- 新增：上传后执行的命令 ---
# 将此变量设置为您想在上传和解压成功后在远程服务器上执行的命令
# 例如: "sh /path/to/restart.sh" 或 "docker-compose restart"
# 如果不需要执行任何命令，请将其留空，例如: $POST_UPLOAD_CMD = ""
$POST_UPLOAD_CMD = "supervisorctl restart Bot:Bot_00"

# --- 文件/目录排除配置 ---
# 要在上传时忽略的文件或目录列表
# tar 的 --exclude 模式支持通配符
$EXCLUDE_ITEMS = @(
    "*.log"
    "*.tmp"
    "*.cache"
    ".DS_Store"
    ".git"
    ".gitignore"
    ".vscode"
    "*.pyc"
    "*.pyo"
    "__pycache__"
    "data"
)

# =================================================================
# ||                                                             ||
# ||                  -- 脚本执行区 --                           ||
# ||              通常情况下无需修改以下代码                     ||
# ||                                                             ||
# =================================================================

# 设置控制台输出编码为 UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "[INFO] 同步脚本仓库最新代码..." -ForegroundColor Cyan
git pull

Write-Host ""
Write-Host "[INFO] 开始执行上传任务..." -ForegroundColor Cyan

# --- 1. 验证配置 ---
if (-not (Test-Path -Path $LOCAL_PATH -PathType Container)) {
    Write-Host "[ERROR] 本地路径 `"$LOCAL_PATH`" 不存在。请检查配置。" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path -Path $PRIVATE_KEY_PATH -PathType Leaf)) {
    Write-Host "[ERROR] 密钥文件 `"$PRIVATE_KEY_PATH`" 不存在。请确保路径正确。" -ForegroundColor Red
    exit 1
}

# --- 2. 构建 tar 排除参数 ---
$TAR_EXCLUDE_ARGS = @()
foreach ($item in $EXCLUDE_ITEMS) {
    $TAR_EXCLUDE_ARGS += "--exclude=$item"
}

Write-Host "[INFO] 将忽略以下模式: $($EXCLUDE_ITEMS -join ', ')" -ForegroundColor Yellow

# --- 3. 构建并执行 tar + ssh 命令 ---
# 基础远程命令：创建目录、进入目录、解压
$SSH_REMOTE_CMD = "mkdir -p '$REMOTE_PATH' && cd '$REMOTE_PATH' && tar -xf -"

# 如果定义了后置命令，则追加到远程命令中
if ($POST_UPLOAD_CMD) {
    Write-Host "[INFO] 上传成功后将执行命令: $POST_UPLOAD_CMD" -ForegroundColor Yellow
    $SSH_REMOTE_CMD = "$SSH_REMOTE_CMD && $POST_UPLOAD_CMD"
}

Write-Host "[INFO] 开始通过 tar 和 ssh 流式传输文件..." -ForegroundColor Cyan
Write-Host "[INFO] 连接到 $REMOTE_USER@${REMOTE_HOST}:$REMOTE_PORT" -ForegroundColor Cyan
Write-Host "--------------------------------------------------"

# --- 4. 执行上传 ---
# 保存当前目录
$OriginalLocation = Get-Location

try {
    # 切换到本地目录
    Set-Location -Path $LOCAL_PATH

    # 构建 tar 命令参数
    $tarArgs = $TAR_EXCLUDE_ARGS + @("-cvf", "-", ".")

    # 执行 tar 并通过管道传给 ssh
    # 使用 cmd /c 来处理管道，因为 PowerShell 原生管道对二进制数据处理有问题
    $tarCommand = "tar $($tarArgs -join ' ')"
    $sshCommand = "ssh -p $REMOTE_PORT -i `"$PRIVATE_KEY_PATH`" $REMOTE_USER@$REMOTE_HOST `"$SSH_REMOTE_CMD`""

    $fullCommand = "$tarCommand | $sshCommand"

    # 使用 cmd /c 执行完整命令
    cmd /c $fullCommand
    $EXIT_CODE = $LASTEXITCODE
}
finally {
    # 恢复原始目录
    Set-Location -Path $OriginalLocation
}

# 检查最终的退出码
Write-Host "--------------------------------------------------"
if ($EXIT_CODE -ne 0) {
    Write-Host "[ERROR] 上传或后置命令执行失败。命令退出码: $EXIT_CODE" -ForegroundColor Red
    exit 1
}
else {
    Write-Host "[SUCCESS] 上传和后置命令执行成功完成！" -ForegroundColor Green
}

Write-Host "[INFO] 任务结束。" -ForegroundColor Cyan
exit 0
