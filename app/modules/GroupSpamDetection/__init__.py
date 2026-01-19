import os


# 模块名称
MODULE_NAME = "GroupSpamDetection"


# 模块是否启用（默认开启）
MODULE_ENABLED = True
# 模块 开关名称
SWITCH_NAME = "GSD"

# 模块描述
MODULE_DESCRIPTION = "群聊刷屏检测"

# 数据目录
DATA_DIR = os.path.join("data", MODULE_NAME)
os.makedirs(DATA_DIR, exist_ok=True)


# 模块的一些命令可以在这里定义，方便在其他地方调用，提高代码的复用率
# ------------------------------------------------------------
# COMMANDS1 = "命令1"
# COMMANDS2 = "命令2"
# COMMANDS3 = "命令3"
# ------------------------------------------------------------
