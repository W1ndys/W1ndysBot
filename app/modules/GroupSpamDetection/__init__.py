import os


# 模块名称
MODULE_NAME = "GroupSpamDetection"

# 开关名称(由模块名称的大写字母的缩写组成)
SWITCH_NAME = "".join([c for c in MODULE_NAME if c.isupper()])

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
