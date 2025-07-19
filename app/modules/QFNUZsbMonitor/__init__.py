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
# ------------------------------------------------------------

EXAMPLE_COMMAND = "示例命令"  # 示例命令

COMMANDS = {
    EXAMPLE_COMMAND: "示例命令，用法：示例命令",
    # 可以继续添加其他命令
}
# ------------------------------------------------------------
