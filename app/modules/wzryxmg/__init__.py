import os


# 模块名称
MODULE_NAME = "wzryxmg"


# 模块是否启用（默认开启）
MODULE_ENABLED = True
# 模块开关名称
SWITCH_NAME = "xmg"

# 模块描述
MODULE_DESCRIPTION = "王者荣耀小马糕收集与高价查询"

# 数据目录
DATA_DIR = os.path.join("data", MODULE_NAME)
os.makedirs(DATA_DIR, exist_ok=True)


# 模块的一些命令可以在这里定义，方便在其他地方调用，提高代码的复用率
# 一个主命令，其余子命令都以主命令开头，便于不同模块的命令区分
# ------------------------------------------------------------

BASE_COMMAND = "小马糕"  # 主命令

COMMANDS = {
    BASE_COMMAND: "显示当前群内最高价格的小马糕",
    f"{BASE_COMMAND}帮助": "显示本模块帮助信息",
}
# ------------------------------------------------------------


# 临时存储结构（模块级变量）
# 用于存储待处理的get_msg请求（主要是删除功能）
# 格式: {echo_str: {"group_id": "", "user_id": "", "message_id": "", "delete_msg_id": "", "timestamp": 0}}
# echo_str 格式: "key={uuid}_gid={group_id}_uid={user_id}_mid={message_id}"
pending_get_msg = {}
