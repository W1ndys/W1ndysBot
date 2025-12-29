#!/bin/bash

# =================================================================
# ||                                                             ||
# ||                  -- 用户配置区 --                           ||
# ||           请在此处修改所有必要的上传参数                    ||
# ||                                                             ||
# =================================================================

# --- 基础配置 ---
# 本地源文件夹路径 (例如: /c/MyProject/dist)
LOCAL_PATH="./app/modules"

# 远程服务器 IP 或域名
REMOTE_HOST="192.168.137.75"

# 远程服务器 SSH 用户名
REMOTE_USER="root"

# 远程服务器的目标路径 (末尾不要带斜杠)
# !! 重要: 脚本会先清空此目录，请确保路径正确 !!
REMOTE_PATH="/root/bot/app/modules"

# --- 密钥配置 ---
# 标准 SSH 私钥文件路径 (例如 id_rsa)
PRIVATE_KEY_PATH="/C/Users/W1ndysThinkPad/.ssh/id_ed25519"

# --- 新增：上传后执行的命令 ---
# 将此变量设置为您想在上传和解压成功后在远程服务器上执行的命令
# 例如: "sh /path/to/restart.sh" 或 "docker-compose restart"
# 如果不需要执行任何命令，请将其留空，例如: POST_UPLOAD_CMD=""
POST_UPLOAD_CMD="supervisorctl restart Bot:Bot_00"


# --- 文件/目录排除配置 ---
# 要在上传时忽略的文件或目录列表，用空格分隔
# tar 的 --exclude 模式支持通配符
EXCLUDE_ITEMS=(
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

echo "[INFO] 同步脚本仓库最新代码..."
git pull

echo ""
echo "[INFO] 开始执行上传任务..."

# --- 1. 验证配置 ---
if [ ! -d "$LOCAL_PATH" ]; then
    echo "[ERROR] 本地路径 \"$LOCAL_PATH\" 不存在。请检查配置。"
    exit 1
fi

if [ ! -f "$PRIVATE_KEY_PATH" ]; then
    echo "[ERROR] 密钥文件 \"$PRIVATE_KEY_PATH\" 不存在。请确保路径正确。"
    exit 1
fi

# --- 2. 构建 tar 排除参数 ---
TAR_EXCLUDE_ARGS=""
for item in "${EXCLUDE_ITEMS[@]}"; do
    TAR_EXCLUDE_ARGS+="--exclude=$item "
done

echo "[INFO] 将忽略以下模式: ${EXCLUDE_ITEMS[*]}"

# --- 3. 构建并执行 tar + ssh 命令 ---
# 基础远程命令：创建目录、进入目录、解压
SSH_REMOTE_CMD="mkdir -p '$REMOTE_PATH' && cd '$REMOTE_PATH' && tar -xf -"

# 如果定义了后置命令，则追加到远程命令中
if [ -n "$POST_UPLOAD_CMD" ]; then
    echo "[INFO] 上传成功后将执行命令: $POST_UPLOAD_CMD"
    SSH_REMOTE_CMD="$SSH_REMOTE_CMD && $POST_UPLOAD_CMD"
fi


echo "[INFO] 开始通过 tar 和 ssh 流式传输文件..."
echo "--------------------------------------------------"

# --- 修改部分开始 ---
# 使用更兼容的方式执行命令并捕获退出码，以避免 PIPESTATUS 的问题
# 我们将命令的输出重定向到 /dev/null 以保持终端干净，错误仍然会显示
# set -o pipefail 使得管道中任何一个命令失败，整个管道的退出码就为非零
set -o pipefail
# 在 tar 命令中加入 -v 标志以打印文件名
(cd "$LOCAL_PATH" && tar $TAR_EXCLUDE_ARGS -cvf - . | ssh -i "$PRIVATE_KEY_PATH" "$REMOTE_USER@$REMOTE_HOST" "$SSH_REMOTE_CMD")
EXIT_CODE=$?
set +o pipefail # 恢复默认行为


# 检查最终的退出码
if [ $EXIT_CODE -ne 0 ]; then
    echo "--------------------------------------------------"
    echo "[ERROR] 上传或后置命令执行失败。命令退出码: $EXIT_CODE"
    exit 1
else
    echo "--------------------------------------------------"
    echo "[SUCCESS] 上传和后置命令执行成功完成！"
fi
# --- 修改部分结束 ---

echo "[INFO] 任务结束。"
exit 0