import os


# 模块名称
MODULE_NAME = "GroupMessageMonitor"

# 模块开关名称
SWITCH_NAME = "GMM"

# 模块描述
MODULE_DESCRIPTION = "群消息监控模块,用于监控敏感消息，常用于引流广告监控"

# 数据目录
DATA_DIR = os.path.join("data", MODULE_NAME)
os.makedirs(DATA_DIR, exist_ok=True)


# 模块的一些命令可以在这里定义，方便在其他地方调用，提高代码的复用率
# ------------------------------------------------------------
# COMMANDS1 = "命令1"
# COMMANDS2 = "命令2"
# COMMANDS3 = "命令3"
# ------------------------------------------------------------
