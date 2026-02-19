import os


# 模块名称
MODULE_NAME = "GPA"


# 模块是否启用（默认开启）
MODULE_ENABLED = True
# 模块开关名称
SWITCH_NAME = "gpa"

# 模块描述
MODULE_DESCRIPTION = "绩点查询模块，支持查询绩点百分位排名"

# 数据目录
DATA_DIR = os.path.join("data", MODULE_NAME)
os.makedirs(DATA_DIR, exist_ok=True)


# 模块的一些命令可以在这里定义，方便在其他地方调用，提高代码的复用率
# 一个主命令，其余子命令都以主命令开头，便于不同模块的命令区分
# ------------------------------------------------------------

BASE_COMMAND = "绩点百分比"  # 主命令

COMMANDS = {
    BASE_COMMAND: "查询绩点百分位排名\n用法：绩点百分比 班级名称 学期 目标绩点\n示例：绩点百分比 22网安 2024-2025-1 3.91\n示例：绩点百分比 24电子信息 all 3.64\n学期格式：xxxx-xxxx-x 或 all（代表全部学期）",
}
# ------------------------------------------------------------
