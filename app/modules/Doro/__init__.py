import os


# 模块名称
MODULE_NAME = "Doro"

# 模块开关名称
SWITCH_NAME = "doro"

# 模块描述
MODULE_DESCRIPTION = "随机返回一个Doro表情包"

# 数据目录
DATA_DIR = os.path.join("data", MODULE_NAME)
os.makedirs(DATA_DIR, exist_ok=True)


# 模块的一些命令可以在这里定义，方便在其他地方调用，提高代码的复用率
# ------------------------------------------------------------
DORO_COMMANDS = "来个doro"
# ------------------------------------------------------------
