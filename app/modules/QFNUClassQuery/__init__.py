import os


# 模块名称
MODULE_NAME = "QFNUClassQuery"

# 模块开关名称
SWITCH_NAME = "qcq"

# 模块描述
MODULE_DESCRIPTION = (
    "用于对接werobot的api服务，实现QQ群内查询空闲教室和教室课闲忙情况的功能。"
)

# 数据目录
DATA_DIR = os.path.join("data", MODULE_NAME)
os.makedirs(DATA_DIR, exist_ok=True)


# 模块的一些命令可以在这里定义，方便在其他地方调用，提高代码的复用率
# 一个主命令，其余子命令都以主命令开头，便于不同模块的命令区分
# ------------------------------------------------------------

# 空教室命令
EMPTY_CLASSROOM_COMMAND = "查空教室"

# 教室课闲忙命令
CLASS_SCHEDULE_COMMAND = "查教室课"


# 下方作废，不需要这个

BASE_COMMAND = "/base"  # 主命令

COMMANDS = {
    BASE_COMMAND: "主命令，用法：/base",
    # 可以继续添加其他命令
}
# ------------------------------------------------------------
