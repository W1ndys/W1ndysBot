import os


# 模块名称
MODULE_NAME = "Template"

# 模块开关名称
SWITCH_NAME = "tp"

# 模块描述
MODULE_DESCRIPTION = "模板模块"

# 数据目录
DATA_DIR = os.path.join("data", MODULE_NAME)
os.makedirs(DATA_DIR, exist_ok=True)


# 模块的一些命令可以在这里定义，方便在其他地方调用，提高代码的复用率
# 一个主命令，其余子命令都以主命令开头，便于不同模块的命令区分
# ------------------------------------------------------------

BASE_COMMAND = "/base"  # 主命令

COMMANDS = {
    BASE_COMMAND: "主命令，用法：/base",
    # 可以继续添加其他命令
}
# ------------------------------------------------------------
